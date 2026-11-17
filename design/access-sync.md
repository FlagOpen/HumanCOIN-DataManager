# Hugging Face access propagation

This administrator tool grants accepted users of explicitly selected entry datasets access to all public `HumanCOIN/*` datasets whose gating mode is `auto`. It does not affect ModelScope. Uses official `HfApi.list_accepted_access_requests`, `list_rejected_access_requests` and `grant_access` methods.

## Configure

In this GitHub repository, open Settings → Secrets and variables → Actions and add `HF_ACCESS_TOKEN`. Use a token from an account with write/admin access to all target datasets and permission to manage gated access. The catalog refresh workflow also reuses this secret for reading gated metadata. Locally the catalog sync accepts HF_TOKEN, falling back to HF_ACCESS_TOKEN. Never put tokens in frontend configuration or commit them.

Once this workflow is published, open Actions → Sync Hugging Face access → Run workflow. Enter one or more full entry dataset IDs separated by spaces. Leave `apply` unchecked to preview counts. Check the target repositories and counts, then run with `apply` checked to grant access.

Local equivalent (Python 3.10+):

```bash
pip install 'huggingface_hub>=0.34,<2'
# Set HF_ACCESS_TOKEN securely in the environment, then:
python scripts/sync_hf_access.py --source HumanCOIN/ENTRY_DATASET
python scripts/sync_hf_access.py --source HumanCOIN/ENTRY_DATASET --apply
```

Replace `ENTRY_DATASET` with the real entry dataset name. No real grants are performed by the tests or by the default preview mode.

## Behavior and limits

- Unions accepted usernames from the specified entry datasets. Does not store emails or form responses, and prints only repository names and counts.
- Discovers current public auto-gated targets on every run. New targets receive the same eligible users on the next execution.
- Reads all access lists before any writes. Skips existing grants and target-level rejected users; rechecks before applying. Repeated runs fill missing grants.
- A partial apply is not transactional: successful grants remain if another grant fails. The command exits nonzero on failure and can be rerun.
- Grant-only. Removing a user from an entry dataset does not revoke permissions previously granted elsewhere. Rejected users on each target remain excluded. Revocation must be managed separately.
- Manual execution only. This does not yet provide immediate, continuous synchronization; do not promise immediate organization-wide access in visitor documentation. A scheduled service can be enabled after preview and verification.
- Entry forms should clearly explain the intended HumanCOIN-wide access scope. Dataset-specific terms are not merged or collected by this script.
