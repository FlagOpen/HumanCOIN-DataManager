#!/usr/bin/env python3
"""Propagate accepted entry-dataset users to public HumanCOIN auto-gated datasets."""
import argparse
import os
import sys


def usernames(requests):
    return {request.username for request in requests}


def synchronize(api, sources, *, apply=False):
    sources = sorted(set(sources))
    if not sources or any(not repo.startswith('HumanCOIN/') or repo.count('/') != 1 for repo in sources):
        raise ValueError('Specify entry datasets as HumanCOIN/name.')
    # Fully read the inventory and source access lists before performing mutations.
    inventory = {dataset.id: dataset for dataset in api.list_datasets(author='HumanCOIN')}
    for repo in sources:
        if repo not in inventory or inventory[repo].gated != 'auto' or inventory[repo].private:
            raise ValueError('Entry datasets must be public HumanCOIN datasets with automatic gating.')
    accepted = set()
    for repo in sources:
        accepted.update(usernames(api.list_accepted_access_requests(repo, repo_type='dataset')))
    targets = sorted(repo for repo, info in inventory.items()
                     if repo.startswith('HumanCOIN/') and info.gated == 'auto' and not info.private)
    plan = []
    for repo in targets:
        existing = usernames(api.list_accepted_access_requests(repo, repo_type='dataset'))
        rejected = usernames(api.list_rejected_access_requests(repo, repo_type='dataset'))
        candidates = accepted - existing - rejected
        plan.append((repo, sorted(candidates), len(accepted & rejected)))
    result = {'users': len(accepted), 'targets': len(targets), 'planned': 0,
              'granted': 0, 'skipped': 0, 'failed': 0}
    for repo, candidates, blocked in plan:
        result['planned'] += len(candidates)
        result['skipped'] += blocked
        print(f'{repo}: {len(candidates)} missing grants; {blocked} rejected users skipped')
    if not apply:
        return result
    for repo, candidates, _ in plan:
        # Recheck decisions just before writes, including refusals made after planning.
        existing = usernames(api.list_accepted_access_requests(repo, repo_type='dataset'))
        rejected = usernames(api.list_rejected_access_requests(repo, repo_type='dataset'))
        for user in candidates:
            if user in existing or user in rejected:
                result['skipped'] += 1
                continue
            try:
                api.grant_access(repo_id=repo, user=user, repo_type='dataset')
                result['granted'] += 1
            except Exception as error:
                # No request bodies, personal information, or tokens in logs.
                print(f'{repo}: grant failed ({type(error).__name__})', file=sys.stderr)
                result['failed'] += 1
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', nargs='+', required=True, help='Entry dataset IDs, space-separated')
    parser.add_argument('--apply', action='store_true', help='Grant missing access; otherwise preview only')
    args = parser.parse_args()
    token = os.environ.get('HF_ACCESS_TOKEN')
    if not token:
        parser.error('Set HF_ACCESS_TOKEN to an account token with write access to the gated datasets.')
    try:
        from huggingface_hub import HfApi
        result = synchronize(HfApi(token=token), args.source, apply=args.apply)
    except Exception as error:
        print(f'Access sync stopped ({type(error).__name__}). Check source IDs and token permissions.', file=sys.stderr)
        return 1
    print(('APPLY' if args.apply else 'PREVIEW') + ': ' + ', '.join(f'{k}={v}' for k, v in result.items()))
    return 1 if result['failed'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
