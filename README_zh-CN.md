# HumanCOIN DataManager

[English](README.md) · [在线门户](https://flagopen.github.io/HumanCOIN-DataManager/?lang=zh) · [HumanCOIN 项目介绍](https://koorye.github.io/HumanCOIN-dev/)

HumanCOIN DataManager 是查找、预览和下载 HumanCOIN 数据集的网页工具。你可以筛选数据、保存选择，并直接复制下载命令，无需手动拼接数据集名称。

首批预计开放约 **1,200 小时**数据。后续数据欢迎通过邮件联系申请使用：[humancoin@163.com](mailto:humancoin@163.com)。实际已发布的数据以门户目录为准。

## 下载前：申请访问权限

前往 [HumanCOIN Hugging Face 主页](https://huggingface.co/HumanCOIN)，选择需要的数据集，按页面提示填写申请信息并提交。启用自动审批的数据集会自动批准申请，下载时仍需使用获批账号认证。

HumanCOIN 每 5 分钟运行一次跨数据集权限同步：在任意公开 `auto` 数据集获批后，系统会补齐其他公开 `auto` 数据集的权限，不必逐个重复申请。定时任务可能延迟，明确被拒绝的权限不会被重新授予。新增数据集也会在后续同步中纳入。

魔搭权限单独管理，以 [HumanCOIN 魔搭主页](https://www.modelscope.cn/organization/HumanCOIN)和具体数据集页面为准；Hugging Face 的授权不会自动同步到魔搭。

## 快速下载一个数据集

1. 打开门户，找到需要的数据集。
2. 在页面下方选择下载平台：Hugging Face 或 ModelScope。
3. 点击对应卡片上的“下载”，复制生成的命令。
4. 安装工具后，在终端执行命令。

使用 Python **3.10–3.13** 安装下载工具，只需一次：

```bash
pip install -U "humancoin>=0.1.1"
```

同一安装支持两个平台。无需克隆工具源码，工具仓库见 [HumanCOIN](https://github.com/FlagOpen/HumanCOIN)。受限数据集需要先登录获批账号，或在本地环境中配置 `HF_TOKEN` / `MODELSCOPE_TOKEN`；不要将 Token 上传到仓库或填写进门户。

## 批量下载

1. **打开门户**：访问 [HumanCOIN-DATA](https://flagopen.github.io/HumanCOIN-DataManager/?lang=zh)。右上角可切换中英文，数据集名称和元数据保持英文。
2. **筛选数据**：按 L1/L2/L3、模态、场景类别与区域、任务、主相机分辨率筛选，也可搜索名称或 ID。
3. **选择数据集**：勾选卡片上的“选择数据集”。“选择本页”只选当前页，“选择全部匹配项”覆盖筛选后的所有页面。
4. **选择下载平台**：在“我的选择”区域选择 Hugging Face 或 ModelScope。所选数据集须在对应平台可用。
5. **生成命令**：点击“生成下载命令”，复制到终端执行。不同数据集可能生成多条命令。

命令默认下载至 `./data/HumanCOIN/`。可以修改 `--target-dir` 指定保存目录。`--revision` 固定所选仓库版本，便于复现实验；`--max-workers` 控制下载并发数。

门户只生成命令，实际数据由本地工具从所选平台下载。

## 保存和分享选择

- **导出 JSON**：将当前选择保存为 `selection.json`。
- **导入 JSON**：恢复之前保存或他人分享的数据集选择。
- **清空**：移除当前选择。

JSON 是选择清单，不包含数据本身，也不会上传本地数据。浏览器还会记住当前选择。

## 预览与目录更新

卡片支持封面和短视频预览，点击“预览”可查看视频与传感器信息。自动播放取决于浏览器设置；完整视频目前优先从 Hugging Face 加载，请确保网络可达并具备所需权限。选择下载平台不会切换预览来源。

数据目录每天北京时间 **08:00、09:00** 自动同步，也可由维护者手动触发。门户提示目录更新后，点击刷新即可应用。为避免临时接口异常导致误删，数据集从所有来源消失后，需要连续两次成功同步确认才会移除。

## 需要帮助？

- 下载失败：确认工具已安装、目标平台网络可达、账号已获授权，Token 权限有效。
- 预览失败：检查 Hugging Face 连接与访问权限，也可前往数据来源平台查看。
- 网页问题：[提交 Issue](https://github.com/FlagOpen/HumanCOIN-DataManager/issues)。
- 工具与数据读取问题：[HumanCOIN 仓库](https://github.com/FlagOpen/HumanCOIN)。
- 数据申请与其他联系：[humancoin@163.com](mailto:humancoin@163.com)。

## 本地运行与开发

门户开发需要 Python 3.10+ 和 Node.js 20+，前端无需安装依赖：

```bash
npm run dev
```

打开 http://127.0.0.1:8000/ 。架构、同步与测试说明见[开发指南](design/development-guide.md)，发布前检查见 [RELEASE_CHECK.md](RELEASE_CHECK.md)，权限同步配置见 [access-sync.md](design/access-sync.md)。
