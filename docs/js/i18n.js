// Translate portal UI only. Dataset content, metadata, IDs and commands stay verbatim.
const translations = {
 'Data Guide':'数据说明',
 'Request full dataset access':'申请全量数据',
 'Full name':'姓名',
 'Email address':'邮箱',
 'Phone number (optional)':'手机号（选填）',
 'Institution or organization':'所属机构',
 'How will you use the dataset?':'请说明数据用途',
 'The HumanCOIN team will use this information to review your request and contact you.':'HumanCOIN 团队会使用这些信息审核申请并联系你。',
 'Submit request':'提交申请',
 'Online applications are not available yet.':'在线申请暂未开放。',
 'Submitting your request…':'正在提交申请…',
 'Your request was received.':'申请已提交。',
 'We could not submit your request. Please try again.':'申请提交失败，请重试。',
 "HumanCOIN Data Portal | Egocentric Manipulation Dataset":"HumanCOIN 数据门户 | 第一视角人类操作数据集",
 "HUMANCOIN · HUMAN INTENT":"HUMANCOIN · 人的意图与动作",
 "HumanCOIN — intent before action":"HumanCOIN — 意图先于动作",
 "HumanCOIN is building a 12,500-hour first-person manipulation corpus around the human intent pathway: gaze before the hand, muscle load before contact, and cortical activity before the motor command. Its three nested tiers capture proxies for attention (L1), exertion (L2), and cognition (L3) in a shared time and coordinate frame.":"人在伸手前会先看向目标，触碰前肌肉已开始发力，大脑也在为动作做准备。HumanCOIN 计划采集 12,500 小时的第一视角操作数据，从视觉注意、肌肉运动到认知活动，分三层记录这些信号。各层数据使用统一的时钟和坐标系，便于对齐分析。",
 "CC BY-NC 4.0 data":"数据许可 CC BY-NC 4.0",
 "Apache-2.0 code":"代码许可 Apache-2.0",
 "Project homepage":"项目主页",
 "HumanCOIN project links":"HumanCOIN 项目链接",
 "Technical report":"技术报告",
 "Data download portal":"数据下载门户",
 "User documentation":"用户使用文档",
 "ModelScope Community":"ModelScope（魔搭社区）",
 "Contact":"联系我们",
 "Get the data":"获取数据",
 "Read the quick start":"查看下载指南",
 "L1 · Attention":"L1 · 视觉注意",
 "L2 · Exertion":"L2 · 肌肉运动",
 "L3 · Cognition":"L3 · 认知活动",
 "Attention":"视觉注意",
 "Exertion":"肌肉运动",
 "Cognition":"认知活动",
 "10,000 h planned":"计划 10,000 小时",
 "2,000 h planned":"计划 2,000 小时",
 "500 h planned":"计划 500 小时",
 "INTENT PATHWAY · OUTPUT END":"意图如何显现 · 视线指向",
 "INTENT PATHWAY · MIDWAY":"意图如何执行 · 肌肉运动",
 "INTENT PATHWAY · ORIGIN":"意图如何形成 · 大脑活动",
 "Gaze reaches the target before the hand.":"手还没到，目光已落在目标上。",
 "Muscle load builds before contact.":"碰到物体之前，肌肉就开始发力。",
 "Cortical activity precedes the motor command.":"运动指令发出前，皮层活动已出现。",
 "Four headband cameras capture first-person video. Gaze inferred from these views shows where attention shifts before the hand arrives.":"头环上的四台相机记录第一视角视频。通过视频估计注视方向，可以看出手伸向物体之前，操作者在看哪里。",
 "L2 inherits L1 and adds two forearm sEMG armbands (8+8 channels) to capture the effort a task demands as it unfolds.":"在 L1 的基础上，用两个臂环采集左右前臂的表面肌电（各 8 通道），观察操作过程中何时发力、发力如何变化。",
 "L3 inherits L1 and L2 and adds scalp EEG. In the controlled subset, an eye tracker, motion-capture gloves and 6-DoF trackers directly measure gaze, hand pose and finger kinematics.":"在 L1 和 L2 的基础上增加头皮脑电。部分任务在受控环境中采集，并用眼动仪、动捕手套和六自由度追踪器直接测量视线、手部位姿和手指运动。",
 "38/38 scene classes · inferred gaze · RGB · depth/point cloud · 6-DoF head/wrist pose":"覆盖全部 38 类场景 · 估计注视 · RGB · 深度与点云 · 头部和手腕的六自由度位姿",
 "21/38 scene classes · adds sEMG (8+8 channels)":"覆盖 21 类场景 · 新增双侧表面肌电（各 8 通道）",
 "9/38 scene classes (controlled) · adds EEG and measured gaze/hand pose":"受控采集覆盖 9 类场景 · 新增脑电、实测注视与手部位姿",
 "Browse L1 episodes →":"浏览 L1 数据 →",
 "Browse L2 episodes →":"浏览 L2 数据 →",
 "Browse L3 episodes →":"浏览 L3 数据 →",

 'Hugging Face login':'登录 Hugging Face',
 'ModelScope authentication':'魔搭认证',
 'For restricted datasets, request access on ModelScope. Once approved, create a token with the same account and run these commands in your Bash download terminal.':'下载受限数据集前，请先在魔搭申请访问权限。获批后，用同一账号创建令牌，并在用于下载的 Bash 终端中运行以下命令。',
 'ModelScope access tokens ↗':'魔搭访问令牌 ↗',
 'Run these commands in the terminal you will use to download. Confirm that the displayed username has access to the dataset.':'请在用于下载的终端中运行这些命令，确认显示的账号已获得该数据集的访问权限。',
 'Data availability':'数据开放',
 'The first batch is expected to include approximately':'首批预计开放约',
 '1,200 hours':'1,200 小时',
 'of data.':'数据。',
 'For access to subsequent data, please email':'后续数据欢迎通过邮件联系申请使用：',
 'Modalities':'模态','Detailed stream metadata is unavailable.':'暂无详细的传感器流元数据。','No modalities declared.':'暂无模态信息。','No cover image is available.':'暂无封面图片。',
 'Before downloading':'下载须知',
 'Visit the':'请访问',
 'and open the datasets you need. If access is restricted, submit a request, wait for approval and authenticate with the approved account before downloading.':'，打开所需数据集。如有权限要求，请先申请，待批准后使用获批账号认证下载。',

 'First data release · November 24–30, 2026':'首批数据开放 · 2026 年 11 月 24–30 日',
 'The first batch is expected to include approximately 1,200 hours of data. For access to subsequent data, please email':'首批预计开放约 1,200 小时数据。后续数据欢迎通过邮件联系申请使用：',
 'to apply.':'。',
 'HumanCOIN DataManager — Multimodal Human Data Portal':'HumanCOIN DataManager — 多模态人体数据门户',
 'DATA PORTAL':'数据门户','WORKSPACE':'工作区','Overview':'概览','Explore Datasets':'浏览数据集','Explore datasets':'浏览数据集','My Selection':'我的选择','▤   My Selection':'▤ 我的选择','Quick Start':'快速入门','RESOURCES':'资源','About HumanCOIN':'关于 HumanCOIN','Project introduction ↗':'项目介绍 ↗','Public Data Portal':'公开数据门户',
 'EGOCENTRIC MANIPULATION · HUMAN SIGNALS':'第一视角操作 · 人体信号','Human activity,':'人类活动，','and the signals behind it.':'及其背后的信号。',
 'HumanCOIN connects egocentric multi-view observations with human signals, including gaze, surface EMG, EEG and glove-based finger kinematics. Three tiers—visual, motor and cognitive intention—share a unified spatiotemporal reference, bringing scene coverage and signal depth together for embodied manipulation research.':'HumanCOIN 将第一视角多视角观测与注视、表面肌电、脑电及手套采集的手指运动学等人体信号相结合。视觉意图、运动意图和认知意图三个等级共享统一的时空参考，为具身操作研究兼顾场景覆盖与信号深度。',
 'Download Quick Start →':'下载快速入门 →','Data at a glance':'数据概览','Published dataset overview':'已发布数据集概况','Check for updates':'检查更新','New catalog available · Refresh':'目录有更新 · 刷新','Loading dataset catalog…':'正在加载数据目录…','Datasets':'数据集','Total Episodes':'总片段数','Total Duration':'总时长','HF Downloads':'HF 下载量','Published dataset collections':'已发布的数据集集合','Published dataset repositories':'已发布的数据集仓库','Across all data levels':'覆盖所有数据等级','Across dataset repositories':'按数据集仓库汇总','Multimodal recordings':'多模态记录','Total duration across repositories':'仓库时长汇总','Hugging Face statistics':'Hugging Face 平台统计','Hugging Face dataset downloads':'Hugging Face 数据集下载量',
 'Explore by data level':'按数据等级浏览','A shared task ontology across three tiers, from everyday scenes to motor execution and cognitive signals.':'三个等级共享任务本体，覆盖日常场景、运动执行与认知信号。','VISUAL INTENTION':'视觉意图','MOTOR INTENTION':'运动意图','COGNITIVE INTENTION':'认知意图','Visual intention':'视觉意图','Motor intention':'运动意图','Cognitive intention':'认知意图',
 'Multi-view headband capture covers real-world environments. Gaze, hand motion and scene depth are estimated from images to reflect the operator’s focus of attention.':'头环多视角覆盖真实环境，通过图像估计注视、手部运动、场景深度，反映操作者的关注目标。','Adds bilateral surface EMG and wrist views to L1, recording motor execution during semi-structured tasks.':'在 L1 基础上加入双侧表面肌电与腕部视角，记录半结构化任务中的运动执行。','Adds EEG, measured gaze, motion-capture gloves and measured poses to the earlier tiers for controlled tabletop manipulation.':'在前述等级基础上加入脑电、实测注视、动作捕捉手套、实测位姿，用于受控的桌面操作。','Open environments':'开放环境','Everyday environments':'日常环境','Tabletop manipulation':'桌面操作','Explore ↗':'浏览 ↗',
 'Filter complete datasets by tier, modality, scene, task and main camera resolution. Downloads include the full dataset.':'按等级、模态、场景、任务和主相机分辨率筛选完整数据集。下载包含整个数据集。','Filters':'筛选','Reset all':'重置全部','DATA LEVEL':'数据等级','All levels':'全部等级','MODALITIES':'模态','Match all':'同时满足','SCENE CATEGORY':'场景类别','SCENE AREA':'场景区域','All categories':'全部类别','All areas':'全部区域','TASK':'任务','All tasks':'全部任务','MAIN CAMERA RESOLUTION':'主相机分辨率','All resolutions':'全部分辨率','Search tasks…':'搜索任务…','Search tasks':'搜索任务','Scene category':'场景类别','Main camera resolution':'主相机分辨率','Search ID, task, scene, modality or summary...':'搜索 ID、任务、场景、模态或简介…','Default order':'默认排序','Newest first':'最新优先','Most episodes':'片段最多','Most downloaded':'下载最多','Showing':'当前显示','datasets':'个数据集','All levels and modalities':'全部等级和模态','All modalities in selected levels':'所选等级的全部模态','Retry scope':'重试加载','No datasets match your filters. Try adjusting the selected modalities or scene.':'没有匹配的数据集，请调整模态或场景等筛选条件。','Per page':'每页','Previous':'上一页','Next':'下一页',
 'Generate commands for complete datasets, or export selection.json to save your selection.':'为完整数据集生成下载命令，或导出 selection.json 保存选择。','Select page':'选择本页','Select all matches':'选择全部匹配项','↑ Import JSON':'↑ 导入 JSON','Clear':'清空','↓ Export JSON':'↓ 导出 JSON','⌘ Generate Download Command':'⌘ 生成下载命令','Select Dataset':'选择数据集','◉ Preview':'◉ 预览','↓ Download':'↓ 下载','HOVER TO PLAY':'悬停播放','TAP TO PREVIEW':'点击预览','VIDEO PREVIEW':'视频预览','Cached metadata':'缓存的元数据','Dataset':'数据集','Close':'关闭','© HumanCOIN · Egocentric Manipulation & Human Signals':'© HumanCOIN · 第一视角操作与人体信号',
 'Welcome to HumanCOIN':'欢迎使用 HumanCOIN','Please make sure you can access':'请确保能够访问','Hugging Face ↗':'Hugging Face ↗','. Full video previews currently load from Hugging Face.':'。完整视频预览目前从 Hugging Face 加载。','Before downloading, visit the':'下载前，请访问','HumanCOIN Hugging Face page ↗':'HumanCOIN Hugging Face 主页 ↗',', open the datasets you need and request download access where required. For gated datasets, wait for approval and authenticate with the approved account before downloading.':'，打开所需数据集，如有权限要求，请先申请。对于受限数据集，请等待批准，并使用获批账号认证后下载。','Continue to portal':'进入门户',
 'Download dataset':'下载数据集','Batch download':'批量下载','LOADING PREVIEW…':'正在加载预览…','PLAYING PREVIEW':'正在播放预览','CLICK PREVIEW':'点击预览','Previous selections':'上一页选择','Next selections':'下一页选择',
 'INSTALL (ONCE)':'安装（仅需一次）','INSTALL FROM PYPI':'从 PyPI 安装','DOWNLOAD COMMAND':'下载命令','⧉ Copy Command':'⧉ 复制命令','Selection JSON':'选择清单 JSON','Get Download Command →':'获取下载命令 →','HumanCOIN · Quick Start':'HumanCOIN · 快速入门','HumanCOIN Repository ↗':'HumanCOIN 仓库 ↗','HumanCOIN project · Concept and acquisition architecture ↗':'HumanCOIN 项目 · 概念与采集架构 ↗',
 'Filter datasets, choose a source, select complete repositories and generate download commands. Your selection is saved in this browser and can be imported or exported as JSON.':'筛选数据集，选择下载平台与完整仓库，并生成下载命令。选择会保存在当前浏览器中，也可通过 JSON 导入或导出。',
 'HumanCOIN is an egocentric multimodal dataset for embodied manipulation. It connects visible actions with the operator’s state through multi-view vision, gaze, surface EMG, EEG and glove kinematics under a unified spatiotemporal reference, supporting research into attention, execution and cognition.':'HumanCOIN 是面向具身操作的第一视角多模态数据集。在统一时空参考下，利用多视角视觉、注视、表面肌电、脑电与手套运动学，将可见动作与操作者状态相联系，支持注意、执行与认知研究。',
 'Three acquisition tiers share a task ontology. L1, visual intention, emphasizes everyday scene coverage. L2, motor intention, adds EMG and wrist views. L3, cognitive intention, adds EEG, measured gaze and detailed kinematic measurements. Deeper tiers focus on more controlled tasks with richer signal measurements.':'三个采集等级共享任务本体。L1 视觉意图侧重日常场景覆盖；L2 运动意图增加肌电和腕部视角；L3 认知意图增加脑电、实测注视和详细的运动学测量。更深的等级聚焦更受控的任务，并提供更丰富的信号。',
 'This portal provides discovery, previews, filters and downloads for published datasets. Available modalities follow each repository’s metadata. Planned project scale is distinct from the published catalog statistics shown here.':'本门户提供已发布数据集的浏览、预览、筛选与下载功能。可用模态以各仓库元数据为准。项目规划规模与此处显示的已发布数据统计有所区别。',
 'Download counts come from Hugging Face.':'下载量来自 Hugging Face。','Copied to clipboard.':'已复制到剪贴板。','Copy failed. Please select and copy the command manually.':'复制失败，请手动选择并复制命令。','Loading dataset details…':'正在加载数据集详情…','Ready to play.':'可以播放。','Video loads on demand. If access is restricted or the codec is unsupported, open the dataset on its source platform.':'视频按需加载。如访问受限或不支持该编码，请前往来源平台查看。','Video failed to load. Check your connection and access permissions, or open the dataset on its source platform.':'视频加载失败，请检查网络和访问权限，或前往来源平台查看。','No browser video preview is available for this dataset.':'此数据集暂无浏览器视频预览。','Sensor metadata':'传感器元数据','Episodes':'片段数','Duration':'时长','Size (metadata)':'大小（元数据）','License':'许可证','Updated':'更新时间','First episode from the dataset. Sensor streams retain their independent sampling rates.':'展示数据集的首个片段，各传感器流保留独立采样率。',
 'Commands use the HumanCOIN download tool. JSON saves your selection for import into this portal.':'命令使用 HumanCOIN 下载工具。JSON 可保存选择，供下次导入本门户。',
 'Download to ./data/HumanCOIN/ with the selected revision for each repository.':'按各仓库所选版本下载至 ./data/HumanCOIN/。',
 'Restricted repositories require platform access and authentication. Commit revisions pin content; main/master are mutable branches. Sizes come from metadata; HF downloads are platform statistics.':'受限仓库需要平台权限与身份认证。提交版本可固定内容；main/master 分支可能更新。大小来自元数据，HF 下载量为平台统计。',
 'The download tool supports --hub, --datasets, --revision, --target-dir, --max-workers and --dry-run. Add --dry-run to check destination paths. Use Python 3.10–3.13. Authenticate with HF_TOKEN for Hugging Face, or MODELSCOPE_TOKEN / MS_TOKEN for ModelScope.':'下载工具支持 --hub、--datasets、--revision、--target-dir、--max-workers 和 --dry-run。可添加 --dry-run 检查目标路径。请使用 Python 3.10–3.13。Hugging Face 使用 HF_TOKEN 认证；ModelScope 使用 MODELSCOPE_TOKEN 或 MS_TOKEN。',
 'Unavailable statistics appear as —. Repositories with the same ID on both platforms share one catalog entry. Download commands are available only for platforms that host the selected repositories.':'缺失统计显示为 —。两个平台上 ID 相同的仓库合并为一条目录记录。只能为实际托管所选仓库的平台生成下载命令。',
 'Catalog refreshed.':'数据目录已刷新。','A new snapshot is ready.':'有新的数据目录可用。','Preparing the new snapshot…':'正在准备新数据目录…','Loading catalog summary…':'正在加载目录概况…','Catalog loading failed':'目录加载失败','No published datasets are available yet.':'暂无已发布数据集。','Choose a data level to browse, or select All levels.':'请选择数据等级，或选择全部等级。','Scope loading failed. Any list below belongs to the previous completed query.':'加载失败，下方保留的是上次成功查询的结果。',

};
export function translate(text){
 if(translations[text])return translations[text];
 const patterns=[[/^Showing (.*?) of ([\d,]+)$/,(_,a,b)=>`共 ${b} 个，显示 ${a}`],[/^(.*) complete dataset\(s\) · (.*)$/,(_,n,h)=>`${n} 个完整数据集 · ${h}`],[/^Showing (.*?) of (.*?) datasets$/,(_,a,b)=>`显示 ${b} 个数据集中的 ${a}`],[/^Loading selected indexes: (\d+) of (\d+) files$/,(_,a,b)=>`正在加载索引：${a} / ${b} 个文件`],[/^Page (\d+) of (\d+)$/,(_,a,b)=>`第 ${a} / ${b} 页`],[/^(\d[\d,]*) datasets?$/,(_,n)=>`${n} 个数据集`],[/^(\d+) modality filters$/,(_,n)=>`${n} 个模态筛选条件`],[/^Showing 100 of ([\d,]+) tasks\. Refine your search\.$/,(_,n)=>`显示 ${n} 个任务中的前 100 个，请细化搜索。`],[/^Episodes: (.*?) · Duration: (.*)$/,(_,a,b)=>`片段数：${a} · 时长：${b}`]];
 for(const [re,fn] of patterns)if(re.test(text))return text.replace(re,fn);
 return text;
}
export function setupLanguage(){
 const pageTitle=document.title;
 let language;try{language=localStorage.getItem('humancoin.language');}catch{}
 language=new URL(location.href).searchParams.get('lang')||language||'en';language=language==='zh'?'zh':'en';
 const originals=new WeakMap(),attributes=new WeakMap();
 const protectedSelector='pre,code,[data-content-language],.dataset-title,.dataset-id,.desc,.stream,.previewtag,#selectionItems,.sensorline b,.detailcell b,.metricval';
 const isProtected=node=>node.parentElement?.closest(protectedSelector)||node.parentElement?.closest('option')&&!node.parentElement.closest('#sort')&&node.parentElement.value!=='';
 function apply(){
  document.documentElement.lang=language==='zh'?'zh-CN':'en';
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let node;
  while((node=walker.nextNode())){
   if(isProtected(node)||node.parentElement.closest('script,style,#languageSwitch'))continue;
   const cached=originals.get(node);let original=cached&&node.nodeValue===cached.output?cached.original:node.nodeValue;
   const value=language==='zh'?original.replace(/\S[\s\S]*\S|\S/,s=>translate(s)):original;
   originals.set(node,{original,output:value});if(node.nodeValue!==value)node.nodeValue=value;
  }
  document.querySelectorAll('[placeholder],[title],[aria-label]').forEach(element=>{
   if(element.closest(protectedSelector)||element.closest('.dataset'))return;
   const cache=attributes.get(element)||{};
   for(const name of ['placeholder','title','aria-label'])if(element.hasAttribute(name)){
    const value=element.getAttribute(name),prior=cache[name],original=prior&&value===prior.output?prior.original:value,output=language==='zh'?translate(original):original;
    cache[name]={original,output};if(value!==output)element.setAttribute(name,output);
   }attributes.set(element,cache);
  });
  const buttonLabel=language==='zh'?'English':'中文';if(button.textContent!==buttonLabel)button.textContent=buttonLabel;button.setAttribute('aria-label',language==='zh'?'Switch to English':'切换到中文');
  document.title=language==='zh'?translate(pageTitle):pageTitle;
 }
 const button=document.getElementById('languageSwitch');
 button.onclick=()=>{language=language==='zh'?'en':'zh';try{localStorage.setItem('humancoin.language',language);}catch{}const url=new URL(location.href);url.searchParams.set('lang',language);history.replaceState(null,'',url);apply();};
 apply();let pending=false;new MutationObserver(()=>{if(!pending){pending=true;queueMicrotask(()=>{pending=false;observerRun();});}}).observe(document.body,{childList:true,subtree:true,characterData:true});
 function observerRun(){apply();}
}
