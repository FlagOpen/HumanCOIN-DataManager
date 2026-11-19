"""Cache dataset-provided JPEG covers for the static portal."""
import hashlib
import json
from pathlib import Path
from urllib.error import URLError

try:
    from .catalog_store import encoded
except ImportError:
    from catalog_store import encoded

MAX_POSTER_BYTES = 2 * 1024 * 1024


def asset(root, data, extension):
    sha = hashlib.sha256(data).hexdigest()
    path = f'media/{sha}.{extension}'
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest() != sha:
        temp = target.with_suffix('.tmp')
        temp.write_bytes(data)
        temp.replace(target)
    return {'path': path, 'sha256': sha, 'bytes': len(data)}


def read_jpeg(response):
    data = response.read(MAX_POSTER_BYTES + 1)
    if len(data) > MAX_POSTER_BYTES or not data.startswith(b'\xff\xd8\xff') or not data.endswith(b'\xff\xd9'):
        raise ValueError('Expected a JPEG cover no larger than 2 MiB')
    return data


def attach_previews(datasets, root, state_dir, warnings, *, sources_for, fetch, max_new=None):
    root, state_dir = Path(root), Path(state_dir)
    cache_path = state_dir / 'previews.json'
    try:
        cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    except (ValueError, OSError):
        cache = {}
    attempted, deferred = 0, 0
    for dataset in datasets:
        dataset.pop('preview', None)
        errors = []
        for url, fingerprint in sources_for(dataset):
            key = hashlib.sha256(encoded(['preview.jpg', url, fingerprint])).hexdigest()
            poster = cache.get(key, {}).get('poster', {})
            path = root / poster.get('path', '')
            if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == poster.get('sha256'):
                dataset['preview'] = {'poster': poster}
                break
            if max_new is not None and attempted >= max_new:
                deferred += 1
                continue
            attempted += 1
            try:
                image, _ = fetch(url, load=read_jpeg)
                poster = asset(root, image, 'jpg')
            except (URLError, TimeoutError, ValueError) as exc:
                errors.append(str(exc.code) if hasattr(exc, 'code') else type(exc).__name__)
                continue
            dataset['preview'] = cache[key] = {'poster': poster}
            break
        if errors and 'preview' not in dataset:
            warnings.append(f"{dataset['id']}: preview.jpg unavailable ({', '.join(errors)})")
    if deferred:
        warnings.append(f'Preview image requests deferred ({deferred}); increase --preview-limit or run sync again')
    state_dir.mkdir(parents=True, exist_ok=True)
    temp = cache_path.with_suffix('.tmp')
    temp.write_bytes(encoded(cache))
    temp.replace(cache_path)
