import copy
from datetime import datetime, timedelta, timezone
import json
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import sync_catalog as sync
from scripts.catalog_store import aggregate, publish, validate, read_records, encoded

NOW = datetime(2026,11,13,tzinfo=timezone.utc)
HF_ROW={'id':'HumanCOIN/l3_demo','author':'HumanCOIN','sha':'a'*40,'downloads':4,'tags':['L3'],'lastModified':'2026-11-12T00:00:00Z'}
PORTAL = {'schema_version': 1, 'scene': {'name': 'kitchen'}, 'task_name': 'cook',
          'example_task_description': 'Example recording', 'num_recordings': 2,
          'duration_s': 10, 'size_bytes': 1024, 'modalities': ['RGB', 'EEG'],
          'resolution': '1920x1184', 'primary_camera': 'observation.images.head',
          'preview_video': 'first recording/videos/head.mp4'}

def record(index=0, level='L3'):
    result=sync.normalize(f'HumanCOIN/l3_demo_{index}',HF_ROW,{},PORTAL)
    result['level']=level
    return result

class CatalogTest(unittest.TestCase):
    def test_scene_hierarchy(self):
        from scripts.catalog_store import scene_fields
        self.assertEqual(scene_fields({'category':'commercial_service','area':'dining_area'}), ('dining_area','household'))
        self.assertEqual(scene_fields({'category':'commercial_service','area':'shoe_repair'}), ('shoe_repair','commercial_service'))
        self.assertEqual(scene_fields('kitchen'), ('kitchen','household'))
        self.assertEqual(scene_fields('legacy_scene'), ('legacy_scene',''))
        self.assertEqual(scene_fields({'category':'unknown'}), ('unknown','unknown'))

    def test_metadata_token_scope(self):
        from urllib.request import HTTPRedirectHandler
        with patch.dict('os.environ', {'HF_TOKEN':'', 'HF_ACCESS_TOKEN':'test-secret'}):
            request = sync.metadata_request('https://huggingface.co/datasets/HumanCOIN/demo/raw/main/portal.yaml')
            self.assertEqual(request.get_header('Authorization'), 'Bearer test-secret')
            self.assertNotIn('Authorization', request.headers)
            for url in ['https://www.modelscope.cn/api', 'http://huggingface.co/file', 'https://huggingface.co.evil.test/file']:
                self.assertIsNone(sync.metadata_request(url).get_header('Authorization'))
            redirected = HTTPRedirectHandler().redirect_request(request, None, 302, 'redirect', {}, 'https://cdn.example/file')
            self.assertIsNone(redirected.get_header('Authorization'))

    def setUp(self):
        self.previews = patch('scripts.preview_assets.attach_previews')
        self.previews.start()
        self.addCleanup(self.previews.stop)

    def test_portal_fields_and_hub_preview_urls(self):
        repo = 'HumanCOIN/l1_demo_1280x720_30fps'
        metadata = sync.validate_portal(PORTAL, repo)
        hf = sync.normalize(repo, HF_ROW, {}, metadata)
        self.assertEqual(hf['level'], 'L3')
        self.assertEqual(hf['episodes'], 2)
        self.assertEqual(hf['durationSeconds'], 10)
        self.assertEqual(hf['description'], 'Example recording')
        self.assertEqual(hf['sceneCategory'], 'household')
        self.assertEqual(hf['mods'], ['RGB', 'EEG'])
        self.assertEqual(hf['resolution'], '1920x1184')
        self.assertEqual(hf['resolutionSource'], 'metadata')
        self.assertTrue(hf['videos'][0]['url'].endswith('/first%20recording/videos/head.mp4'))
        ms = sync.normalize(repo, {}, {'Name': 'l1_demo'}, metadata)
        self.assertEqual(ms['videos'][0]['url'], sync.ms_file(repo, PORTAL['preview_video']))
        self.assertEqual(ms['metadataSources'], [sync.ms_file(repo, 'portal.yaml')])

    def test_missing_portal_uses_listing_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            warnings = []
            with patch.object(sync, 'fetch', side_effect=sync.HTTPError('url', 404, 'missing', {}, None)) as fetch:
                row, status, _ = sync.source_record('HumanCOIN/l1_demo_1280x720', 'huggingface', HF_ROW, Path(tmp), NOW, warnings)
            self.assertEqual(status, 'missing')
            self.assertEqual(row['resolution'], '1280x720')
            self.assertIsNone(row['episodes'])
            self.assertEqual(row['videos'], [])
            self.assertIn('portal.yaml', warnings[0])
            fetch.assert_called_once_with(sync.portal_url(row['id'], 'huggingface', HF_ROW['sha']), load=sync.yaml.safe_load)

    def test_portal_rejects_invalid_metrics_and_paths(self):
        for invalid in ({'duration_s': '10'}, {'preview_video': '../sample.mp4'},
                        {'preview_video': 'https://example.com/sample.mp4'}, {'schema_version': True}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                sync.validate_portal({**PORTAL, **invalid}, HF_ROW['id'])

    def test_pagination_and_partial_inventory_rejection(self):
        with patch.object(sync,'fetch',side_effect=[([{'id':'one'}],'<https://huggingface.co/api/datasets?cursor=n>; rel="next"'),([{'id':'two'}],'')]):
            self.assertEqual(len(sync.hf_catalog()),2)
        with patch.object(sync,'fetch',side_effect=[({'Code':200,'Data':[{'Name':'one'}],'TotalCount':2},''),({'Code':200,'Data':[],'TotalCount':2},'')]):
            with self.assertRaisesRegex(ValueError,'Incomplete'):sync.ms_catalog()
    def test_statistics_missing_zero_invalid_and_unknown(self):
        a={'episodes':0,'durationSeconds':None,'sizeBytes':-1,'downloads':None}
        b={'episodes':2.5,'durationSeconds':3,'sizeBytes':float('inf'),'downloads':0,'staleMetrics':['durationSeconds'],'derivedMetrics':['durationSeconds']}
        s=aggregate([a,b]);self.assertEqual(s['episodes']['sumKnown'],0);self.assertEqual(s['episodes']['missingCount'],1)
        self.assertEqual(s['durationSeconds'],{'sumKnown':3,'knownCount':1,'missingCount':1,'staleCount':1,'derivedCount':1})
        self.assertIsNone(s['sizeBytes']['sumKnown']);self.assertEqual(aggregate([])['episodes']['sumKnown'],0)
    def test_shards_atomic_validation_stable_snapshot_and_gc(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'data/catalog.json';rows=[record(i,('L1','L2','L3','Unknown')[i%4]) for i in range(80)]
            m=publish(out,rows,generated_at=NOW.isoformat(),sources={},warnings=[],shard_limit=3000)
            self.assertEqual(m['stats']['datasets'],80);self.assertGreater(len(m['tiers']['L1']['files']),1);validate(out.parent)
            self.assertTrue(all(part['bytes']<=3000 for tier in m['tiers'].values() for part in tier['files']))
            newer=publish(out,rows,generated_at=(NOW+timedelta(days=1)).isoformat(),sources={},warnings=[],shard_limit=3000)
            self.assertEqual(m['snapshotId'],newer['snapshotId']);self.assertEqual(m['generatedAt'],newer['generatedAt']);self.assertNotEqual(m['checkedAt'],newer['checkedAt'])
            before=out.read_bytes()
            with self.assertRaises(ValueError):publish(out,rows+[rows[0]],generated_at=NOW.isoformat(),sources={},warnings=[])
            self.assertEqual(out.read_bytes(),before)
            rows[0]['downloads']=999
            changed=publish(out,rows,generated_at=(NOW+timedelta(days=10)).isoformat(),sources={},warnings=[])
            self.assertNotEqual(changed['snapshotId'],m['snapshotId'])
            old_detail=next(read_records(out.parent)[0]['detailPath'] for _ in [0])
            self.assertTrue((out.parent/old_detail).exists());self.assertEqual(len(list((out.parent/'manifests').glob('*.json'))),2)
    def test_dynamic_stats_do_not_rewrite_details(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'catalog.json';d=record();a=publish(out,[d],generated_at=NOW.isoformat(),sources={},warnings=[])
            first=read_records(out.parent)[0]['detailPath'];d['downloads']=100;d['updated']='2026-11-13';publish(out,[d],generated_at=NOW.isoformat(),sources={},warnings=[])
            self.assertEqual(first,read_records(out.parent)[0]['detailPath'])
    def test_incremental_sync_stale_metadata_and_confirmed_removal(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'data/catalog.json';state=Path(tmp)/'state'
            with patch.object(sync,'hf_catalog',return_value=[HF_ROW]),patch.object(sync,'ms_catalog',return_value=[]),patch.object(sync,'fetch',return_value=(PORTAL,'')) as fetch:
                first=sync.synchronize(out,state,now=NOW);self.assertEqual(fetch.call_count,1)
            with patch.object(sync,'hf_catalog',return_value=[HF_ROW]),patch.object(sync,'ms_catalog',return_value=[]),patch.object(sync,'fetch') as fetch:
                same=sync.synchronize(out,state,now=NOW+timedelta(hours=1));fetch.assert_not_called();self.assertEqual(first['snapshotId'],same['snapshotId'])
            changed={**HF_ROW,'sha':'b'*40}
            with patch.object(sync,'hf_catalog',return_value=[changed]),patch.object(sync,'ms_catalog',return_value=[]),patch.object(sync,'fetch',side_effect=TimeoutError('temporary')):
                stale=sync.synchronize(out,state,now=NOW+timedelta(hours=2));self.assertEqual(stale['stats']['episodes']['staleCount'],1)
            with patch.object(sync,'hf_catalog',return_value=[]),patch.object(sync,'ms_catalog',return_value=[]):
                pending=sync.synchronize(out,state,now=NOW+timedelta(hours=3));self.assertEqual(pending['stats']['datasets'],1)
                removed=sync.synchronize(out,state,now=NOW+timedelta(hours=4));self.assertEqual(removed['stats']['datasets'],0)
    def test_inventory_failure_preserves_published_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'data/catalog.json';publish(out,[record()],generated_at=NOW.isoformat(),sources={},warnings=[]);before=out.read_bytes()
            with patch.object(sync,'hf_catalog',side_effect=TimeoutError('down')):
                with self.assertRaises(TimeoutError):sync.synchronize(out,Path(tmp)/'state',now=NOW)
            self.assertEqual(before,out.read_bytes())
    def test_rate_limit_reduces_concurrency_and_retries(self):
        response=io.BytesIO(b'{"ok":true}');response.headers={}
        previous=sync._NETWORK_LIMIT
        sync._NETWORK_LIMIT=4
        try:
            with patch.object(sync,'urlopen',side_effect=[sync.HTTPError('url',429,'limited',{'Retry-After':'0'},None),response]),patch.object(sync.time,'sleep'):
                self.assertTrue(sync.fetch('https://example.com')[0]['ok'])
                self.assertEqual(sync._NETWORK_LIMIT,2)
        finally:sync._NETWORK_LIMIT=previous

    def test_retry_policy(self):
        self.assertEqual(sync.retry_delay('5',0),5);self.assertEqual(sync.retry_delay('999',0),120)
        with patch.object(sync,'urlopen',side_effect=sync.HTTPError('url',403,'denied',{},None)) as opening:
            with self.assertRaises(sync.HTTPError):sync.fetch('https://example.com')
            self.assertEqual(opening.call_count,1)

if __name__=='__main__':unittest.main()
