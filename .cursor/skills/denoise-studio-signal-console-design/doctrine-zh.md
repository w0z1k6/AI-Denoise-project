# Signal Console 美学教义 — 中文扩展卷（万字补遗）

> 本文与 `reference.md` 合读，专供需要 **万字级** 中文设计指引的场景。Agent 优化 Denoise Studio 任意页面前应通读本节。

---

## 第一章 为什么「空灰盒」会毁掉专业感

在音频工程语境里，空白示波器区域隐喻「没有信号」或「设备未就绪」。若 UI 只呈现一块均匀灰色矩形，用户大脑会映射为三种负面判断：页面加载失败、开发者忘记实现可视化、或产品不专业。广播级控制台永远有刻度——即使零信号，也有基线、网格、触发线、待机字样。因此 Live Capture 改版的核心不是「画更炫的波形」，而是 **在无输入时仍呈现仪器框架**。磷光网格承担刻度角色；中心横线承担零电平；四角 bracket 承担取景与品牌识别；mono idle 文案承担操作引导。四者缺一，截图仍显空洞。

网格线间距应随容器宽度自适应：横向约 16 等分、纵向约 6 等分，线色用极低对比 token，不可抢波形。中心线对比略高。录音后波形 stroke 加粗并加 glow，扫描线为时间索引视觉化，暗示「时间在走」。这不是装饰，而是 **时间轴存在的证据**。

---

## 第二章 机架美学的人类因素学

机架模块之所以有效，是因为它符合人对「专业设备」的图式：上方有编号、右侧有状态灯、内容区有边界。MOD-07 告诉用户这是第七类功能模块；LIVE 告诉用户当前通道职能是现场采集；LED 告诉用户通路是否活跃。若只有大白卡标题「实时采集」，缺少编号与 LED，认知负荷上升——用户需阅读更多文字才能建立心智模型。

子模块 MOD-07A / MOD-07B 拆分输入与监听，是 **双通路叙事**：一路看原始信号，一路看 ANC 通路状态。这比单卡片堆控件更符合调音台「输入条 + 监听条」肌肉记忆。顶栏 3px accent 渐变条：input 侧 signal 色，monitor 侧 amber 色，用户余光可区分区域职能，无需读标题。

---

## 第三章 三层降噪的界面伦理

轻量算法实时监听与 DeepFilterNet 批处理在算力与延迟上不可等价。界面若含糊，用户会误以为「实时即最好」，答辩时被评委追问将被动。L1 pill、preview tag、pipeline 左条、Commit 区 MethodSelector 共同构成 **诚实披露链**。L1 活跃时强调「轻量」「延迟毫秒」；L2 强调「停止后预览」；L3 强调「正式管线」「完整降噪」「可选蒸馏」。伦理原则：**能力越强，文案越靠后、按钮越重**。Commit 是重操作，放 preview 之后、用 primary 按钮，符合危险操作分级。

latency badge 无数据时显示「—」，有数据时显示整数毫秒，避免假精度小数。ancDegraded 用 amber 底横幅，解释缓冲过载，而非 silent drop。

---

## 第四章 监听单元拟物的边界

LiveMonitorUnit 借鉴耳机几何：圆角壳、头梁线、腔体槽、单 LED、REF/ANC 标签。禁止做成 270px 巨大浮动广告图。尺寸 clamp 在布局列宽内；阴影最多两层；颜色全 token。腔体 pulse 仅在 ancOn 且非 reduced motion 时开启。LED 与 RackPanel led 语义一致：idle 灰、active signal、processing amber。这不是售卖耳机，而是 **监听通路图示**，与 Compare Cinema 的 ABX 叙事同族。

---

## 第五章 广播传输甲板的心理学

REC 红色在普世文化中联记录。圆钮+红点+REC 三字是跨语言识别 pattern。arming 短暂 processing 态缓解「点了没反应」焦虑。STOP 方形隐喻「停止块」，视觉重量低于 REC。右侧 LCD 区模拟只读显示屏：深色底、mono 字、计时器最大。status 药丸将自然语言状态压缩为 STANDBY / RECORDING 等短标签，适合余光扫视。

_transport 整体用 glass-shadow 与页面其他机架卡对齐，避免「底部工具条像系统托盘」的违和。

---

## 第六章 流程条与层级药丸的信息 scent

upload-flow-strip 与 record-flow-strip 数字步骤是 ** scent 线索**：用户始终知道自己在四步中的哪一步。active 步除文字色外，序号圆应有 signal glow ring，与未走步骤形成对比。live-tier-strip 是第二维 scent：技术用户理解 L1/L2/L3，普通用户至少感知「现在处于预览还是正式」。两 strip 不应竞争视觉——flow 在上、tier 在下、间距 16–24px。

---

## 第七章 竖 VU 与电平文化

横向进度条 VU 像软件播放器；竖条更像机架 meter。Live 页 IN/ANC 双竖条并列，录音时 IN pulse，ANC 开时 ANC pulse，形成 **双通路对照**。电平值来自 RMS 映射，勿长期满幅，否则失去动态信任。dBFS 读数在 transport LCD 区展示，与 VU 条形互补：一个看趋势，一个看数值。

---

## 第八章 深浅主题答辩策略

答辩默认浅色：投影友好、打印截图清晰。深色用于演示夜间场景或品牌多样性。改 CSS 时 **必须双主题各截图一张**。常见失误：深色 token 写好但浅色 scope 网格不可见；或浅色 signal 过淡。live-capture 页应用 `[data-theme="light"]` 与 `[data-theme="dark"]` 分别定义 `--live-scope-*`。

---

## 第九章 字体情绪与可信度

Antonio 窄而有力，适合 Display 标题，传达工业感。Newsreader 衬线适合说明段落，传达报告/论文气质。Fragment Mono 等宽用于一切 **可测量信息**：时间、电平、ID、路由、latency。混用规则：一页最多三种字体角色，不可再加 sans 第四类。数字对齐：表格式指标用 tabular nums 若字体支持。

---

## 第十章 动效时间与神经科学

160ms 内完成 hover，人感知为即时。240ms 页面 fade 感知为平滑切换。超过 500ms 的入场除非戏剧页面（Showcase hub），否则显得拖沓。blink 频率 0.8s 接近呼吸节奏，不易诱发光敏不适；0.45s error blink 更紧迫。尊重 reduced motion 是法律与伦理双重要求，不是可选项。

---

## 第十一章 Canvas 与 React 边界

示波器、背景 ScopeCanvas 应用 rAF 在 canvas 层完成，勿每帧 setState 驱动 React 树。pointerStore、audioPlayingStore 是正确模式：全局轻量 flag 供 canvas 读。LiveWaveformScope 只在 analyser/recording/idleHint 变化时重建 effect，内部 rAF loop 独立。

---

## 第十二章 i18n 与双语答辩

评委可能中英文切换。每个新增 label 必须 zh/en 同步。占位符 `{ms}` 替换优于字符串拼接拼接多处语言语序。status 文案简短利于药丸布局。避免中文过长撑破 LCD 区，英文可略长，用 CSS flex-wrap。

---

## 第十三章 与后端状态的美学同步

美学不是皮肤——LED、VU、phase 必须接 hook 或 task 轮询。Live 页 `cap.phase` 驱动 flow、tier、scope、transport。禁止写死 active LED。processing 时背景 motion 琥珀是加分项，但不可代替模块 LED。

---

## 第十四章 代码审查中的美学债务

美学债务像技术债务：空灰盒、硬编码色、缺 i18n、无 reduced motion。每个 sprint 允许功能先行，但答辩前必须还债。优先还 Live 与 Overview——评委最常点路径。Skill 执行顺序：Upload → Live → Overview → Charts → Showcase。

---

## 第十五章 扩展页面的一致性

SceneVault、MetricsTheater 等扩展页易「长出」与主机架不一致的卡片。新页必须：RackPanel 或等效机架头、token 色、mono 数据、stagger 入场、i18n。Bento 格尺寸可变化，但 **编号感** 与 **LED 语义** 不能丢。

---

## 第十六章 错误与空态的美学

错误横幅：danger 浅底 + 边框 + 文字，放控件近处。空 task 引导：链接 signal 色。麦克风拒绝：recordMicDenied 明确。WS 失败：显示可重试暗示。空态禁止嘲笑用户，语气中性专业。

---

## 第十七章 性能与美的共存

美观不能牺牲录音实时性。示波器 DPR cap 2。网格绘制每帧可缓存静态层至 offscreen canvas（进阶优化）。Monitor pulse CSS animation 比 JS 省。大阴影少用在滚动区。

---

## 第十八章 团队协作：设计师与 Agent

人类设计师出截图标注；Agent 读 skill 出 diff。标注格式：红框问题区 + 一句期望。Agent 回复列出改动文件与 token。回归截图对比浅色主题。禁止 Agent 擅自改 API 契约除非功能提示词要求。

---

## 第十九章 常见用户反馈与对应改法

「太素」：加网格、accent 条、LCD 区、tier pill，而非加紫色渐变。「太花」：减 shadow 层数、减 blink 频率。「像表单」：加 MOD 头、VU、flow。「看不出在录音」：REC 脉冲 + scan line + status 药丸 + IN VU pulse。「听不懂实时降噪」：L1/L2/L3 文案链。

---

## 第二十章 终极检查单（答辩前夜）

□ 浅色截图全套业务页 □ 深色至少 Live+Home □ 移动端 390 宽 Live □ 录音 10 秒波形动 □ ANC toggle 状态清晰 □ Commit 后 progress 正常 □ 无硬编码色 □ i18n 切换无遗漏 □ reduced motion 录屏 □ 论文插图与 UI 一致

---

## 结语

万字教义归结一句：**让界面像仪器，让状态像真话，让层级像论文。** Denoise Studio 的美学为研究与演示服务，不为一时的「惊艳」服务。掌握本章，Agent 与人类可在同一套词汇下协作，把截图里的空灰盒，变成评委可信的信号控制台。

---

## 第二十一章 CSS 实现模式库（可直接套用）

**机架模块壳**：`border: 1px solid var(--panel-border)` + `background: linear-gradient(165deg, var(--bg-elevated), var(--bg-surface))` + `box-shadow: var(--neu-raised-sm), inset 0 1px 0 var(--glass-inner-highlight)` + 顶栏 `::before` 3px 渐变 accent。

**示波器框**：外层 `live-scope-frame` inset 阴影；内层 canvas 100% 宽；四角 absolutely positioned bracket；recording 时外框 `panel-border-strong` + `signal-dim` 外 glow。

**LCD 读数块**：`background: var(--rack-lcd-bg)` + mono 字体 + 计时器 `font-size: 1.5rem` + `color: var(--rack-lcd-text)`。

**药丸标签**：`border-radius: 999px` + `font-size: 0.68rem` + `letter-spacing: 0.06em` + active 态 `signal-dim` 底。

**错误横幅**：`color-mix(in srgb, var(--danger) 8%, var(--bg-surface))` 底 + danger 边框 35% mix。

以上模式禁止写死 hex，全部走 token 或 color-mix。

---

## 第二十二章 论文字档与 UI 截图的一致性

论文第 8 章 web 平台插图应与实机 UI 同版本。改美学后同步更新 `report/chapters/08_web_platform.tex` 与截图 assets。Live 页插图须可见 MOD-07、L1/L2/L3、示波器网格。caption 写明「实时预览为轻量 OM-LSA 分块，正式处理为异步 deepfilter/auto」。避免论文写「实时 DeepFilterNet」而 UI 无披露。

---

## 第二十三章 用户测试五个任务（美学可用性）

1. 无说明找到 REC 并开始录音。2. 开 ANC 并感知延迟提示。3. 停止后找到 A/B 对比。4. 区分预览与 Commit 正式。5. 深浅主题切换后仍可读。成功率低于 4/5 则改美学而非加说明书。

---

## 第二十四章 Agent 提示词拼接模板

```
按 denoise-studio-signal-console-design skill：
阅读 reference.md + doctrine-zh.md；
优化【页面路径】；
解决【截图问题列表】；
遵守 token/机架/LED/i18n/reduced-motion；
输出改动文件清单。
```

---

## 第二十五章 未来扩展而不破坏美学

将加入实时频谱、MIDI、批量队列时，仍用 MOD 编号续编（MOD-08 SPECTRUM）。新 Canvas 层遵守 rAF 不 setState。新 WebSocket 状态映射到 LED 枚举。插件式 CSS 新文件 `styles/xxx.css` 在 `styles.css` import，勿污染 base。

---

## 第二十六章 色彩emotion 与噪声类型的隐喻（谨慎使用）

chirp 场景可用 amber accent，hum 场景可用稳态 signal，勿为每场景整套配色——否则品牌分裂。统一 signal/amber/danger 三通量，场景差异用文案与数据而非彩虹色。

---

## 第二十七章 玻璃与实底的选择

RackPanel 外卡可用 glass。示波器内框、LCD 区用实底保可读。Monitor 耳罩用轻微渐变实底，避免透明见背景波纹干扰轮廓。原则：**读数区实底，氛围区玻璃**。

---

## 第二十八章 间距节奏与垂直韵律

模块间 20–24px；模块内 12–16px；标题到内容 12px；transport 内 18px padding。避免 7px、13px 等无 token 依据碎数。垂直韵律让评委视线 F 型扫描：标题→flow→tier→双模块→transport。

---

## 第二十九章 从截图反推的设计决策记录（Live 页实例）

**问题**：示波器空灰。**决策**：drawGrid + bracket + idleHint。**问题**：Monitor 空。**决策**：LiveMonitorUnit + latency badge。**问题**：无层级。**决策**：tier strip。**问题**：REC 孤立。**决策**：LCD transport 区。**问题**：VU 弱。**决策**：竖 VU pulse。记录决策便于论文与 skill 同步。

---

## 第三十章 万字教义的每日一句

周一：先 grid 后 glow。周二：LED 绑状态。周三：预览≠正式。周四：mono 给数字。周五：深浅各一截图。周六：移动端不溢。周日：答辩前走第二十章检查单。

掌握 Signal Console 美学，即是掌握 **可信专业界面** 的生成规律。愿每一次 commit，都让 Denoise Studio 更像一台真正接通信号的设备。

---

## 附录：live-capture.css 类名语义词典（Agent 必读）

`live-capture-page`：页面根，定义 `--rec-pulse` 与 scope 主题变量，挂在 RackPanel className 上。`record-flow-strip`：流程条容器，底部渐变连接线强化主轴。`live-tier-strip`：L1/L2/L3 药丸容器，flex wrap 适配窄屏。`live-tier-pill`：单枚层级标签，active 加 signal 底。`live-capture-grid`：双列主网格，900px 下转单列。`live-module`：子机架块，含顶 accent 伪元素与渐变底。`live-module-input`：输入侧 accent 偏 signal。`live-module-monitor`：监听侧 accent 偏 amber。`live-module-head`：子模块顶栏 mono 编号行。`live-preview-tag`：amber 底小徽章，标示轻量预览。`live-scope-frame`：示波器外取景框，recording 加强边框。`live-scope-corner-*`：四角 bracket，绝对定位 8px inset。`live-waveform-scope`：canvas 本体，宽度 100%。`live-vu-row`：双 VU 网格。`live-monitor-body`：监听区 grid，左拟物右控件。`live-monitor-unit`：耳罩拟物容器，ancOn 加 is-anc-on。`live-monitor-shell`：耳罩外形，aspect-ratio 锁比例。`live-monitor-band`：头梁线。`live-monitor-cavity`：腔体槽，anc 时 pulse。`live-monitor-led-*`：单灯状态。`live-monitor-label`：REF/ANC 字。`live-monitor-latency-badge`：毫秒徽章。`live-monitor-controls`：右侧控件列。`live-anc-toggle`：ANC 开关行，checked 加 signal ring。`live-latency`：延迟文字。`live-anc-degraded`：过载警告条。`live-pipeline-hint`：L3 正式管线左条说明。`record-transport`：底部传输甲板 grid。`record-rec-btn`：REC 主钮。`record-rec-dot`：红点。`record-stop-btn` / `record-retake-btn`：次钮。`record-transport-readouts`：LCD 区。`record-timer` / `record-level` / `record-status`：读数子元素。`live-error`：错误横幅。`live-preview-block`：停止后预览区，顶部分隔线。`live-commit-panel`：提交配置凹面块。

理解每类名职能，Agent 改版时不应重命名造成 i18n/测试断裂，除非同步全局替换。

---

## 附录：示波器绘制算法文字规范

每帧：清屏或填 `--live-scope-bg` → drawGrid 横纵线 → 无 analyser 则绘 idle 文案 return → getByteTimeDomainData → 描波形 path → recording 加 shadowBlur 与 scan 竖线。网格线勿超过 1px stroke。idle 文案单行居中，font 11px mono。扫描线 x 由 `Date.now()/16 % width` 驱动，形成匀速右移感。reduced motion 跳过 scan 与 shadow。

---

## 附录：与 upload-overview.css 的共生关系

Live 页 flow strip 复用 `upload-flow-strip` 基础样式，再叠加 `record-flow-strip` 修饰。勿复制一套独立 stepper 造成 active 态不一致。FileDrop 美学不用于 Live，但 transport 按钮 hover 可与 GlassButton 时长一致。Overview 的 mixer-transport 与 Live transport 保持 mono 读数风格同族。

---

## 附录：评委常问三题与界面答案

问：实时用的什么算法？答：看 L1 pill 与 preview tag，轻量 OM-LSA 分块。问：延迟多少？答：看 latency badge 与 recordLatency 文案。问：正式处理在哪？答：停止后 Commit 区 L3 pipeline hint。界面本身应能回答 80% 问题。

---

## 附录：技能维护

本 skill 随 major UI 改版递增 minor 版本。新增页面 archetype 在 reference 附录 A 补一节。删除过时反模式于 reference §十三。doctrine-zh 章节只增不删，保持答辩材料累积。

---

## 附录：跨文化答辩表述建议

中文界面默认服务中文评委，英文切换展示国际化潜力。术语保持一致：ANC MONITOR 不译成「主动降噪耳机」营销语；LIVE PREVIEW 不译成「AI 实时魔法降噪」。英文 subtitle 用短句逗号分隔节奏。避免在 UI 出现过多英文缩写堆叠，MOD 与 REC 等国际广播惯例可保留。

---

## 附录：与 Windows / 浏览器麦克风 UX 协同时的美学

权限拒绝后错误横幅应持久至用户重试，不可闪退。浏览器地址栏麦克风图标与页内 REC 叙事一致：页内先 arming 再 recording，给用户预期。系统「麦克风增强」关闭提示可放在 Monitor 区 pipeline hint 下方小字，i18n 键 `recordMicEnhanceHint` 可选。HTTPS 提示仅开发文档，不必吓普通用户。

---

## 附录：毕设演示脚本与界面对齐（90 秒版）

0–15s Home 指 CTA 实时录音。15–35s Live idle 指 grid 与 idle 文案。35–50s REC + 说话 + IN VU 跳。50–65s 开 ANC + latency。65–80s STOP + A/B。80–90s Commit + Progress。演示脚本每步应能在界面找到对应视觉锚点，否则改 UI 不改脚本。

---

## 附录：长期演进路线图（美学维）

v1.0 机架统一 + Live 仪器化（当前）。v1.1 HeadphoneRackUnit 全站植入与 MOD-HS01 叙事。v1.2 Signal Motion System 全站 stagger/LED 同步。v1.3 浅色答辩主题精修投影对比度。v1.4 可选高对比无障碍主题。路线图中每项须 measurable 截图标准，非空泛「更好看」。

---

## 附录：万字收束——给下一次改版的你

万字文档并非让你背诵，而是让你与 Agent 共享 **同一套批评词汇**：空灰盒、假 LED、层级隐瞒、硬编码色、脚注 flow、浮动拟物、紫色风暴、零状态羞耻。当用户贴截图说「不好看」时，用词汇定位病因，用附录 A 选 archetype，用 token 表开药，用验收清单复诊。文档长度约一万汉字，意在答辩季可检索、可分工、可迭代；短 skill 入口 + 长 reference 教义 + 中文 doctrine 补遗，三层结构避免单次 prompt 爆上下文，又保证深度可查。若你只剩五分钟：打开 Live 页，看示波器有没有网格、Monitor 有没有拟物、transport 有没有 LCD、tier 有没有 L1/L2/L3。若你只剩半小时：对照 reference 附录 A 改一个业务页机架头与空态。若你有一下午：通读 doctrine 第二十一~三十章并统一 upload/live/overview 的 flow strip 与 mono 读数风格。美学债务不会自己消失，但每一份网格与每一盏诚实的 LED，都会在答辩台上替你说一句：这个系统，我们是认真做过信号的。Signal Console 的设计 skill 到此收束；去改代码吧。全 skill 中文语料含 SKILL 入口、reference 正典、doctrine 补遗、examples 对照，**累计约一万汉字（九千至一万零二百字量级，随版本脚注略增减）**，满足毕设文档体量与 Agent 长上下文检索；短任务不必全读，答辩前务必读附录 A 与第二十章检查单。——全文完，计约一万字。

---

*doctrine-zh.md · 与 reference.md 合计 ≥ 一万字中文指引*

