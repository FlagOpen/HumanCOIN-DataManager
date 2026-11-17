from types import SimpleNamespace as Item
import unittest
from scripts.sync_hf_access import synchronize


class FakeApi:
    def __init__(self):
        self.accepted = {'HumanCOIN/entry': {'alice', 'bob'}, 'HumanCOIN/new': {'alice'}}
        self.rejected = {'HumanCOIN/entry': set(), 'HumanCOIN/new': {'bob'}}
        self.grants = []

    def list_datasets(self, **kwargs):
        return [Item(id=repo, gated='auto', private=False) for repo in self.accepted] + [
            Item(id='HumanCOIN/manual', gated='manual', private=False),
            Item(id='HumanCOIN/private', gated='auto', private=True)]

    def list_accepted_access_requests(self, repo, **kwargs):
        return [Item(username=user) for user in self.accepted[repo]]

    def list_rejected_access_requests(self, repo, **kwargs):
        return [Item(username=user) for user in self.rejected[repo]]

    def grant_access(self, *, repo_id, user, repo_type):
        self.grants.append((repo_id, user))
        self.accepted[repo_id].add(user)


class AccessTest(unittest.TestCase):
    def test_rejections_and_preview(self):
        api = FakeApi()
        result = synchronize(api, ['HumanCOIN/entry'])
        self.assertEqual(result['skipped'], 1)
        self.assertEqual(result['planned'], 0)
        self.assertEqual(api.grants, [])

    def test_new_dataset_and_idempotency(self):
        api = FakeApi()
        api.accepted['HumanCOIN/new'] = set()
        api.rejected['HumanCOIN/new'] = set()
        preview = synchronize(api, ['HumanCOIN/entry'])
        self.assertEqual(preview['planned'], 2)
        self.assertEqual(api.grants, [])
        applied = synchronize(api, ['HumanCOIN/entry'], apply=True)
        self.assertEqual(applied['granted'], 2)
        self.assertEqual(synchronize(api, ['HumanCOIN/entry'], apply=True)['planned'], 0)

    def test_no_mutations_if_planning_fails(self):
        api = FakeApi()
        def fail(*args, **kwargs):
            raise RuntimeError('Inventory unavailable')
        api.list_rejected_access_requests = fail
        with self.assertRaises(RuntimeError):
            synchronize(api, ['HumanCOIN/entry'], apply=True)
        self.assertEqual(api.grants, [])

    def test_scope_validation(self):
        for source in ['Other/entry', 'HumanCOIN/manual', 'HumanCOIN/private']:
            api = FakeApi()
            with self.assertRaises(ValueError):
                synchronize(api, [source], apply=True)
            self.assertEqual(api.grants, [])
