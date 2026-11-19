import io
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import preview_assets as previews
from scripts.catalog_store import publish, validate, read_records

URL='https://huggingface.co/datasets/HumanCOIN/example/resolve/abc/preview.jpg'

class PreviewTest(unittest.TestCase):
    def test_only_jpeg_is_accepted(self):
        with self.assertRaises(ValueError):
            previews.read_jpeg(io.BytesIO(b'not a jpg'))

    def test_cached_cover_does_not_fetch_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, state = Path(tmp)/'data', Path(tmp)/'state'
            image = bytes.fromhex('ffd8ffe0ffd9')
            def download(url, *, load):
                self.assertEqual(url, URL)
                return load(io.BytesIO(image)), ''
            rows=[{'id':'HumanCOIN/test'}]
            warnings=[]
            with patch('scripts.preview_assets.read_jpeg', wraps=previews.read_jpeg) as reader:
                for _ in range(2):
                    previews.attach_previews(rows, root, state, warnings,
                                             sources_for=lambda row: [(URL, 'abc')], fetch=download)
                reader.assert_called_once()
            self.assertEqual(set(rows[0]['preview']), {'poster'})
            self.assertEqual(warnings, [])

    def test_request_budget_defers_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows=[{'id':'HumanCOIN/test'}];warnings=[]
            def unexpected_fetch(*args, **kwargs):
                self.fail('No image should be requested')
            previews.attach_previews(rows,Path(tmp)/'data',Path(tmp)/'state',warnings,
                                     sources_for=lambda row: [(URL, 'abc')], fetch=unexpected_fetch, max_new=0)
            self.assertNotIn('preview',rows[0]);self.assertIn('deferred',warnings[0])
    def test_preview_hashes_are_validated_and_retained(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'data';root.mkdir();ref={'poster':previews.asset(root,b'jpg','jpg'),'clip':previews.asset(root,b'mp4','mp4')}
            row={'id':'HumanCOIN/test','level':'L3','scene':'desk','task':'move','mods':['RGB'],'resolution':None,'episodes':1,'durationSeconds':4,'sizeBytes':10,'downloads':0,'updated':'','public':True,'hubs':{},'streams':[],'videos':[],'preview':ref}
            publish(root/'catalog.json',[row],generated_at=datetime.now(timezone.utc).isoformat(),sources={},warnings=[])
            self.assertEqual(read_records(root)[0]['preview'],ref);validate(root)
            (root/ref['poster']['path']).write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'preview hash'):validate(root)

if __name__=='__main__':unittest.main()
