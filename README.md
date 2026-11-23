# HumanCOIN DataManager

[简体中文](README_zh-CN.md) · [Live portal](https://flagopen.github.io/HumanCOIN-DataManager/) · [Project introduction](https://koorye.github.io/HumanCOIN-dev/)

HumanCOIN DataManager is a web portal for finding, previewing and downloading HumanCOIN datasets. Filter datasets, save your selection and copy ready-to-run download commands without assembling repository names by hand.

The first batch is expected to include approximately **1,200 hours** of data. To request access to the full dataset, use the application form on the live portal. The portal catalog shows what is currently published.

## Before downloading: request access

Visit [HumanCOIN on Hugging Face](https://huggingface.co/HumanCOIN), open a dataset and complete the access form shown on its page. Automatically approved datasets grant access upon submission; downloads still require authentication with the approved account.

ModelScope permissions are managed separately. Follow the requirements on the [HumanCOIN ModelScope page](https://www.modelscope.cn/organization/HumanCOIN) and individual dataset pages. Hugging Face approval does not grant ModelScope access.

## Download a single dataset

1. Open the portal and find a dataset.
2. Choose Hugging Face or ModelScope in the selection area below the results.
3. Click **Download** on the dataset card and copy the generated command.
4. Install the tool, then run the command in your terminal.

Install once with Python **3.10–3.13**:

```bash
pip install -U "humancoin>=0.1.1"
```

This installation supports both platforms; no source checkout is required. See the [HumanCOIN repository](https://github.com/FlagOpen/HumanCOIN) for tool documentation. For restricted datasets, sign in locally with an approved account or configure `HF_TOKEN` / `MODELSCOPE_TOKEN` in your local environment. Do not commit tokens or enter them into the portal.

## Download a batch

1. **Open the portal:** visit [HumanCOIN-DATA](https://flagopen.github.io/HumanCOIN-DataManager/). Switch English/Chinese in the top bar; dataset names and metadata remain in English.
2. **Find datasets:** filter by tier, modality, scene category and area, task or main camera resolution. Search by name or repository ID.
3. **Select datasets:** check **Select Dataset** on the cards. **Select page** selects the current page; **Select all matches** selects every matching page.
4. **Choose a platform:** select Hugging Face or ModelScope in **My Selection**. All selected datasets must be available on that platform.
5. **Get commands:** click **Generate Download Command**, copy the commands and run them in your terminal. A batch may generate multiple commands.

Commands download to `./data/HumanCOIN/` by default. Change `--target-dir` to choose another location. `--revision` pins each repository version for reproducibility, while `--max-workers` controls download concurrency.

The portal generates commands; the local tool downloads data directly from the selected platform.

## Save and share a selection

- **Export JSON:** save the current selection as `selection.json`.
- **Import JSON:** restore your saved selection or one shared by another user.
- **Clear:** remove the current selection.

The JSON file contains a selection list, not dataset files. Importing it does not upload local data. Your browser also remembers your selection.

## Previews and catalog updates

Cards and dataset details display the dataset cover. To publish a cover, place a JPEG named `preview.jpg` (up to 2 MiB) at the dataset repository root.

The catalog refreshes daily at **08:00 and 09:00 Asia/Shanghai** and can also be refreshed manually by maintainers. Apply an update when the portal offers it. To avoid removing datasets during temporary API failures, removal requires two consecutive successful syncs confirming absence from all sources.

## Need help?

- Download issues: check tool installation, connectivity, access approval and token permissions.
- Preview issues: check Hugging Face connectivity and permissions, or open the dataset on its source platform.
- Portal bugs: [open an issue](https://github.com/FlagOpen/HumanCOIN-DataManager/issues).
- Tool and dataset-reading questions: [HumanCOIN repository](https://github.com/FlagOpen/HumanCOIN).

## Local development

Portal development requires Python 3.10+ and Node.js 20+. There are no frontend dependencies to install.

```bash
npm run dev
```

Open http://127.0.0.1:8000/ . See the [development guide](design/development-guide.md) for architecture, sync and tests, [release checks](RELEASE_CHECK.md) for deployment, and [access synchronization](design/access-sync.md) for administrative configuration.
