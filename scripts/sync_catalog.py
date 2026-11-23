#!/usr/bin/env python3
"""Incrementally sync public HumanCOIN metadata and atomically publish a validated static snapshot."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import random
import re
import sys
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen

import yaml

try:
    from .catalog_store import publish, read_records, encoded, valid_number, camera_resolution, scene_fields
except ImportError:
    from catalog_store import publish, read_records, encoded, valid_number, camera_resolution, scene_fields

HF = 'https://huggingface.co'
MS = 'https://www.modelscope.cn'
METADATA_FORMAT = 'portal.yaml+sensor-streams'
L3_METADATA_FORMAT = 'portal.yaml+sensor-streams+total-episodes'
ROOT = Path(__file__).resolve().parents[1]
_NETWORK_LOCK = threading.Lock()
_THROTTLE_UNTIL = 0.0
_NETWORK_CONDITION = threading.Condition()
_NETWORK_LIMIT = 4
_NETWORK_ACTIVE = 0

def retry_delay(value, attempt):
    try:
        return max(0.0, min(120, float(value)))
    except (ValueError, TypeError):
        try:
            return max(0.0, min(120, parsedate_to_datetime(value).timestamp() - time.time()))
        except (ValueError, TypeError, AttributeError):
            return min(30, 2 ** attempt) + random.random()

def metadata_request(url):
    request = Request(url, headers={'User-Agent': 'HumanCOIN-DataManager/3.0'})
    parsed = urlparse(url)
    if parsed.scheme != 'https':
        return request
    # Credentials are scoped to the original request, including on CDN redirects.
    if parsed.hostname == 'huggingface.co':
        token = os.environ.get('HF_TOKEN') or os.environ.get('HF_ACCESS_TOKEN')
        if token:
            request.add_unredirected_header('Authorization', 'Bearer ' + token)
    elif parsed.hostname == 'www.modelscope.cn' and re.fullmatch(r'/api/v1/datasets/HumanCOIN/[^/]+/repo', parsed.path):
        token = os.environ.get('MODELSCOPE_TOKEN') or os.environ.get('MODELSCOPE_API_TOKEN')
        if token:
            # The legacy dataset file endpoint authenticates with the SDK session cookie.
            request.add_unredirected_header('Cookie', 'm_session_id=' + token)
    return request

def fetch(url, *, load=json.load):
    global _THROTTLE_UNTIL, _NETWORK_LIMIT, _NETWORK_ACTIVE
    for attempt in range(4):
        try:
            delay = _THROTTLE_UNTIL - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            with _NETWORK_CONDITION:
                _NETWORK_CONDITION.wait_for(lambda: _NETWORK_ACTIVE < _NETWORK_LIMIT)
                _NETWORK_ACTIVE += 1
            try:
                with urlopen(metadata_request(url), timeout=30) as response:
                    return load(response), response.headers.get('Link', '')
            finally:
                with _NETWORK_CONDITION:
                    _NETWORK_ACTIVE -= 1
                    _NETWORK_CONDITION.notify_all()
        except (HTTPError, URLError, TimeoutError) as exc:
            retryable = not isinstance(exc, HTTPError) or exc.code in (408, 429, 500, 502, 503, 504)
            if not retryable or attempt == 3:
                raise
            delay = retry_delay((exc.headers or {}).get('Retry-After') if isinstance(exc, HTTPError) else None, attempt)
            if isinstance(exc, HTTPError) and exc.code == 429:
                with _NETWORK_CONDITION:
                    _NETWORK_LIMIT = max(1, _NETWORK_LIMIT // 2)
                with _NETWORK_LOCK:
                    _THROTTLE_UNTIL = max(_THROTTLE_UNTIL, time.monotonic() + delay)
            time.sleep(delay)

def hf_catalog():
    url = HF + '/api/datasets?author=HumanCOIN&limit=100&full=true'
    result, seen = [], set()
    while url:
        if url in seen:
            raise ValueError('Repeated Hugging Face pagination URL')
        seen.add(url)
        data, link = fetch(url)
        if not isinstance(data, list):
            raise ValueError('Unexpected Hugging Face catalog response')
        result.extend(data)
        match = re.search(r'<([^>]+)>; rel="next"', link)
        url = match[1] if match else None
        if url and not url.startswith(HF + '/api/datasets?'):
            raise ValueError('Unexpected pagination URL')
    ids = [row['id'] for row in result]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate records across Hugging Face pages; retry a stable scan')
    return result

class ModelScopeInventoryChanged(ValueError):
    pass


def ms_catalog():
    for attempt in range(3):
        try:
            return ms_catalog_scan()
        except ModelScopeInventoryChanged as exc:
            if attempt == 2:
                raise
            print(f'{exc}; restarting ModelScope inventory from page 1', file=sys.stderr)
            time.sleep(retry_delay(None, attempt))


def ms_catalog_scan():
    result, page, expected, seen = [], 1, None, set()
    while True:
        data, _ = fetch(MS + '/api/v1/datasets?' + urlencode({'Owner': 'HumanCOIN', 'PageNumber': page, 'PageSize': 100}))
        if data.get('Code') != 200 or not isinstance(data.get('Data'), list):
            raise ValueError('Unexpected ModelScope catalog response')
        if expected is None:
            expected = data['TotalCount']
        if data['TotalCount'] != expected:
            raise ModelScopeInventoryChanged(
                f'ModelScope inventory changed during pagination (page {page}: '
                f'expected {expected} repositories, received total {data["TotalCount"]})')
        for row in data['Data']:
            key = (row.get('Namespace'), row['Name'])
            if key in seen:
                raise ValueError('Repeated ModelScope page')
            seen.add(key)
        result.extend(data['Data'])
        if len(result) == expected:
            return result
        if not data['Data'] or len(result) > expected:
            raise ValueError('Incomplete ModelScope inventory')
        page += 1

def ms_file(repo, path):
    return f'{MS}/api/v1/datasets/{repo}/repo?' + urlencode({'Revision': 'master', 'FilePath': path})

def normalize(repo, hf, ms, metadata):
    tags = hf.get('tags', []) + (ms.get('UserDefineTags') or '').split(',')
    named_level = re.match(r'(l[123])(?:_|-)', repo.split('/')[-1], re.I)
    explicit = metadata.get('level') or next((tag.upper() for tag in tags if tag.upper() in ('L1', 'L2', 'L3')), None)
    level = explicit if explicit in ('L1', 'L2', 'L3') else named_level[1].upper() if named_level else 'Unknown'
    scene, scene_category = scene_fields(metadata.get('scene'))
    revision = hf.get('sha') or 'main'
    primary = metadata.get('primary_camera')
    resolution = metadata.get('resolution')
    resolution_source = 'metadata'
    if not resolution:
        resolution, _, resolution_source = camera_resolution(repo)
    videos = []
    preview = metadata.get('preview_video')
    if preview and (hf or ms):
        url = (f'{HF}/datasets/{repo}/resolve/{revision}/{quote(preview, safe="/")}'
               if hf else ms_file(repo, preview))
        videos.append({'key': primary or 'preview', 'url': url})
    return {
        'id': repo, 'repo': repo, 'name': repo.split('/')[-1].replace('_', ' '),
        'level': level, 'scene': scene, 'sceneCategory': scene_category,
        'task': metadata.get('task_name') or '', 'description': metadata.get('example_task_description') or '',
        'mods': metadata.get('modalities') or [], 'resolution': resolution, 'primaryCamera': primary,
        'resolutionSource': resolution_source,
        'episodes': metadata.get('total_episodes' if level == 'L3' else 'num_recordings'),
        'durationSeconds': metadata.get('duration_s'), 'sizeBytes': metadata.get('size_bytes'),
        'downloads': hf.get('downloads'),
        'updated': hf.get('lastModified') or (datetime.fromtimestamp(ms['GmtModified'], timezone.utc).isoformat() if ms.get('GmtModified') else ''),
        'public': not hf.get('private', False), 'gated': hf.get('gated', False),
        'license': metadata.get('license') or next((t.split(':', 1)[1] for t in tags if t.startswith('license:')), ms.get('License')),
        'hubs': {**({'huggingface': {'repo': repo, 'revision': revision, 'url': f'{HF}/datasets/{repo}'}} if hf else {}),
                 **({'modelscope': {'repo': repo, 'revision': 'master', 'url': f'{MS}/datasets/{repo}'}} if ms else {})},
        'videos': videos, 'streams': [
            {'key': item['feature_key'], 'dtype': item.get('dtype'), 'shape': item['shape'],
             'rate': item.get('sample_rate_hz')}
            for item in metadata.get('sensor_streams', [])
        ],
        'levelConflict': bool(explicit in ('L1', 'L2', 'L3') and named_level and explicit != named_level[1].upper()),
        'derivedMetrics': [],
        'metadataSources': [portal_url(repo, 'huggingface' if hf else 'modelscope', revision)] if hf or ms else [],
    }


def portal_url(repo, hub, revision):
    if hub == 'huggingface':
        return f'{HF}/datasets/{repo}/raw/{revision}/portal.yaml'
    return ms_file(repo, 'portal.yaml')

def recording_streams(info):
    features = info.get('features') if isinstance(info, dict) else None
    if not isinstance(features, dict):
        raise ValueError('Expected recording features')
    streams = []
    bookkeeping = {'timestamp', 'frame_index', 'episode_index', 'index', 'task_index'}
    for key, feature in features.items():
        if key in bookkeeping or not isinstance(feature, dict):
            continue
        dtype, shape = feature.get('dtype'), feature.get('shape')
        if not isinstance(dtype, str) or not isinstance(shape, list) or not all(type(n) is int and n >= 0 for n in shape):
            continue
        rate = feature.get('fps')
        details = feature.get('info')
        if not valid_number(rate) and isinstance(details, dict):
            rate = details.get('video.fps')
        streams.append({'key': key, 'dtype': dtype, 'shape': shape,
                        'rate': rate if valid_number(rate) and rate > 0 else None})
    return streams


def validate_portal(metadata, repo):
    if not isinstance(metadata, dict) or type(metadata.get('schema_version')) is not int or metadata['schema_version'] != 1:
        raise ValueError('Expected portal.yaml schema_version 1')
    if metadata.get('repo_id') not in (None, repo):
        raise ValueError('repo_id does not match the repository')
    for field in ('level', 'task_name', 'example_task_description', 'primary_camera', 'license'):
        value = metadata.get(field)
        if value is not None and not isinstance(value, str):
            raise ValueError(f'Invalid {field}')
    for field in ('num_recordings', 'total_episodes', 'duration_s', 'size_bytes'):
        value = metadata.get(field)
        if value is not None and not valid_number(value, integer=field != 'duration_s'):
            raise ValueError(f'Invalid {field}')
    scene = metadata.get('scene')
    if scene is not None and not (isinstance(scene, str) or isinstance(scene, dict) and
                                   all(scene.get(k) is None or isinstance(scene[k], str) for k in ('area', 'name', 'category'))):
        raise ValueError('Invalid scene')
    modalities = metadata.get('modalities')
    if modalities is not None and not (isinstance(modalities, list) and all(isinstance(value, str) for value in modalities)):
        raise ValueError('Invalid modalities')
    streams = metadata.get('sensor_streams', [])
    if not isinstance(streams, list):
        raise ValueError('Expected a sensor_streams list')
    keys = set()
    for item in streams:
        key = item.get('feature_key') if isinstance(item, dict) else None
        if not isinstance(key, str) or not key.strip() or key in keys:
            raise ValueError('Expected a unique sensor_streams feature_key')
        keys.add(key)
        shape, rate, dtype = item.get('shape'), item.get('sample_rate_hz'), item.get('dtype')
        if not isinstance(shape, list) or not all(type(n) is int and n >= 0 for n in shape):
            raise ValueError(f'Invalid sensor stream shape for {key}')
        if rate is not None and (not valid_number(rate) or rate <= 0):
            raise ValueError(f'Invalid sample_rate_hz for {key}')
        if dtype is not None and not isinstance(dtype, str):
            raise ValueError(f'Invalid dtype for {key}')
    resolution = metadata.get('resolution')
    if resolution is not None and not (isinstance(resolution, str) and re.fullmatch(r'[1-9]\d*x[1-9]\d*', resolution)):
        raise ValueError('Invalid resolution')
    preview = metadata.get('preview_video')
    if preview is not None and (not isinstance(preview, str) or not preview or
                                PurePosixPath(preview).is_absolute() or any(part in ('', '.', '..') for part in preview.split('/')) or
                                any(char in preview for char in '\\:?#') or not preview.lower().endswith('.mp4')):
        raise ValueError('Expected a repository-relative MP4 preview_video')
    return metadata



def source_record(repo, hub, listing, cache_root, now, warnings, force=False):
    cache_path = cache_root / (hashlib.sha256((hub + '/' + repo).encode()).hexdigest() + '.json')
    try:
        cached = json.loads(cache_path.read_text()) if cache_path.exists() else None
        if cached and not all(key in cached for key in ('fingerprint', 'checkedAt', 'record')):
            cached = None
        if cached and cached.get('metadataFormat') not in ('portal.yaml', 'portal.yaml+recording-info', METADATA_FORMAT, L3_METADATA_FORMAT):
            cached = None
    except (ValueError, OSError):
        cached = None
    fingerprint = listing.get('sha') if hub == 'huggingface' else str(listing.get('GmtModified') or '')
    cache_format = L3_METADATA_FORMAT if cached and cached['record'].get('level') == 'L3' else METADATA_FORMAT
    if cached and cached['metadataFormat'] == cache_format and not force and cached['fingerprint'] == fingerprint:
        # Commit-addressed HF data can be reused indefinitely. Branch-based sources are rechecked daily.
        age = (now - datetime.fromisoformat(cached['checkedAt'])).total_seconds()
        if (hub == 'huggingface' and fingerprint and not cached.get('streamReadFailed') and not cached.get('episodeReadFailed')) or age < 86400:
            return cached['record'], 'ok', cached['checkedAt']
    revision = (listing.get('sha') or 'main') if hub == 'huggingface' else 'master'
    try:
        metadata = validate_portal(fetch(portal_url(repo, hub, revision), load=yaml.safe_load)[0], repo)
    except (HTTPError, URLError, TimeoutError, ValueError, yaml.YAMLError) as exc:
        warnings.append(f'{hub}/{repo}/portal.yaml: {exc}')
        if cached:
            record = cached['record']
            if record.get('level') == 'L3' and cached['metadataFormat'] != L3_METADATA_FORMAT:
                record = {**record, 'episodes': None}
            return record, 'stale', cached['checkedAt']
        metadata = None
    record = normalize(repo, listing if hub == 'huggingface' else {}, listing if hub == 'modelscope' else {}, metadata or {})
    record['metadataFingerprint'] = fingerprint
    record['metadataRevision'] = revision
    if metadata is not None:
        episode_read_failed = False
        if record['level'] == 'L3' and record['episodes'] is None:
            path = 'meta/info.json'
            url = f'{HF}/datasets/{repo}/raw/{revision}/{path}' if hub == 'huggingface' else ms_file(repo, path)
            try:
                info = fetch(url)[0]
                total = info.get('total_episodes') if isinstance(info, dict) else None
                if not valid_number(total, integer=True):
                    raise ValueError('Invalid or missing total_episodes')
                record['episodes'] = total
                record['metadataSources'].append(url)
            except (URLError, TimeoutError, ValueError) as exc:
                episode_read_failed = True
                warnings.append(f'{hub}/{repo}/meta/info.json: {exc}')
                if cached and cached['metadataFormat'] == L3_METADATA_FORMAT and cached['fingerprint'] == fingerprint:
                    record['episodes'] = cached['record'].get('episodes')
        example = metadata.get('example_recording')
        stream_read_failed = False
        if 'sensor_streams' not in metadata and isinstance(example, str) and re.fullmatch(r'[a-zA-Z0-9_-][a-zA-Z0-9_. -]*', example):
            path = f'{quote(example)}/meta/info.json' if hub == 'huggingface' else f'{example}/meta/info.json'
            url = f'{HF}/datasets/{repo}/raw/{revision}/{path}' if hub == 'huggingface' else ms_file(repo, path)
            try:
                record['streams'] = recording_streams(fetch(url)[0])
                record['metadataSources'].append(url)
            except (URLError, TimeoutError, ValueError) as exc:
                stream_read_failed = True
                warnings.append(f'{hub}/{repo}/example_recording/meta/info.json: {exc}')
                if cached and cached['fingerprint'] == fingerprint:
                    record['streams'] = cached['record'].get('streams', [])
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        temp = cache_path.with_suffix('.tmp')
        metadata_format = L3_METADATA_FORMAT if record['level'] == 'L3' else METADATA_FORMAT
        temp.write_bytes(encoded({'metadataFormat': metadata_format, 'fingerprint': fingerprint,
                                  'checkedAt': now.isoformat(), 'streamReadFailed': stream_read_failed,
                                  'episodeReadFailed': episode_read_failed,
                                  'record': record}))
        temp.replace(cache_path)
    return record, 'missing' if metadata is None else 'ok', now.isoformat()

def synchronize(output, state_root, *, workers=4, force=False, now=None, preview_limit=None):
    global _NETWORK_LIMIT
    _NETWORK_LIMIT = workers
    now = now or datetime.now(timezone.utc)
    warnings, inventories, sources = [], {}, {}
    # Do not mutate removal state or publish anything until both inventories are complete.
    for hub, loader in [('huggingface', hf_catalog), ('modelscope', ms_catalog)]:
        inventories[hub] = loader()
        sources[hub] = {'status': 'ok', 'count': len(inventories[hub]), 'checkedAt': now.isoformat()}
    hf = {d['id']: d for d in inventories['huggingface'] if d.get('author') == 'HumanCOIN' and not d.get('private') and not d.get('disabled')}
    ms = {f"{d['Namespace']}/{d['Name']}": d for d in inventories['modelscope'] if d.get('Namespace') == 'HumanCOIN'}
    sources['huggingface']['count'] = len(hf)
    sources['modelscope']['count'] = len(ms)
    state_root = Path(state_root)
    state_file = state_root / 'inventory.json'
    old_state = json.loads(state_file.read_text()) if state_file.exists() else {'missing': {}}
    previous = {d['id']: d for d in read_records(Path(output).parent)} if Path(output).exists() else {}
    missing = {}
    def build(repo):
        records, statuses, checks = {}, {}, {}
        for hub, listing in [('huggingface', hf.get(repo)), ('modelscope', ms.get(repo))]:
            if listing is not None:
                if hub == 'modelscope' and statuses.get('huggingface') == 'ok':
                    statuses[hub] = 'mirrored'
                else:
                    records[hub], statuses[hub], checks[hub] = source_record(repo, hub, listing, state_root / 'sources', now, warnings, force)
            elif hub in previous.get(repo, {}).get('hubs', {}):
                key = hub + '/' + repo
                scans = old_state.get('missing', {}).get(key, 0) + 1
                missing[key] = scans
                if scans < 2:
                    statuses[hub] = 'removal_candidate'
        available = sorted(records, key=lambda hub: (statuses[hub] != 'ok', hub != 'huggingface'))
        if not available:
            if not statuses:
                return None
            d = dict(previous[repo])
            d['staleMetrics'] = ['episodes', 'durationSeconds', 'sizeBytes', 'downloads']
        else:
            canonical = available[0]
            d = dict(records[canonical])
            d['metadataSource'] = canonical
            d['sourceChecks'] = checks
            if statuses[canonical] != 'ok':
                d['staleMetrics'] = ['episodes', 'durationSeconds', 'sizeBytes'] if statuses[canonical] == 'stale' else []
        if d.get('levelConflict'):
            warnings.append(repo + ': explicit tier conflicts with repository name; explicit tier retained')
        d['sourceStatus'] = statuses
        hubs = {}
        for hub in statuses:
            old = previous.get(repo, {}).get('hubs', {}).get(hub, {})
            revision = hf[repo].get('sha') or 'main' if hub == 'huggingface' and repo in hf else 'master' if hub == 'modelscope' and repo in ms else old.get('revision', 'main')
            hubs[hub] = {'repo': repo, 'revision': revision, 'url': f'{HF}/datasets/{repo}' if hub == 'huggingface' else f'{MS}/datasets/{repo}', 'mutableRevision': revision in ('main', 'master')}
        d['hubs'] = hubs
        d['downloads'] = hf[repo].get('downloads') if repo in hf else d.get('downloads') if statuses.get('huggingface') == 'removal_candidate' else None
        d['updated'] = hf[repo].get('lastModified', '') if repo in hf else datetime.fromtimestamp(ms[repo]['GmtModified'], timezone.utc).isoformat() if repo in ms and ms[repo].get('GmtModified') else d.get('updated', '')
        if any(status == 'removal_candidate' for status in statuses.values()):
            warnings.append(repo + ': source missing from first complete inventory; pending confirmation')
            d['staleMetrics'] = list(set(d.get('staleMetrics', []) + ['downloads']))
        return d
    with ThreadPoolExecutor(max_workers=workers) as pool:
        datasets = [d for d in pool.map(build, sorted(hf.keys() | ms.keys() | previous.keys())) if d is not None]
    try:
        from .preview_assets import attach_previews
    except ImportError:
        from preview_assets import attach_previews
    def cover_sources(dataset):
        repo = dataset['id']
        if repo in hf:
            revision = hf[repo].get('sha') or 'main'
            yield f'{HF}/datasets/{repo}/resolve/{revision}/preview.jpg', revision if revision != 'main' else hf[repo].get('lastModified') or now.date().isoformat()
        if repo in ms:
            yield ms_file(repo, 'preview.jpg'), ms[repo].get('GmtModified') or now.date().isoformat()

    attach_previews(datasets, Path(output).parent, state_root, warnings,
                    sources_for=cover_sources, fetch=fetch, max_new=preview_limit)
    result = publish(output, datasets, generated_at=now.isoformat(), sources=sources, warnings=warnings)
    state_root.mkdir(parents=True, exist_ok=True)
    temp = state_file.with_suffix('.tmp')
    temp.write_bytes(encoded({'missing': missing, 'checkedAt': now.isoformat()}))
    temp.replace(state_file)
    return result

def write_catalog(output, datasets, **kwargs):
    return publish(output, datasets, **kwargs)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/data/catalog.json')
    parser.add_argument('--state-dir', type=Path, default=ROOT / 'sync-state')
    parser.add_argument('--workers', type=int, choices=range(1, 9), default=4)
    parser.add_argument('--preview-limit', type=int, help='Maximum new cover image requests per sync; cached covers are reused')
    parser.add_argument('--force', action='store_true', help='Re-read unchanged source metadata')
    parser.add_argument('--validate', action='store_true', help='Validate the published snapshot without network access')
    args = parser.parse_args()
    if args.preview_limit is not None and args.preview_limit < 0:
        parser.error('--preview-limit must be nonnegative')
    try:
        if args.validate:
            try:
                from .catalog_store import validate
            except ImportError:
                from catalog_store import validate
            result = validate(args.output.parent)
        else:
            result = synchronize(args.output, args.state_dir, workers=args.workers, force=args.force, preview_limit=args.preview_limit)
        print(f"Snapshot {result['snapshotId'][:12]}: {result['stats']['datasets']} datasets")
        return 0
    except Exception as exc:
        print(f'Catalog unchanged: {exc}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
