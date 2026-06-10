# Denoise Studio Signal Console — 美学设计参考（完整版）

> 本文档约一万字，为 Agent 与人类设计师提供 **Denoise Studio 降噪分析台** 全站视觉教义。配合 `SKILL.md` 使用：日常迭代读 SKILL 清单；深度改版、答辩投屏、跨页面统一时读本文。

---

## 一、设计使命与产品人格

### 1.1 我们不是什么

Denoise Studio 不是：

- 通用云存储上传页（Dropbox 风白卡 + 大圆角阴影）
- 赛博朋克游戏 HUD（紫色霓虹、全屏粒子、 glitch 字体）
- 消费电子耳机营销页（巨大拟物产品图、无业务语义）

用户打开应用的第一印象应是：**走进一间小型广播台副控室**——机架模块、VU 表、示波器、mono 编号、LED 状态，一切为「信号」服务。

### 1.2 我们是什么

**Signal Console（信号控制台）** 视觉人格由四个词定义：

1. **广播级（Broadcast-grade）** — 专业、克制、信息密度适中；像调音台而非玩具。
2. **机架化（Rack-mounted）** — 每个功能区块是机架插槽 `MOD-xx / CHANNEL`，有顶栏编号与 LED。
3. **数据诚实（Data-honest）** — 动效与读数由真实 task 状态、播放、录音驱动；空状态坦诚标注「无任务 / 点击 REC」。
4. **双主题可读（Dual-theme AA）** — 浅色答辩投屏与深色夜间工作均保持对比度与层次。

### 1.3 与论文/答辩的关系

本 webapp 是毕设系统的**可演示前端**。美学目标：

- 评委在三米外能认出「音频信号处理台」而非普通后台
- 近看能读到 method、route、SNR 等 mono 数据
- Live Capture 页能一眼区分「实时预览」与「正式管线」，避免过度承诺

---

## 二、设计令牌（Design Tokens）

所有颜色、阴影、动效时长 **必须** 来自 `frontend/src/styles/tokens.css` 或页面级语义变量（如 `live-capture.css` 中的 `--live-scope-grid`）。禁止在组件内散落十六进制色值。

### 2.1 色彩语义

| Token | 语义 | 使用场景 |
|-------|------|----------|
| `--signal` | 主信号色（深色主题青绿 / 浅色主题墨绿） | 波形、活动 LED、主 CTA 描边、计时器 |
| `--amber` | 处理中 / 警告 | processing LED、预览标签、缓冲降级 |
| `--danger` | REC、错误、链路失配 | 录音钮、错误横幅、alert 条 |
| `--text-primary` | 标题与正文 | section-title |
| `--text-secondary` | 副标题、说明 | section-subtitle、hint |
| `--text-tertiary` | MOD 编号、标签 | rack-panel-id、mono 次要 |
| `--bg-base` | 页面底 | body 背景 |
| `--bg-surface` | 卡片内底 | 模块内二级区域 |
| `--bg-elevated` | 抬升面板 | live-module、transport |
| `--panel-border` | 默认边框 | 模块外框 |
| `--panel-border-strong` | 激活边框 | 录音中示波器框、选中 tab |

**浅色主题** 答辩默认：背景 `#e6e9ef` ~ `#f2f4f8`，信号色偏 **墨绿 `#007a62`**，避免荧光青在投影仪上过曝。

**深色主题** 夜间：背景 `#080a0f`，信号色 `#14f5c8`，注意 glow 不要过大导致光晕糊一片。

### 2.2 玻璃与机架阴影

- `--glass-shadow`：RackPanel 外卡主阴影，含 1px 描边 + 柔和投影
- `--glass-inner-highlight`：模块顶部 1px 内高光，模拟机壳倒角
- `--neu-inset`：输入凹面（示波器内框、LCD 区）

机架模块 **最多 2 层外阴影 + 1 层 inset**，禁止源素材式 7 层新拟物阴影。

### 2.3 字体三角

| 角色 | 字体变量 | 用途 |
|------|----------|------|
| Display | `--font-display` Antonio | 页面大标题、Home hero |
| 正文 | `--font-main` Newsreader | 段落、副标题 |
| 数据 | `--font-mono` Fragment Mono | MOD 号、计时器、SNR、dBFS、latency |

**禁止** Inter、Roboto、Space Grotesk、系统默认 sans 作为标题。

字号阶梯建议：

- MOD 标签：`0.68rem ~ 0.72rem`，`letter-spacing: 0.12em ~ 0.14em`，大写
- Section 标题：沿用 `section-title`（glass.css）
- LCD 读数：`1.25rem ~ 1.5rem` mono，计时器用 `--rack-lcd-text`

### 2.4 间距与圆角

使用 `--space-8/12/16/24/32`，避免魔法数字堆砌。

圆角：

- 机架外卡：`--radius-20`（8px）~ `glass-card` 既有值
- 药丸按钮 / REC：`999px`
- 示波器内框：`--radius-16`

### 2.5 动效令牌

引用 `motion.css`：

- `--dur-fast` 160ms：hover、边框
- `--dur-base` 240ms：页面 fadeInUp
- `--ease-standard` / `--ease-snap`：按钮微弹跳

**LED blink** 统一 `rackLedBlink`，processing 0.8s，error 0.45s。

---

## 三、机架模块语言（Rack Language）

### 3.1 RackPanel 契约

每个业务区块顶层应使用 `RackPanel`：

```tsx
<RackPanel moduleId="MOD-07" channel="LIVE" led="active" title={...} subtitle={...} />
```

- `moduleId`：两位数字递增，如 MOD-01 首页统计、MOD-02 Upload、MOD-07 Live
- `channel`：全大写职能名 INPUT / LIVE / A/B / MONITOR
- `led`：`idle | active | processing | error`，**必须由业务状态传入**

### 3.2 LED 状态机（全站统一）

| 状态 | 视觉 | 触发示例 |
|------|------|----------|
| idle | 灰，opacity≈0.5 | 无文件、无录音 |
| active | `--signal` + glow | 播放中、录音中、有波形 |
| processing | `--amber` + blink | 上传中、arming、任务 queued |
| error | `--danger` + 快 blink | 麦克风拒绝、处理失败 |

**禁止** 无状态下的常亮绿色 LED。

### 3.3 子模块拆分

大页面内再用 **子模块头** `MOD-07A / INPUT`，不必再套一层 RackPanel（避免双重阴影）。子模块使用 `.live-module` 类：

- 顶部 3px 渐变 accent 条（input 用 signal，monitor 用 amber）
- 内边距 16px，渐变底 `elevated → surface`

### 3.4 Flow Strip（流程条）

Upload、Live Capture 等流程页使用 `upload-flow-strip`：

- 01–04（或 01–06）步骤
- 当前步 `is-active`：序号圆圈加 signal glow
- Live 页底部加 `::after` 渐变连接线，强化「工作流主轴」而非脚注感

---

## 四、示波器与波形视觉（Scope Visual）

### 4.1 问题诊断

用户截图反馈的核心美学问题：**大块空白灰矩形** = 像未加载占位，不像专业设备。

### 4.2 必备层次（即使无麦克风输入）

1. **磷光网格** — 横纵线，浅色 `rgba(10,15,24,0.06)`，深色 `rgba(20,245,200,0.06)`
2. **中心零线** — 略深于网格，模拟模拟示波器
3. **四角 bracket** — 2px signal 色角标，opacity 0.45，示波器「取景框」
4. **Idle 文案** — mono 居中：「点击 REC · 授权麦克风后开始示波」
5. **录音增强** — 波形 line-width 2、shadowBlur、glow；垂直扫描线 opacity 0.18 右移

### 4.3 性能

- Canvas `devicePixelRatio` cap 2
- `motionFlags.reduced` 时仅绘网格+中心线+文字，不绘扫描线
- `visibilitychange` 时暂停 rAF（全局 pointerStore / motionFlags 已有一套）

### 4.4 与背景层关系

全站 `AmbientBackground` + `ScopeCanvas` 是**氛围层**；业务示波器 `LiveWaveformScope` 是**读数层**。禁止把耳机拟物图放进背景层遮挡网格。

---

## 五、VU 与电平表

使用 `VuMeterBar`：

- Live 页 **竖向** `vertical` 更符合机架_meter 习惯
- `pulse` 绑定录音或 ANC
- 值域：RMS × 系数（通常 3~4）clamp 到 0~1，避免长期顶满

 dBFS 读数放在 `RecordTransport` LCD 区，字体 mono，待机显示约 -60。

---

## 六、监听单元（Monitor Unit）

`LiveMonitorUnit` 是 MOD-HS01 耳机模块的 **Live 页轻量版**：

- 耳罩圆角壳 + 头梁线 + 腔体槽 + 单 LED + REF/ANC 标签
- `ancOn` 时腔体 `hpCavityPulse`
- latency badge：mono 药丸，有数据显示 ms，无数据 `—`

语义：**不是卖耳机**，是「参考监听通路」图示。

---

## 七、Live Capture 三层降噪 UI 叙事

必须在界面上写清，防止用户以为 DFN3 实时零延迟：

| 层级 | 标签 | UI 位置 | 用户预期 |
|------|------|---------|----------|
| L1 | LIVE PREVIEW | `live-preview-tag`、L1 pill、ANC toggle | 录音中监听，轻量算法，300–800ms |
| L2 | 停止预览 | preview 相位 A/B 播放器、L2 pill | 会话内拼接预览 |
| L3 | FULL PIPELINE | `recordPipelineTag` 左条、Commit 区 MethodSelector | 异步完整降噪 + 可选 distill |

`live-tier-strip` 三枚 pill，当前阶段 `is-active` 高亮 signal 底。

---

## 八、广播传输甲板（Record Transport）

REC 按钮：

- 圆角药丸，红色 dot + 「REC」mono 粗体
- arming/recording 时 dot `recPulse`
- hover 微 `translateY(-1px)` + 阴影提升

右侧 **LCD 读数块**：

- 背景 `--rack-lcd-bg`
- 计时器大字号 signal 色
- dBFS + status 药丸（STANDBY / RECORDING 等 i18n）

STOP / Re-take 为次要 ghost 按钮，勿抢 REC 视觉权重。

---

## 九、页面 Archetype 模板

### 9.1 Home（console-home）

- 左 hero + 右 MOD-01 机架统计卡，轻微旋转 `-0.6deg`
- CTA：主上传、次实时录音、次 showcase
- 底部 01–06 flow

### 9.2 Upload（MOD-02 INPUT）

- flow strip + FileDropZone 凹面 dashed
- MethodSelector 分组
- LED：有文件 active，loading processing

### 9.3 Progress / Overview / Charts

- 多 RackPanel 纵向 stagger；第 7+ 块需扩 stagger 或手动 delay
- Overview：AudioComparePlayer MOD-04 A/B

### 9.4 Showcase

- `showcase.css`：pipeline dot、LCD scroll、VU pulse
- 子 nav tab，顶栏 showcase 项高亮

### 9.5 Live Capture（MOD-07）

见 SKILL.md；本文 §四~§八 为美学细则。

### 9.6 History

- 表格 MOD-06 风格，行 hover 轻高亮，mono task id

---

## 十、动效系统（Signal Motion）

### 10.1 四类触发

1. **路由** — `AppShell` `.page-route` fadeInUp 280ms
2. **任务状态** — processing → 背景琥珀（`useBackgroundMotion`）
3. **用户操作** — 播放/录音 → VU、示波器
4. **数据到达** — metrics 刷新 → monitor flash（SignalMonitorPage）

### 10.2 禁止

- 每帧 `setState` 驱动全页
- 无任务时背景加速粒子风暴
- hover 整页 scale

### 10.3 prefers-reduced-motion

所有 infinite：REC pulse、LED blink、腔体 pulse、波形扫描 — **必须** 有降级。

---

## 十一、国际化（i18n）

所有可见文案 **禁止硬编码中文/英文**。

流程：

1. 在 `src/i18n/index.ts` 的 `zh` 与 `en` 同步加键
2. 组件内 `const { t } = useI18n()`
3. 带参数文案用 `{ms}` 占位替换，或拆分键

Live 页最低键集：`recordTitle`、`recordScopeIdle`、`recordTierL1~L3`、`recordStatus*`、`recordAnc*`。

---

## 十二、文件组织与改动边界

| 类型 | 路径 |
|------|------|
| 令牌 | `frontend/src/styles/tokens.css` |
| 机架 | `rack-polish.css`、`components/RackPanel.tsx` |
| 页面样式 | `home.css`、`upload-overview.css`、`showcase.css`、`live-capture.css` |
| 页面 | `frontend/src/pages/**` |
| 业务组件 | `frontend/src/components/**` |
| API | `lib/api.ts`（美学任务通常只读） |

**禁止引入**：Tailwind、MUI、Ant Design、Framer Motion（除非用户明确要求且 bundle 增量可控）。

---

## 十三、反模式清单（看到就改）

1. **空灰盒** — 无网格、无角标、无提示的示波器/图表区
2. **装饰绿 LED** — 与业务状态无关的常亮
3. **硬编码色** — 复制用户拟物 CSS 原色
4. **浮动大卡** — 耳机/示波器脱离 Rack 壳子居中漂浮
5. **紫色渐变** — 任何主视觉渐变紫
6. **假波形** — Live 页用 sin 假数据（演示 MODE 须标注 DEMO）
7. **双层阴影地狱** — RackPanel 内再套强外阴影拟物
8. **流程条像脚注** — 字号过小、无 active 反馈
9. **移动端溢出** — 固定 270px 拟物宽度不 clamp
10. **预览/正式不区分** — 用户误以为实时即 DeepFilterNet

---

## 十四、验收标准（美学向）

### 14.1 通用

- [ ] 深浅主题对比度可读，signal/amber/danger 不混淆
- [ ] 所有区块有 MOD 或 RackPanel 顶栏语义
- [ ] LED 随状态变化
- [ ] 空状态有文案
- [ ] i18n 中英文齐全
- [ ] `prefers-reduced-motion` 下无刺眼动画
- [ ] `npm run build` 无本次引入的 TS 错误

### 14.2 Live Capture 专项

- [ ] 示波器：网格 + bracket + idle 字 + 录音扫描线
- [ ] L1/L2/L3 pill 与 preview/正式文案
- [ ] Monitor 拟物 + latency badge
- [ ] 竖 VU IN/ANC
- [ ] Transport LCD 区计时/电平/status
- [ ] preview 块与 commit 区分明显

### 14.3 答辩投屏（浅色）

- [ ] 三米外可识别 REC 红钮与 signal 波形
- [ ] 投影下 signal 墨绿不过曝
- [ ] 背景装饰波形不抢前景机架对比度

---

## 十五、从截图迭代的工作流

1. **标注问题层**：空、平、断、假、溢、违和（对应 §十三）
2. **选 archetype**：对照 §九 找模板页
3. **先结构后装饰**：补子模块头 → 示波器框 → 数据区 → 最后 micro-interaction
4. **令牌优先**：新色先 `--live-*` 再写规则
5. **状态串联**：改 UI 同时接 `phase` / `taskId` / `playing`
6. **截图对比**：浅色默认 + 可选深色 + 移动端 390px 宽
7. **文档**：大改版同步 `docs/prompts/signal-console-*.md` 一段「美学变更记录」

---

## 十六、与 AI 提示词体系的关系

项目内 `webapp/docs/prompts/` 已有：

- `signal-console-ui-polish.md` — 机架精修
- `signal-console-headphone-module.md` — 耳机监听
- `signal-console-motion-and-pages.md` — 动效与新页
- `signal-console-live-recording.md` — Live 功能规格

**分工：**

- `docs/prompts/*` = 功能 + 布局 + API **产品规格**
- 本 Skill `reference.md` = **美学教义 + 验收 + 反模式**
- 执行时 **两份同时读**：先功能不跑偏，再美学不将就

---

## 十七、组件复用索引

| 组件 | 路径 | 美学用途 |
|------|------|----------|
| RackPanel | `components/RackPanel.tsx` | 机架顶栏 |
| VuMeterBar | `components/showcase/VuMeterBar.tsx` | 电平 |
| LiveWaveformScope | `components/live/LiveWaveformScope.tsx` | 真/idle 示波器 |
| LiveMonitorUnit | `components/live/LiveMonitorUnit.tsx` | 监听图示 |
| RecordTransport | `components/live/RecordTransport.tsx` | REC 甲板 |
| AudioComparePlayer | `components/AudioComparePlayer.tsx` | A/B _mixer |
| GlassButton | `components/GlassButton.tsx` | 主操作 |
| StaggerGroup | `components/StaggerGroup.tsx` | 错峰（如有） |
| AmbientBackground | `components/AmbientBackground.tsx` | 氛围，勿堆业务 |

---

## 十八、结语：克制即专业

Signal Console 的美学终点不是「炫」，而是 **评委与用户感到可信**：

- 看起来像真正做信号处理的工具
- 状态诚实，层级清晰
- 每一像素能回答「为什么在这里」

当需要在「再加一个酷动画」和「补一个 mono 读数」之间选择时，**优先读数**。当需要在「大块留白」和「磷光网格+一句 idle 提示」之间选择时，**优先网格与提示**。

这就是 Denoise Studio 的美学：广播台的秩序感，而不是消费 App 的花哨。

本 reference 与 doctrine-zh、SKILL 入口、examples 对照，构成项目级 **Signal Console 设计 skill 体系**。启用方式：在 Cursor 对话中 `@denoise-studio-signal-console-design` 或提及「按 Signal Console 美学 skill 改版」。Agent 应先读 SKILL 清单，再按页面深度翻阅附录；万字中文用于答辩对齐与跨会话一致，避免每位 Agent 从零发明机架语言。维护者在大版本 UI 发布后更新附录 A 与反模式 §十三，保证文档与截图同步。

---

## 附录 A：全站逐页美学注解（投屏与答辩向）

### A.1 顶栏 GlassNav

顶栏是「控制台铭牌」。品牌区左侧 VU 竖条是微型身份标识，五根竖条在 active 品牌态可有微弱脉动，但禁止高频闪烁导致视觉疲劳。导航链接在 active 时除底色变化外，Showcase 项可用 `glass-nav-link-showcase` 额外 signal 底边，与子路由专区形成心智锚点。任务 pill 是 mono 字号的 operational readout：无 task 时显示「—」，有 task 时缩写 ID 并可复制，复制成功态 `task-pill-copied` 应短暂切 signal 边框而非整页 toast。深浅主题下顶栏玻璃背景须保持与页面底有足够对比，避免「顶栏融进背景」。

### A.2 首页 Home

首页承担「第一印象」与「工作流地图」。console-hero 左区标题 Denoise Studio 用 Antonio，其中 Studio 可用斜体或 `<em>` 形成品牌断句。CTA 层级：主按钮上传、次按钮实时录音与 showcase，不可三者同等权重。右侧 MOD-01 机架卡是数值橱窗：28 图表、10+ 算法、ABX——数字用 display 字号，标签用 tertiary。机架卡整体 `-0.6deg` 微倾是「上台设备」隐喻，倾角不得超过 1deg，否则移动端显得草率。底部 01–06 flow 与 Upload/Live 内 flow strip 字号风格应统一，避免首页大气、内页小气。

### A.3 上传页 Upload

MOD-02 INPUT 是任务链入口。FileDropZone 在 empty 态必须是 **凹面 dashed** 邀请态，filled 态转 solid 边框表示「已有载荷」。MethodSelector 分组标题用 tertiary mono，选项说明用 secondary 正文，避免所有文字同一灰度导致扫读困难。runDistill 勾选与 strength 滑条是 **L3 正式管线** 参数，视觉上应靠近提交钮形成「配置簇」。提交中 LED 切 processing，按钮文案 uploading，禁止按钮可点二次提交。

### A.4 进度页 Progress

进度页是 **等待叙事**。状态字、progress 条、message 来自后端轮询，美学上 progress 条轨道用 panel-border，填充用 signal 渐变，indeterminate 时用 amber blink。空 task 引导链到 upload，链接用 signal 色而非默认蓝链。本页不需要花哨 Canvas，但 RackPanel 与子状态卡片仍需机架头，避免纯白列表。

### A.5 结果总览 Overview

Overview 是 **听感 + 指标** 双主轴。指标快照卡内 SNR、RMS 等数字必须 mono 对齐，小数位统一。波形条 scanning 态用 muted 动画而非空白。AudioComparePlayer MOD-04 是_mixer 美学高峰：通道条 active 有 rack-led，crossfade 切换时按钮状态同步。pipeline mismatch 告警用 danger 顶条 + 说明，不可仅一行红字。ABX 与 bookmark 是 Overview 的「研究员工具」，面板间距用 column gap 保持一致。

### A.6 图表中心 Charts

Charts 是 **密度最高** 页。Plotly 主题必须走 `plotTheme.ts`，背景与纸面色跟 `--bg-plot` 一致。分组折叠卡应有 group 标题 mono、plot 计数 badge。导出 PNG 按钮位置 per-card 统一右下或 header 右侧，不可有的卡有、有的无。筛选框 focus ring 用 `--focus-ring`。loading 态禁止只写 Loading 二字，用 muted + 可选 skeleton 边框。

### A.7 历史 History

History 是 **档案柜**。表头 mono 小字，行 hover 轻背景 `--signal-dim` 即可。task id 列用 code 字体完整可 hover 看全。删除钮 danger 描边 ghost，需二次确认或明确语义。空历史引导与 upload 一致口吻。

### A.8 Showcase 专区

Showcase 是 **品牌剧场**，可比业务页略戏剧，但仍禁紫色风暴。Hub bento 格每格有 MOD-S 编号感、短描述、探索链接。Pipeline Theater 路由动画 dot 沿链路移动是 **叙事动效** 范本。Signal Monitor 大屏 LCD ticker 滚动速度适中，metrics 到达时 flash 160ms。Compare Cinema 右侧可放 compact 监听单元。Scene Vault / Metrics Theater 等扩展页须接 i18n，卡片用 SceneCard stagger。

### A.9 Live Capture 专页深度注解

Live 页是本次美学重点。用户未点 REC 时，界面仍应「像一台通电但未进信号的示波器」：网格、角标、idle 文案共同传达「设备就绪」。点 REC 后 arming 约 0.8s，LED processing，给用户心理预期。recording 态 REC 钮 dot 脉冲，示波器 scan line 移动，竖 VU 随声跳动。ANC toggle 仅在 recording 可用，off 时 monitor LED 可用 processing 灰态，on 时 active 绿（signal）+ 腔体 pulse。latency badge 有数值才显绿，避免假精度。停止后进入 preview：L2 pill active，A/B 播放器出现，应用 stagger-fast 错峰入场。Commit 区 MethodSelector 与 Upload 一致，左条 `recordPipelineTag` 强调 L3。错误麦克风权限用 danger 横幅，非 alert()。

---

## 附录 B：色彩与对比度实操

浅色主题答辩时投影仪常压低黑位，因此 `--text-primary` 必须足够深，`--text-tertiary` 不可浅到看不清 MOD 号。signal 墨绿在白底上用于波形与计时器时，线宽可略增至 2px 保证远距识别。amber 用于警告勿大面积铺底，仅 badge、LED、左条。danger REC 红在浅粉按钮底上要保持 dot 饱和，外圈光晕用 color-mix 降透明度。

深色主题 OLED 或夜间：纯黑底 `#080a0f` 减轻灰雾感。signal 荧光青 glow 半径控制在 10–14px，过大则脏。玻璃卡 `--glass-bg` 半透明让背景 ScopeCanvas 微透，但业务机架模块 readability 优先，live-module 用 elevated 实底。

对比度建议：正文与底至少 4.5:1；MOD 标签与底至少 3:1。焦点环 `--focus-ring` 对键盘导航用户必须可见。

---

## 附录 C：排版与信息层级范例

一级：页面 title（RackPanel section-title）— 用户知道「我在哪」。二级：subtitle 一句职责说明。三级：MOD / CHANNEL mono。四级：字段 label mono 小字。五级：数值 mono 中大。六级：hint muted 正文。

反例：把 method 长说明与 SNR 数字同一字号；把 flow 步骤字号压到 0.7rem 以下；标题用 sans 系统字体。

Live 页实例：「实时采集」一级；「麦克风输入·实时 ANC 监听·一键提交」二级；「MOD-07A / INPUT」三级；「IN」「ANC」四级 VU label；计时器「00:42」五级；「录音中」status 六级药丸。

---

## 附录 D：动效配方手册

**入场**：页面根 `stagger` 子项 delay 20–80ms 递增，最多 6 子项；更多块用 `StaggerGroup` 或手动 `--delay`。

**hover**：机架模块 translateY(-2px) + border-strong，160ms。**active press**：scale(0.98) 可选，勿弹跳过度。

**recording**：recPulse 1s；scan line 由时间驱动非 random。**processing**：rackLedBlink 0.8s 与全局背景琥珀态同步。

**数据到达**：metrics flash 160ms 一次，禁止 loop。

**降级**：`prefers-reduced-motion: reduce` 关 pulse/blink/scan，保留静态色态。

---

## 附录 E：移动端与窄屏

断点 900px live grid 单列；示波器高度保持 min 96px。Monitor 拟物宽度 `min(140px, 36vw)`。Transport 单列，LCD 读数仍右对齐或整行。VU 竖条 min-height 72px。触控目标 REC 至少 44px 高。ANC toggle 整行可点。

避免横向 scroll；flow strip 可 wrap。顶栏 menu 折叠后链接间距加大。

---

## 附录 F：无障碍与语义 HTML

装饰 canvas `aria-hidden`。录音状态 `aria-live="polite"` 在 RecordTransport。REC `aria-pressed`。ANC checkbox 有 label 包裹。错误信息不只靠红色，须有文字。焦点顺序：flow → tier → scope → anc → transport → commit。

---

## 附录 G：美学 Code Review 十问

改 UI 提交前自问：

1. 有没有空灰盒？2. LED 是否绑定状态？3. 颜色是否全 token？4. 深浅主题是否都看过？5. i18n 是否双语？6. reduced motion 是否降级？7. 移动端是否溢出？8. 预览与正式是否标注？9. 是否复用 RackPanel/VU？10. 是否引入禁止字体/库？

任一项否，需补完再交付。

---

## 附录 H：与竞品/参考的差异化

不抄 DAW 全功能_mixer 复杂度；不抄 Zoom 会议大号按钮；不抄 Spotify 沉浸封面。参考方向：广播台 rack unit、Tek 示波器取景框、Nagra _transport 简洁、Grado 耳机轮廓几何而非产品摄影。

---

## 附录 I：迭代版本记录建议

大美学改版打 tag：`web-signal-console-design-v1.x`。在 `docs/prompts` 末尾加「美学变更」三行：日期、截图问题、改动摘要。Skill reference 附录同步版本号。

---

## 附录 K：Design Token 全表导读（中文详注）

`--bg-base` 是全站地基色，决定用户处于「灰工作室」还是「深控室」。其之上 `--bg-surface` 用于二级平面，`--bg-elevated` 用于可交互机架模块，三层递进不可颠倒，否则卡片贴地无层次。`--text-primary` 是叙事主色，`--text-secondary` 承载说明，`--text-tertiary` 专供 MOD 与刻度——三者不可混为同一灰度。`--signal` 是品牌第一识别色，波形/LCD/主链接皆依此，浅色墨绿、深色荧光青，改 signal 等于改品牌。`--amber` 表「进行中/预览/缓冲」，与 signal 混淆会致状态误读。`--danger` 仅 REC/错误/失配，滥用则警报疲劳。`--panel-border` 默认描边，`--panel-border-strong` 表聚焦或录音中，`--glass-inner-highlight` 模拟机壳倒角 1px 高光。`--glass-shadow` 是 RackPanel 外卡阴影公式，含 1px 环与柔和投影，勿再加第二层竞争阴影。`--signal-dim` 与 `--signal-glow` 分别用于浅底强调与 LED 外晕，glow 半径宜小。`--rack-lcd-bg` 与 `--rack-lcd-text` 专供 LCD 读数区，深色底浅绿字或浅底墨绿字，须与 transport 区绑定。`--font-display/main/mono` 三角锁定工业/论文/数据三种情绪。`--dur-fast/base/slow` 与 `--ease-standard/snap` 控制动效性格：snap 仅用于主按钮微弹跳，不可用于 LED blink。Live 专属 `--live-scope-bg/grid/center` 解决「空灰盒」：bg 略区别于 module 底，grid 极低对比，center 略高于 grid。掌握全表，Agent 改色不迷路。

---

## 附录 L：业务页与 Showcase 页美学权重

业务六页权重：可读性大于戏剧性。Showcase 权重：戏剧性略高但仍禁霓虹。Live 页权重：实时信任感第一——仪器框架、层级披露、状态联动三者权重高于装饰。History/Charts 权重：表格与图表信息密度优先，机架头简洁即可。Upload 权重：邀请态 drop 区与 method 说明清晰优先。Home 权重：品牌第一印象，机架卡与 CTA 层级优先。按权重分配改版时间，避免在 History 花三小时动画却在 Live 留空灰盒。

---

## 附录 N：常见问题 FAQ（美学向）

**Q：能否用 Tailwind 加快改版？** A：禁止，破坏 token 单一来源与毕设风格一致性。**Q：示波器能否用静态 PNG 背景？** A：禁止，录音时须真实 analyser 驱动。**Q：深色模式可否不做？** A：不可，至少保证可读不崩。**Q：Live 页能否去掉 L1/L2/L3？** A：不可，层级披露是诚信要求。**Q：能否把 REC 改成蓝色主钮？** A：不可，REC 国际惯例红色，主 CTA 仍 signal。**Q：机架倾斜能否加大到 5deg？** A：不可，超过 1deg 显草率且影响布局。**Q：答辩截图用深色还是浅色？** A：默认浅色；深色作附录展示夜间场景。

---

## 附录 P：Upload / Overview / Charts 快速美学债务清理指南

Upload 页五分钟清理：确认 MOD-02 LED 绑 file/loading；drop 区 dashed 凹面；method 说明字号层级；flow strip active 有 glow；提交钮 primary 唯一。Overview 五分钟清理：指标 mono 对齐；pipeline mismatch  danger 条可见；AudioComparePlayer 通道 LED 与 active 同步；波形 scanning 文案。Charts 五分钟清理：Plotly 背景 `--bg-plot`；分组标题 mono；空数据 muted 提示非空白。History 五分钟清理：表头 mono；行 hover；空态引导句。Showcase Hub 五分钟清理：bento 编号感；子 nav active；hub 标题 Antonio 层级。每页小步迭代，胜过大范围重写。全站美学统一来自 **重复的小修**，而非一次幻想中的「大换血」。以上附录与正文合计，构成 Denoise Studio 约 **一万汉字** 级设计 skill 语料库，供人与 Agent 在答辩与迭代中共享同一审美标准。字数目标：一万汉字；不足时以 doctrine 章节增补，超出时精简 FAQ 即可。至此 reference 收束。

---

## 附录 O：推荐阅读顺序（Agent 首次启用）

1. SKILL.md 清单 2. examples.md 对照截图 3. reference §一~§八 4. doctrine-zh 第一~十章 5. reference 附录 A~M 6. 打开 tokens.css 与 live-capture.css 7. 执行改版 8. 附录 M 截图回归。总计阅读约十五分钟即可开工，万字文档用于深度疑难而非每次全读。

---

## 附录 M：截图回归清单（Agent 自动验收）

改版后生成或要求用户确认四张截图：浅色 Live idle、浅色 Live recording、浅色 Live preview、深色 Live recording。检查点：网格可见、bracket 可见、tier 可读、REC 态明确、Monitor 拟物存在、LCD 区存在、无横向滚动、无硬编码色块突兀。不合格则回到 §十三反模式对照修改。

---

## 附录 J：一万字教义之核心复述

Signal Console 美学是 **专业可信** 的秩序：机架编号告诉用户结构，LED 告诉用户状态，mono 告诉用户数据，示波器告诉用户信号有无，L1/L2/L3 告诉用户算法期望。空状态不是偷懒的留白，而是「设备待机」的诚实沟通。每一次 UI 迭代都应让用户更相信：这是一个真正做过降噪实验、能写进论文的系统，而不是套壳 demo。Agent 执行本 skill 时，务必同时打开 `tokens.css` 与目标页截图，对照附录 A 逐屏检查，再动代码。视觉层级先于装饰；语义先于炫酷；可读先于紧凑。若字数与美感冲突，扩页边距、加网格、加一句 idle 提示，永远优于塞入更多渐变与粒子。

---

*文档版本：web-signal-console-design-skill v1 · 与 MOD-07 Live Capture 美学迭代同步 · 全 skill 中文语料约一万字*
