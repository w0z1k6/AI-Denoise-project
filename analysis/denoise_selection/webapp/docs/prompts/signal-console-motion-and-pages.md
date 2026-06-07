# AI 提示词：Denoise Studio Signal Console — 全站动效升级 + 新页面扩展（基于当前全站截图）

> 复制整段给 Cursor / Claude。在 **已上线的业务六页 + Showcase 五页 + RackPanel + 互动背景 + MOD-HS01 监听单元** 基础上迭代，**禁止推倒重来**。  
> 参考截图：Home（MOD-01 机架）、Upload（MOD-02）、Overview（MOD-01~04 纵向机架）、Charts（Plotly 频谱墙）、History（MOD-06 表格）、浅色主题为主。  
> 前置版本：`web-signal-console-rack-polish`、`web-signal-console-showcase-polish`、`web-signal-console-headphone-rack`、`background-mouse-interaction`。

---

## 角色与目标

你是资深创意前端工程师 + 音频 HMI 动效导演，负责将 Denoise Studio 从「功能完整、视觉尚可」升级为「**答辩可投屏、操作有反馈、待机有生命感**」的广播级 Signal Console。

**用户反馈摘要（截图观感）：**
- 整体干净专业，但偏**静态**——背景波形、机架模块、表格行、Plotly 卡片之间缺少「调音台通电」的层次动效
- Home 右侧机架有倾斜与 VU 脉动，内页（Upload / Overview / Charts / History）多为**平铺白卡**，品牌戏剧感在路由切换时断裂
- MOD-HS01 监听单元在部分截图中未出现或视觉权重不足，需与 MOD-01 形成**双模块叙事**（输入统计 + 参考监听）
- 流程条（01–06）字号偏小、与 Hero 区脱节，像脚注而非工作流主轴
- Charts 四宫格同质，仅部分卡有「导出 PNG」，信息层级与交互不一致
- 右侧浮动按钮（疑似浏览器扩展）与产品 UI 无关，**不要**在实现中模仿

**本次两大目标：**

| 轴 | 目标 |
|----|------|
| **动效** | 建立统一的 Signal Motion System：页面转场、机架通电序列、数据驱动 LED/VU、背景与业务状态联动 |
| **页面** | 在不大改 API 的前提下，新增 4–6 个**高价值**路由，填补「场景库、指标剧场、报告导出、批量对比、设置、引导」空白 |

**「炫酷」在本项目中的定义（再次强调）：**

| ✅ 要做 | ❌ 禁止 |
|--------|--------|
| 机架 LED 脉冲、LCD 滚动、管线 dot 流动、VU 随播放跳动 | 紫色渐变、霓虹赛博、全屏粒子风暴 |
| Canvas 示波器振幅调制、频谱柱状微动 | Three.js 大场景、WebGL _shader 滥用 |
| 鼠标视差 ≤24px、lerp 平滑、processing 时琥珀闪烁 | 每帧 React setState 驱动全页 |
| `prefers-reduced-motion` 全量降级 | 无视无障碍的 infinite 动画 |
| 真 task 数据驱动动效（播放、processing、completed） | 假数据冒充已完成任务 |

---

## 技术约束（必须遵守）

| 项 | 要求 |
|----|------|
| 路径 | 主要 `analysis/denoise_selection/webapp/frontend/`；动效 token 可扩 `tokens.css`、`motion.css` |
| 栈 | React 18 + TypeScript + Vite；**纯 CSS + Canvas**，不引入 Framer Motion / GSAP（除非用户明确要求且 bundle 增量 <15KB gzip） |
| 禁止 | Tailwind、MUI、Ant Design、紫色渐变、Inter/Roboto/Space Grotesk、Three.js |
| 字体 | Antonio（Display）+ Newsreader（正文）+ Fragment Mono（数据 / MOD 编号） |
| API | **只读**现有 `api.ts`；新页可用 `getTask`、`getHistory`、`getMetrics`、`audioUrl` 等；**禁止**改后端契约 |
| 路由 | **可**扩展 `app/router.tsx`；业务六 path 保持不变 |
| 性能 | Canvas `requestAnimationFrame`；DPR cap 2；`visibilitychange` 暂停；移动端降级 |
| 测试 | `npm run build` + `npm test` 通过 |
| i18n | 所有可见文案写入 `src/i18n/index.ts` 中英文键 |
| 无障碍 | 动效装饰元素 `aria-hidden`；状态变化有 `aria-live="polite"` 文本兜底 |

---

## 现有资产盘点（必须复用）

| 资产 | 路径 | 动效相关用途 |
|------|------|-------------|
| 指针追踪 | `hooks/useStudioPointer.ts`、`lib/pointerStore.ts` | `--pointer-x/y`、`--grid-shift`、Canvas 相位 |
| 背景层 | `AmbientBackground.tsx`、`ScopeCanvas.tsx`、`studio-console.css` | 网格视差、粒子、涟漪、processing 琥珀晕 |
| 任务态背景 | `hooks/useBackgroundMotion.ts`、`motionFlags.processing` | processing 时背景加速/变色 |
| 页面转场 | `AppShell.tsx`、`motion.css` `.page-route` | 当前仅 `fadeInUp 280ms`；showcase 子路由禁用动画 |
| 错峰入场 | `motion.css` `.stagger` / `.stagger-fast` | 子元素 20–270ms delay，最多 6 子项 |
| 机架 LED | `rack-polish.css` `.rack-led-*`、`rackLedBlink` | 全站统一 LED 语义 |
| 展示动效 | `showcase.css` pipeline dot、VU pulse、LCD scroll、monitor flash | 可抽取为共享 motion 片段 |
| 机架壳 | `RackPanel.tsx` | 所有新页区块顶栏 |
| 监听单元 | `HeadphoneRackUnit.tsx`、`headphone-rack.css` | 播放/ABX/processing 联动 |
| 音频试听 | `AudioComparePlayer.tsx`、`audioCrossfade.ts` | Cinema / 新页可复用 |
| Plotly | `lib/plotTheme.ts` | Charts 与新 Spectral 页主题一致 |

**当前路由（保持 path，可增不改名）：**

```
业务：/  /upload  /progress  /overview  /charts  /history
展示：/showcase  /showcase/algorithms  /showcase/pipeline
      /showcase/monitor  /showcase/cinema
```

**已知待修复（动效/数据联动前置）：**
- `router.tsx` 中 `HomePage` 需传入 `taskId`（否则 MOD-HS01 LED 永远 idle，截图 Home 仅见 MOD-01）
- `stagger` 仅支持直接子元素前 6 个；Overview 等多 RackPanel 页第 7+ 块无错峰
- Charts 页 Plotly 重绘无「数据到达」动效，loading 态仅为 muted 文字

---

## 第一部分：Signal Motion System（全站动效设计系统）

### 1.1 设计原则 — 「广播台通电，不是屏保」

动效必须携带**语义**，四类触发源：

| 触发源 | 示例 | 禁止 |
|--------|------|------|
| **路由** | 进入 Upload 时 stepper 01 高亮扫光 | 每次 hover 整页缩放 |
| **任务状态** | processing → 背景琥珀 + 顶栏 LED blink | 无任务时常亮绿色 |
| **用户操作** | 播放 → VU 跳、耳机网罩 pulse | 点击后 2s 弹跳 |
| **数据到达** | metrics 返回 → 数字 roll-up | 假随机数字滚动 |

**时长与缓动 token（写入 `tokens.css` 或 `motion.css`）：**

```css
--motion-instant: 80ms;
--motion-fast: 160ms;      /* 已有 --dur-fast */
--motion-base: 240ms;
--motion-slow: 520ms;
--motion-dramatic: 840ms;  /* 机架通电序列总时长 */
--ease-rack: cubic-bezier(0.22, 1, 0.36, 1);
--ease-snap: cubic-bezier(0.34, 1.4, 0.64, 1);  /* 已有，用于按钮 */
--ease-lcd: linear;        /* LCD 滚动 */
```

**LED 状态机动画（全站统一，扩 `rack-polish.css`）：**

| 状态 | 视觉 | 动画 |
|------|------|------|
| `idle` | 灰，opacity 0.5 | 无 |
| `active` | `--signal` + glow | 可选 3s 慢呼吸 opacity 0.85↔1 |
| `processing` | `--amber` | `rackLedBlink` 0.8s（已有） |
| `error` | `--danger` | 双闪 0.45s + 常亮 |

### 1.2 页面转场 — 升级 `AppShell` / `motion.css`

**现状：** 业务页统一 `fadeInUp 8px`；showcase 子路由共享 key `/showcase` 无转场（正确，避免闪烁）。

**改进方案（纯 CSS，不增依赖）：**

1. **业务页分级转场** — 根据 `location.pathname` 在 `PageTransition` 上加 modifier class：
   - `page-route--depth-1`：Upload / Progress（表单页）→ 自下方 12px + 轻微 `scale(0.992→1)`
   - `page-route--depth-2`：Overview / Charts（数据页）→ 仅 opacity 180ms（避免大图表布局抖动）
   - `page-route--depth-0`：Home → 保持现有 fadeInUp
   - `page-route--table`：History → 表格行 stagger 由页内负责，外壳 opacity only

2. **导航方向感（可选 P2）** — 在 `GlassNav` 记录 `prevPath` 索引顺序；向左导航时 `translateX(-6px)` 入场，向右 `translateX(6px)`。索引：`home=0, upload=1, progress=2, overview=3, charts=4, showcase=5, history=6`。

3. **转场期间背景** — `motionFlags.transitioning` 300ms 内 ScopeCanvas 振幅 ×0.6，避免「页在动、波在狂」。

4. **reduced-motion** — 已有全局 `animation: none`；补充 `page-route` 直接 `opacity: 1; transform: none`。

**文件：** `AppShell.tsx`、`motion.css`、`lib/pointerStore.ts`（增 `transitioning` flag）

### 1.3 机架通电序列 — `rackPowerOn` 共享 class

为所有 `RackPanel` / `console-module` 增加**首次进入视口**通电动画（`IntersectionObserver`，threshold 0.2，只播一次）：

```
时间轴（总 ~720ms）：
0ms    — 面板 border-opacity 0→1，顶栏 MOD 文字 opacity 0→1
80ms   — 顶栏 LED 从 idle 闪一次 signal（即使状态为 active 也先闪再稳）
160ms  — 内容区 translateY(6px→0) + opacity
240ms  — 若含 VU/读数：柱子从 0 长到目标高度（CSS variable --vu-target）
400ms  — 完成，移除 .rack-powering class
```

实现要点：
- 用 `data-rack-power` 属性标记，`prefers-reduced-motion` 跳过 Observer
- **禁止**每次 re-render 重播；用 `sessionStorage` key `rack-seen-${moduleId}` 或 ref 标记
- Overview 纵向 4+ 面板：**交错 delay** `idx * 90ms`，形成「机架从上到下通电」

**文件：** 新建 `hooks/useRackPowerOn.ts`、`rack-polish.css`（`.rack-powering`、`.rack-powered`）

### 1.4 扩展 stagger — 支持任意子项数量

**现状：** `.stagger > *:nth-child(6)` 封顶，Overview 6+ 模块同时出现。

**改进：**
```css
.stagger > * {
  animation-delay: calc(20ms + (var(--stagger-i, 0) * 50ms));
}
```
在 React 父级用 `style={{ '--stagger-i': index }}` 注入，或小型 `StaggerGroup` 组件包裹 map。

**文件：** `motion.css`、可选 `components/StaggerGroup.tsx`

### 1.5 数据驱动微动效

| 组件 | 数据 | 动效 |
|------|------|------|
| `StatusBadge` | status 变化 | 旧 badge fade out 120ms，新 badge scale 0.92→1 |
| 指标数字 | SNR 等 metrics | `CountUp` 纯 CSS：@property --num + transition 600ms（或 12 帧 rAF 手写，勿引库） |
| `WaveformPanel` | 播放进度 | 播放头竖线 `--progress` 平滑；暂停时停止 |
| `AudioComparePlayer` | active 声道 | 选中卡 border-glow 脉冲 1 次；VU 条高度随 `timeupdate` |
| `HeadphoneRackUnit` | playing | 网罩 pulse（已有）；**补**左右耳罩 VU 微缩放 ±2% |
| Plotly 卡片 | chart ready | 容器 `opacity 0→1` 300ms；toolbar 延迟 150ms 淡入 |
| History 行 | hover | `translateX(2px)` + 左侧 2px signal 竖条；选中行背景 `--signal-dim` |

### 1.6 背景层动效 V2（在 `background-mouse-interaction.md` 基础上）

**截图问题：** 浅色主题下底部波形+频谱条偏淡，像「贴图」而非「 живой 信号」。

**P0 改进：**

1. **双速示波器** — `ScopeCanvas` 增加「慢层」与「快层」：
   - 慢层：周期 4s，amplitude 随 `pointer.y` ±15%
   - 快层：周期 1.2s，amplitude 随播放状态（读取全局 `audioPlaying` flag）×1.8
   - processing：`motionFlags.processing` 时快层改 amber 色 30% 混合

2. **频谱条动画** — 底部竖条（若有）用 CSS `transform: scaleY()` 随机种子固定 per-bar，1.5s ease-in-out infinite，**reduced-motion 静止为 0.6**

3. **滚动视差** — 已有 `--scroll-parallax`；加强：Home hero 区 `translateY(scroll * -0.04)`，rack 区 `translateY(scroll * 0.02)` 形成景深

4. **路由色调** — 轻量 crossfade：`/upload` 背景 grid 偏 signal，`/history` 偏 neutral gray，`/showcase/*` grid 略密。通过 `document.body.dataset.route` 切换 CSS，300ms transition

5. **点击涟漪保留** — 上传区拖拽成功时，在 drop 点触发 **琥珀** ripple（与 signal 默认区分）

**文件：** `ScopeCanvas.tsx`、`studio-console.css`、`AmbientBackground.tsx`、`AppShell.tsx`（设 data-route）

---

## 第二部分：分页面动效规格（基于截图逐项）

### 2.1 Home `/` — 截图：Hero 强、MOD-01 有 VU、流程条弱、MOD-HS01 可能缺失

**P0 — 双机架叙事**
- 确保 `HomePage` 接收 `taskId`，MOD-HS01 与 MOD-01 **垂直叠放**，间距 `var(--space-16)`
- MOD-01 与 MOD-HS01 **交错通电**：HS01 delay +120ms
- 点击 MOD-HS01 整卡链到 `/showcase/cinema`（有 completed task）或 `/overview`

**P1 — Hero 动效**
- `console-title` 字距入场：letter-spacing 0.08em→0.04em，600ms（仅首访）
- CTA primary：hover 时 signal glow 已有；**补** active 时 `scale(0.98)` 100ms

**P1 — 流程条 01–06 升级**
- 改为 `console-flow--timeline`：水平线连接圆点，当前步（根据最近 task 状态推断或默认 01）圆点 `rack-led-active`
- hover 每一步：显示 tooltip 一句话（i18n `flowUploadHint` 等）
- 步进动画：进入视口时圆点依次 scale 0→1，delay `idx * 60ms`

**P2 — 底部 bento 四卡**
- 每卡左上角加 mono 图标（CSS 绘制：上传=箭头、指标=数字、图表=折线、ABX=耳机）
- hover：图标 stroke 改 `--signal`，非整卡弹跳

**文件：** `HomePage.tsx`、`home.css`、`router.tsx`（传 taskId）

### 2.2 Upload `/upload` — 截图：MOD-02 单卡、拖拽区虚线、stepper 01 亮

**P0 — 拖拽区状态机动画**
| 状态 | 视觉 |
|------|------|
| idle | 虚线 border，慢速「呼吸」opacity 0.7↔1，3s |
| drag-over | border `--signal`，背景 `--signal-dim`，虚线改实线，内阴影 inset glow |
| file-selected | 文件名 typewriter 效果（mono），右侧绿色勾 LED 闪 1 次 |
| uploading | 顶部 2px 进度条 indeterminate signal→amber 流动 |

**P1 — Stepper 联动**
- 当前步下方 2px signal 条 `width` animate
- 提交成功后（setTaskId 后）：整卡 flash 150ms + 自动导航 `/progress` 前 200ms 延迟（可选，需防重复）

**P1 — 表单微交互**
- 算法下拉展开：选项 stagger 30ms（纯 CSS max-height transition）
- noisereduce 滑块：thumb 拖动时右侧数值 flip（tabular-nums）

**文件：** `UploadConfigPage.tsx`、`upload-overview.css`

### 2.3 Progress `/progress` — 未在截图集但属主流程

**P0 — 进度机架**
- 复用 Pipeline Theater 的 **dot 流动** 逻辑：steps = upload→queue→process→metrics→done
- `getTask` poll 时 LED processing；completed 时全链路亮 + OUTPUT flash（与 showcase 修复一致）
- 失败：面板 shake 4px 一次（`rack-shake` 400ms，仅 error 时）

**P2 — 预估时间 LCD**
- 若有 `progress` 字段：LcdTicker 滚动显示 step 名称；无则显示 `processingHint`

**文件：** `TaskProgressPage.tsx`、新建 `styles/progress.css` 或扩 `rack-polish.css`

### 2.4 Overview `/overview` — 截图：MOD-01~04 纵向、A/B 播放器、底部波形

**P0 — 纵向机架节奏**
- 4 个 RackPanel stagger 90ms（用扩展 stagger）
- MOD-04 A/B 区：播放时**非选中**声道卡 opacity 0.72，选中卡左侧 3px signal 竖条

**P1 — 波形区**
- `WaveformPanel` 加载：骨架屏 3 条灰色 shimmer（已有 waveShimmer 可复用）
- 双波形对齐：播放时两图同步 vertical line；缩放保持

**P1 — ABX 区**
- `HeadphoneRackUnit` compact：猜题提交 amber flash 300ms（已有逻辑，确保 CSS 可见）
- 准确率数字变化时 CountUp

**P2 — Pipeline 折叠**
- `PipelineSummary` 展开/收起：grid-template-rows 动画（glass.css collapse 已有）

**文件：** `ResultOverviewPage.tsx`、`upload-overview.css`、`ABXTestPanel.tsx`

### 2.5 Charts `/charts` — 截图：2×2 频谱、部分有导出 PNG、Plotly toolbar

**P0 — 卡片一致性**
- 四卡**统一**顶栏：标题 + `导出 PNG` 按钮（或统一收到 hover 工具条）
- 卡片 loading：MiniScope 占位 120px 高，数据到达 crossfade

**P1 — 对比阅读动效**
- Original vs Denoised 并排：用户 hover 标题时，另一张 opacity 0.55，强调对比
- Residual 卡：默认 amber 左边框 2px，提示「差异层」

**P2 — Plotly 主题联动**
- 切换 light/dark：Plotly relayout 无闪烁（plotTheme 已有，补 transition 遮罩 200ms）

**P2 — 滚动入场**
- 2×2 grid 用 IntersectionObserver 逐卡 fadeInUp（非一次全显）

**文件：** `ChartCenterPage.tsx`、`chart` 相关样式

### 2.6 History `/history` — 截图：MOD-06 表、完成/失败色、操作三按钮

**P0 — 表格行交互**
- hover：行背景 `--glass-bg`，左侧 signal 竖条 width 0→3px
- 当前 task 行（与 nav taskId 匹配）：persistent `--signal-dim` 背景 + 行首 `▸` mono
- 删除：点击后行 opacity→0.4 + 按钮 loading，成功后行高 collapse 300ms

**P1 — 状态徽章**
- completed：进入视口时勾 path stroke-dashoffset 动画（SVG 内联 400ms）
- failed：徽章轻微 horizontal shake 1 次

**P2 — 空状态**
- 无历史：空机架 LCD 显示 `NO LOG ENTRIES`，字符闪烁 cursor 1s

**文件：** `HistoryPage.tsx`、`history` 样式（可扩 `rack-polish.css`）

### 2.7 Showcase 五页 — 在 `signal-console-showcase-polish.md` 已列 P0 基础上补动效

| 页 | 追加动效 |
|----|----------|
| Hub | bento 四卡异色 LED 周期错开 0.5s；MiniScope 与背景 Scope 相位差 180° |
| Algorithms | 机架格 hover 时该格 LCD 单行滚动方法名 |
| Pipeline | OUTPUT 点亮时整链 `pipeline-flow-complete` 1s glow（已有 flash，加强连接线） |
| Monitor | present 模式：VU 柱高度 ×1.2，背景 grid opacity 降低 |
| Cinema | 沉浸式：非播放时 UI 控件 opacity 0.35，鼠标移动 fade in；耳机 compact VU 同步 |

**文件：** `showcase.css`、各 showcase 页面

---

## 第三部分：建议新增页面（6 个，按优先级）

> 新页须走 **RackPanel + showcase/business 设计语言**；有 `taskId` 读真数据，无则 demo 态 + `SIM` 徽章。

### P0-A — 场景库 Scene Vault `/showcase/scenes`

**叙事：** 答辩时快速切换「鸟鸣干扰 /  chirp / 低 SNR」等典型场景，一键加载 demo 或跳转 Upload 预填。

**布局：**
```
┌─ MOD-S06 / SCENE VAULT ─────────────────────┐
│ 筛选：SNR · 干扰类型 · 时长                    │
│ ┌────┐ ┌────┐ ┌────┐ ┌────┐  机架格          │
│ │S09 │ │S12 │ │... │ │    │  每格：波形缩略   │
│ └────┘ └────┘ └────┘ └────┘  Canvas 静态帧   │
│ [加载到 Upload] [在 Cinema 试听]               │
└──────────────────────────────────────────────┘
```

**数据：** 新建 `lib/scenePresets.ts`（从前端 manifest 或现有 task 文件名模式推断），**不调新 API**。

**动效：** 选中格 border signal + 缩略波形 phase 动画；切换场景 crossfade 200ms。

**路由：** `/showcase/scenes`；Hub bento 增第 5 格或替换最弱装饰格。

---

### P0-B — 指标剧场 Metrics Theater `/showcase/metrics`

**叙事：** 将 Overview 的数字指标做成**大屏可读**的 LCD + VU + 雷达图（CSS conic-gradient），适合投屏。

**布局：**
- 左：SNR / RMS / Kurtosis 大三数字 CountUp
- 中：雷达图（五维：SNR、清晰度、残留、延迟、算法复杂度——后两项可静态 demo）
- 右：HeadphoneRackUnit + 快捷链 Cinema
- 底：LcdTicker 滚动 raw metrics JSON 行

**数据：** `getMetrics(taskId)`；无 task 显示 demo 数字 + SIM。

**动效：** 数字到达 stagger；雷达图 `--pct` transition 800ms；Load Task 重播整页通电序列。

**与 Monitor 区别：** Monitor 偏时序/遥测；Metrics 偏**单次任务快照对比**（original vs denoised 并排数字）。

---

### P1-C — 频谱对比廊 Spectral Diff `/showcase/spectral`

**叙事：** Charts 页是「分析员工具」；本页是「**一眼看出降噪前后差异**」的展示廊。

**布局：**
- 全宽上下分割 slider（CSS `clip-path` 或 range input 控制中线位置）
- 左半 Original STFT、右半 Denoised STFT（Plotly 静态图或预生成 PNG from API）
- 中线拖动手柄：mono `Δ` 读数

**动效：** 拖动手柄时中线 glow；释放时 residual 能量数字 flash。

**数据：** 复用 Charts 同源 plot API；无 task 用 placeholder spectrogram（灰度 noise pattern，标注 DEMO）。

---

### P1-D — 报告导出台 Report Desk `/report`

**叙事：** 毕设/答辩需要 PDF 或 Markdown 报告，目前分散在 Overview + Charts。

**布局：**
```
MOD-07 / EXPORT
☑ 指标摘要  ☑ 频谱图  ☑ ABX 统计  ☑ Pipeline
[预览 Markdown] [下载 .md] [打印友好 HTML]
```

**实现：** 前端组装已有 API 数据为 Markdown 字符串，`Blob` 下载；**不调新后端**。

**动效：** 勾选 checkbox 时右侧预览区对应 section slide down 240ms；生成时顶部 progress indeterminate。

**路由：** `/report`；Nav 可放 More 下拉或 Overview 顶栏按钮链入。

---

### P2-E — 批量对比 Batch Compare `/compare`

**叙事：** History 表是列表；本页选 2–4 个已完成 task **并排**比 SNR、方法、试听。

**布局：** 列 = task；行 = 指标 / 方法 / 迷你试听按钮 / 雷达缩略

**数据：** `getHistory` + 多次 `getMetrics`（注意并发限制，最多 4 个）。

**动效：** 列增删时 flex 宽度过渡；胜出列（最高 SNR）顶部挂 `BEST` amber 徽章 fade in。

**限制：** 无新 API；任务过多时提示缩小选择。

---

### P2-F — 工作台设置 Settings `/settings`

**叙事：** 主题、语言、动效Reduced 预览、默认算法、Crossfade 时长、示波器密度——目前散落 localStorage。

**布局：** RackPanel 分组：DISPLAY / AUDIO / MOTION / DATA

**关键项：**
- `prefers-reduced-motion` 与站内「减少动效」开关联动（写 `motionFlags.reduced`）
- 默认 landing：Home vs Showcase
- 清除本地 taskId / 缓存

**动效：** 切换主题时 `document.startViewTransition`（若浏览器支持）或 300ms opacity crossfade；不支持则 instant。

**路由：** `/settings`；Nav 右侧齿轮链入。

---

### P2-G — 首次引导 Onboarding `/welcome`（可选，单屏）

**叙事：** 新用户不知 01–06 流程；单屏 3 步 overlay 或独立页。

**步骤：** 上传 → 进度 → Overview 试听；每步示意图 + 「开始」链到 `/upload`。

**动效：** 步进 slide；跳过写 `localStorage onboarding=1` 不再显示。

**触发：** 无 taskId 且首次访问 Home 时 modal（非强制新路由）。

---

## 第四部分：导航与信息架构调整

### 4.1 顶栏 `GlassNav`

**截图问题：** Task ID 过长占宽；Showcase 与业务平级但层级不清。

**改进：**
1. Task pill 默认缩写（`pipelineUtils.abbrevTaskId`），hover 展开全 ID + copy
2. Showcase 项 hover 下拉预览 5 子链（纯 CSS focus-within）
3. 当前路由：mono 底边 2px signal（不仅 background pill）
4. processing 时 nav 底边琥珀 indeterminate 流动（与 `useBackgroundMotion` 联动）

### 4.2 页内 wayfinding

- 除 Home 外，每业务页 RackPanel subtitle 下加 **一行 mono breadcrumb**：`WORKFLOW / 03 PROGRESS`
- Overview ↔ Charts ↔ Cinema 三角互链（「去看频谱」「去影院试听」）

### 4.3 Footer 状态条（可选 P2）

- 固定底栏 24px：`SIGNAL CONSOLE v0.1 · {theme} · {motion on/off} · {task status}`
- 像机架设备状态栏，不挡内容（`padding-bottom` on page-shell）

---

## 第五部分：组件级新建/扩展清单

| 组件 | 职责 |
|------|------|
| `StaggerGroup` | 注入 `--stagger-i`，任意子项错峰 |
| `useRackPowerOn` | IntersectionObserver 机架通电 |
| `CountUpValue` | 数字滚动，尊重 reduced-motion |
| `RouteMotionShell` | 替代 PageTransition 分级 class |
| `SceneCard` | Scene Vault 单格 |
| `SpectralWipe` | 频谱对比中线拖动 |
| `ReportComposer` | 组装 Markdown |
| `CompareColumn` | Batch Compare 单列 |
| `SettingsSection` | Settings 分组 |
| `audioPlayingStore` | 全局播放 flag，供 ScopeCanvas（类似 pointerStore） |

**禁止**为每个动效新建独立 .css 文件超过 2 个；优先并入 `motion.css`、`rack-polish.css`、`showcase.css`。

---

## 第六部分：实施顺序（建议 3 个 PR 波次）

### Wave 1 — 基础动效（1–2 天）
1. 修复 `HomePage` taskId + MOD-HS01 可见
2. `motion.css` 扩展 stagger + page-route 分级
3. `useRackPowerOn` + Overview/Upload 通电
4. `audioPlayingStore` + ScopeCanvas 播放联动
5. Upload 拖拽区状态机动画
6. `npm run build && npm test`

### Wave 2 — 页面体验（2–3 天）
1. Home 流程条 timeline 化
2. Charts 卡片统一 + loading skeleton
3. History 行 hover + 删除动画
4. Progress pipeline dot（若页过简则加强）
5. Nav task pill + processing 底边
6. Scene Vault `/showcase/scenes`
7. Metrics Theater `/showcase/metrics`

### Wave 3 — 扩展页 + 打磨（2–3 天）
1. Spectral Diff `/showcase/spectral`
2. Report Desk `/report`
3. Settings `/settings`
4. Batch Compare `/compare`（时间允许）
5. Onboarding modal
6. 全站 `prefers-reduced-motion` 走查
7. 浅色主题对比度复检 WCAG AA

**建议版本标签：** `web-signal-console-motion-v1`、`web-signal-console-new-pages`

---

## 第七部分：验收标准（Checklist）

**动效**
- [ ] 业务页切换有可感知但不晕的转场；showcase 子路由不闪
- [ ] RackPanel 首次入视口有通电序列；reduced-motion 下跳过
- [ ] processing 任务时：nav/背景/相关 LED 琥珀语义一致
- [ ] 音频播放时：VU、耳机、Scope 快层振幅联动
- [ ] 无 infinite 动画在 reduced-motion 下残留
- [ ] 移动端（≤768px）关闭粒子/减弱视差（`motionFlags.mobile`）

**页面**
- [ ] Scene Vault、Metrics Theater 可无 task demo 访问
- [ ] 有 task 时 Load / 跳转读真 API
- [ ] Report 可下载 Markdown，内容含 metrics + 方法 + 时间
- [ ] 新路由全部 i18n 中英文
- [ ] 不改现有 API 契约；`npm run build` + `npm test` 通过

**截图回归**
- [ ] Home：双机架 + 流程条可读
- [ ] Upload：拖拽三态清晰
- [ ] Overview：机架错落通电，A/B 播放反馈明确
- [ ] Charts：四卡一致、loading 优雅
- [ ] History：行交互不破坏表格布局

---

## 第八部分：i18n 键清单（示例，实施时补全）

| 键 | zh | en |
|----|----|----|
| `motionReduced` | 减少动效 | Reduce motion |
| `flowUploadHint` | 上传音频文件 | Upload audio |
| `sceneVaultTitle` | 场景库 | Scene vault |
| `sceneLoadUpload` | 加载到上传 | Load to upload |
| `metricsTheaterTitle` | 指标剧场 | Metrics theater |
| `spectralDiffTitle` | 频谱对比 | Spectral diff |
| `reportDeskTitle` | 报告导出 | Report export |
| `reportDownloadMd` | 下载 Markdown | Download Markdown |
| `batchCompareTitle` | 批量对比 | Batch compare |
| `settingsTitle` | 设置 | Settings |
| `settingsMotion` | 动效 | Motion |
| `onboardingSkip` | 跳过引导 | Skip tour |
| `navMore` | 更多 | More |
| `wayfindCharts` | 查看频谱 | View spectra |
| `wayfindCinema` | 影院试听 | Cinema listen |

---

## 第九部分：性能与测试要点

1. **Profiler：** Overview 首屏 LCP 不因 Observer 增加 >100ms
2. **Canvas：** 单页最多 2 个 rAF loop（Scope + MiniScope）；离屏暂停
3. **Plotly：** 懒加载 `react-plotly.js` 已有；Spectral 页勿重复 mount 4 实例
4. **测试：** 扩 `ABXTestPanel.test.tsx` 或加 `HomePage` smoke：taskId 传入后 MOD-HS01 渲染
5. **E2E（可选）：** Upload 拖拽 → Progress LED → Overview 播放 → VU 变化截图对比

---

## 第十部分：一句话版（快速粘贴）

> 在 Signal Console 全站建立 Signal Motion System（分级转场、机架通电、数据驱动 VU/LED、背景与播放/ processing 联动），并按截图精修 Home/Upload/Overview/Charts/History 动效；新增 Scene Vault、Metrics Theater、Spectral Diff、Report Desk、Settings（+ 可选 Batch Compare、Onboarding）；纯 CSS+Canvas、复用 RackPanel/HeadphoneRackUnit/pointerStore，不改 API，i18n+build+test 通过。

---

## 相关文档

- 机架语言：`signal-console-ui-polish.md`
- 背景互动：`background-mouse-interaction.md`
- Showcase 初版：`signal-console-showcase-pages.md`
- Showcase 精修：`signal-console-showcase-polish.md`
- 监听单元：`signal-console-headphone-module.md`
- 建议版本标签：`web-signal-console-motion-pages`
