# AI 提示词：Denoise Studio Signal Console — Showcase 展示区精修（基于当前截图）

> 复制整段给 Cursor / Claude。在 **已上线的 `/showcase` 五页 + Signal Lab Hub** 基础上迭代，不要推倒重来。  
> 参考截图：Signal Lab Hub、Pipeline Theater（Auto / DeepFilter / OM-LSA / WPE / Load Current Task 多态）。  
> 前置版本：`web-signal-console-showcase`（展示区初版）、`web-signal-console-rack-polish`（业务页机架化）。

---

## 角色与目标

你是资深创意前端工程师，负责 **Denoise Studio Showcase（Signal Lab）** 的**信息层级、动效完整性、与业务页一致性**提升。

**当前优点（必须保留）：**
- Signal Lab Hub：2×2 bento + MiniScope 波形、MOD-S00 任务 LCD、二级 sub-nav
- Pipeline Theater：预设胶囊 + 横向节点流 + Load Current Task 读真 route/reason
- 全局：RackPanel 顶栏、浅色 Liquid Glass、背景网格/示波器、磷光青 `--signal`
- 技术栈：纯 CSS + Canvas，无 Tailwind / 紫色渐变

**截图暴露的核心问题：**
1. **Pipeline 的 `OUTPUT` 节点永远半透明**（最长链路也只亮到 `metrics`，OUTPUT 不点亮）
2. **子页 Hero 区过高、信息重复**（每页都大写 `PIPELINE THEATER` + 同一 eyebrow `SIGNAL LAB · MOD-SHOWCASE`）
3. **Load Current Task 后预设按钮全部失活**，用户不知道当前链路对应哪类场景
4. **任务 LCD / Details 条视觉权重不足**，不像机架 LCD 读数
5. **Hub bento 四卡同质**，缺少模块个性（颜色/图标/动效差异）
6. **展示区与业务页联动弱**（仅 Monitor 有 Explore；Pipeline/Cinema 无快捷入口）

**本次目标：** 让 Showcase 从「能演示」升级为「答辩可投屏、链路一眼读懂、真任务与 demo 态可区分」。

---

## 技术约束（必须遵守）

| 项 | 要求 |
|----|------|
| 路径 | 主要 `analysis/denoise_selection/webapp/frontend/` |
| 栈 | React 18 + TS + Vite，纯 CSS（`showcase.css` 等） |
| 禁止 | Tailwind、MUI、紫色渐变、Inter/Roboto、Three.js |
| 字体 | Antonio + Newsreader + Fragment Mono |
| API | 只读现有 `api.ts`；不改后端 |
| 路由 | 保持现有 5 条 showcase path；可改组件 props |
| 测试 | `npm run build` + `npm test` 通过 |
| i18n | 新增文案写入 `src/i18n/index.ts` 中英文键 |

---

## 截图诊断 — 待改进清单（按优先级）

### P0 — Pipeline Theater：`OUTPUT` 节点与动画逻辑（截图 2–6 共性 BUG）

**现象：** 无论 Auto（4 步）、DeepFilter（2 步）还是 Load Task，**`OUTPUT` 始终 `opacity: 0.45`**，像链路未完成。

**根因（`PipelineTheaterPage.tsx`）：**
- `nodes = ["INPUT", ...route, "OUTPUT"]`，共 `route.length + 2` 个节点
- `litCount` 最大只到 `route.length`（预设动画 `steps = p.route.length`；Load Task 设 `litCount = route.length`）
- 判断 `idx <= litCount` 时，**最后一个 OUTPUT 索引 `route.length + 1` 永远不会亮**

**改进：**
1. 统一「点亮总数」：`totalLit = route.length + 2`（含 INPUT 与 OUTPUT），或动画结束后显式 `setLitCount(nodes.length - 1)`
2. 预设切换 / Load Task 均走同一 `animatePipeline(nodeCount)` 辅助函数（stagger 80ms，末步点亮 OUTPUT）
3. OUTPUT 亮起时：节点盒 `border-color: var(--panel-border-strong)` + LED `active` + 可选 150ms `signal-glow` flash
4. 连接器：每段管线在「前节点已亮且后节点已亮」时显示 dot；长链路支持 **多颗 dot 错峰**（CSS `animation-delay` 递增）
5. Load Task 成功后：**重播动画**，不要瞬间跳满（截图中 Load 后中间态不清晰）

**文件：** `PipelineTheaterPage.tsx`、`showcase.css`（`.pipeline-node-output`、`.pipeline-flow-complete`）

---

### P0 — Load Task 与预设的状态机（截图 6）

**现象：** 点击 **LOAD CURRENT TASK** 后，Auto/DeepFilter 等预设全部灰掉，仅 Details 显示 `from current task`，用户无法对比「场景预设 vs 真实链路」。

**改进：**
1. 引入三态：`mode: "preset" | "task" | "compare"`
2. `task` 模式：预设按钮降透明度但仍可点击；点击预设切回 preset 并提示 toast/inline：`showcaseSwitchedToPreset`
3. `task` 模式：在 Details LCD 旁加琥珀徽章 **`LIVE`**（真任务）vs 预设模式 **`SIM`**（模拟）
4. Load Task 按钮在 `mode === "task"` 时改为 **`showcaseReloadTask`**（刷新动画）
5. 若 `isDeepfilterMismatch(method, route, reason)`：`RackPanel` `alert` + Details 行红色 + 顶部一行 `pipelineMismatchHint`（复用 Overview 文案）

**文件：** `PipelineTheaterPage.tsx`、`pipelineUtils.ts`（如需）、`i18n`

---

### P1 — 子页 Hero 瘦身与信息架构（截图 2–6）

**现象：** Pipeline / Atlas / Monitor / Cinema 顶部结构重复：
`SubNav` → 大 eyebrow `SIGNAL LAB · MOD-SHOWCASE` → 巨型页标题 → 副标题，**首屏 RackPanel 被挤到视口下沿**。

**改进 — 新建 `ShowcasePageHeader`（或扩展 `ShowcaseHero`）：**

```tsx
// props: variant: "hub" | "inner", moduleId, channel, title, subtitle?, actions?
```

| 页面 | variant | 顶区内容 |
|------|---------|----------|
| `/showcase` Hub | `hub` | 保持现有大 Hero + CTA |
| 子页 | `inner` | 仅一行：`MOD-S02 / ROUTE` mono + 紧凑标题（1.6rem）+ 可选副标题一行；**去掉**重复 eyebrow |

- 子页 `showcase-page` 的 `gap` 从 24px → 16px；`stagger` 子项 delay 减半（展示区切换更利落）
- Sub-nav 链接旁加 mono 编号：`HUB` `S01` `S02` `S03` `S04`（与 bento `MOD-Sxx` 对齐）

**文件：** `ShowcaseHero.tsx` 或新 `ShowcasePageHeader.tsx`、各 `pages/showcase/*`、`showcase.css`

---

### P1 — Signal Lab Hub（截图 1）

| 问题 | 方案 |
|------|------|
| 任务 LCD 仅一行 mono 字 | 拆为三行：**ID** / **method** / **route**；右侧 `StatusBadge`；deepfilter 失配时 LCD 左边 2px 红条 |
| bento 四卡视觉同质 | 每卡左上角色条：S01 `--signal`、S02 `--amber`、S03 青绿渐变条、S04 双色 A\|B 分割；hover 时 MiniScope `freqMul` 略增 |
| CTA 单一 | `Explore with current task` 改为 **下拉或双按钮**：`→ Monitor` `→ Pipeline`（有 taskId 时） |
| MOD-S00 与 bento 高度失衡 | 大屏下左侧 NAV 卡与右侧 2×2 **底对齐**；`<960px` 保持单列 |

**文件：** `ShowcaseHubPage.tsx`、`showcase.css`

---

### P1 — Algorithm Atlas（未在截图中，按初版代码审查）

| 问题 | 方案 |
|------|------|
| 右侧 drawer 空态不明显 | 默认选中 `auto` 且 drawer `is-open`；未选时显示 LCD 占位 `showcaseAlgoPick` |
| 移动端 drawer 在下方 | `<960px` drawer 改为选中模块**下方折叠面板**（`collapse-panel` 复用 Charts 样式） |
| 与 Upload 联动 | 底部 CTA：**「以此方法去上传」** → `/upload` 并通过 `sessionStorage` 预填 method（只写 frontend，不改 API） |

**文件：** `AlgorithmAtlasPage.tsx`、`showcase.css`

---

### P1 — Signal Monitor

| 问题 | 方案 |
|------|------|
| 无 task 时 empty + 全网格同时出现 | 无 task：**仅** empty 机架插画；有 task 未完成：仅 VU 脉冲 + `processing` LED，数值显示 `—` |
| DEMO 徽章位置弱 | 固定在 `MOD-S03` 顶栏右侧，与 Rack LED 并排 |
| 真数据刷新无感知 | 指标变化保留 `is-flash`；**同时** LcdTicker 重置滚动 |
| 答辩投屏模式 | 可选按钮 **「投屏」**：`showcase-monitor--present` 类隐藏 sub-nav、放大 `monitor-value` 至 2.4rem |

**文件：** `SignalMonitorPage.tsx`、`showcase.css`

---

### P2 — Compare Cinema

| 问题 | 方案 |
|------|------|
| 与 Overview 试听重复感强 | Cinema 默认**隐藏** sub-nav + 全宽；顶栏只留文件名 + 播放状态 + 返回 |
| 键盘提示不可见 | 底部固定 mono 条：`SPACE · 1/2/3`；首次进入 3s 高亮后淡出 |
| 波形仅两条 | 中央增加 **Residual** 第三轨折叠区（默认收起，点「R」展开） |
| 播放时 VU 随机跳动 | 改为随 `audio.timeupdate` 驱动的伪电平（无需 Web Audio API） |

**文件：** `CompareCinemaPage.tsx`、`audioCrossfade.ts`（可抽 `useCompareTransport` hook）

---

### P2 — 导航与全局

| 问题 | 方案 |
|------|------|
| 顶栏 SHOWCASE 与 sub-nav 双层高亮 | 主 nav 的 `/showcase` active 仅 **底边 2px 线**，去掉整块 `--signal-dim` 填充（sub-nav 负责区内高亮） |
| Hub 与 Home 入口重复 | Home「进入 Signal Lab」保留；Hub 内增加 **「返回工作台」** ghost 链到 `/overview` |
| 页面切换动画 | showcase 子路由间禁用 `page-route` 8px slide（仅业务路由保留），避免 Hero 重复滑入眩晕 |
| 无障碍 | Pipeline 节点加 `aria-label`；Load Task 后 `aria-live` 播报 route 摘要 |

**文件：** `GlassNav.tsx`、`studio-console.css` 或 `glass.css`、`AppShell.tsx`（按 pathname 条件 class）

---

### P2 — 浅色主题微调（截图均为 Light）

- `pipeline-flow` 内层底：略加深 `var(--bg-elevated)`，与外层 RackPanel 区分
- `pipeline-preset-btn.is-active`：加 `box-shadow: 0 0 12px var(--signal-glow)`，与截图里选中态不够醒目对齐
- `showcase-task-lcd` / `pipeline-reason-lcd`：统一为 Upload 的 `method-lcd` 字色与内边距
- bento 卡 `box-shadow` 在 light 下再加深 1 级（与 `rack-polish` 业务卡一致）

**文件：** `showcase.css`、`tokens.css`（仅 `[data-theme="light"]` 展示语义变量）

---

## 建议共享重构（减少重复）

```ts
// lib/showcasePipelineAnim.ts
export function animatePipelineSteps(
  stepCount: number,
  onStep: (litIndex: number) => void,
  intervalMs = 80,
): () => void;

// hooks/useShowcaseTask.ts
// 封装 getHistory + getMetrics + getTask，返回 { task, metrics, method, route, reason, mismatch, loading }
```

**Compare 与 Overview 共用：**

```ts
// hooks/useCompareTransport.ts — 从 AudioComparePlayer + CompareCinemaPage 抽出
```

---

## 设计 token 补充（`showcase.css`）

```css
--showcase-sim-badge: var(--amber);
--showcase-live-badge: var(--signal);
--showcase-inner-title: clamp(1.4rem, 4vw, 2rem);
--showcase-pipeline-complete-glow: var(--signal-glow);
```

---

## 建议实施顺序（可分 commit）

1. **P0 Pipeline OUTPUT 点亮 + 动画统一 + Load Task 重播**（截图最明显 BUG）
2. **P0 task/preset 三态 + LIVE/SIM 徽章 + 失配告警**
3. **P1 子页 Hero 瘦身 + Sub-nav MOD 编号**
4. **P1 Hub 任务 LCD + bento 差异化**
5. **P1 Monitor 空态 / 投屏模式**
6. **P2 Cinema 沉浸态 + 导航高亮降噪**
7. `npm run build && npm test` + 中英文截图对比（重点 Pipeline 末节点、Load Task）

---

## 验收标准

- [x] Pipeline 任意预设与 Load Task 后，**INPUT → 全 route → OUTPUT** 依次点亮，OUTPUT 不再半透明
- [x] Load Task 后仍有预设可切换，且 LIVE/SIM 状态可辨
- [x] deepfilter 失配时 Pipeline 顶栏红色告警与 Overview 一致
- [x] 子页首屏可见完整 RackPanel（Hero 不占超过 35vh）
- [x] Hub 任务区显示 status；bento 四卡可一眼区分
- [x] Monitor 无 task 不出现 demo 数字墙；有 task 可投屏放大
- [x] Cinema 全宽沉浸、键盘提示可见、不影响 Overview 原有试听
- [x] `npm run build` + `npm test` 通过；无新 UI 框架

---

## i18n 键清单（示例）

| 键 | zh | en |
|----|----|----|
| `showcaseSubNavHub` | 枢纽 | Hub |
| `showcaseSimBadge` | 模拟 | SIM |
| `showcaseLiveBadge` | 实况 | LIVE |
| `showcaseReloadTask` | 重新载入 | Reload task |
| `showcaseSwitchedToPreset` | 已切换为场景预设 | Switched to scene preset |
| `showcaseGoUploadWithMethod` | 用此方法上传 | Upload with this method |
| `showcasePresentMode` | 投屏模式 | Present mode |
| `showcaseBackWorkbench` | 返回工作台 | Back to workbench |
| `showcasePipelineComplete` | 链路就绪 | Pipeline ready |

---

## 一句话版（快速粘贴）

> 精修 Denoise Showcase：修复 Pipeline OUTPUT 永不点亮与 Load Task 动画/状态机，子页 Hero 瘦身+MOD 编号，Hub LCD/ bento 差异化，Monitor 投屏与空态，Cinema 沉浸与键盘提示，LIVE/SIM 徽章与 deepfilter 失配告警；只改 frontend showcase 相关文件，保持 Signal Console 风格，build+test 通过。

---

## 相关文档

- 展示区初版：`docs/prompts/signal-console-showcase-pages.md`
- 业务机架精修：`docs/prompts/signal-console-ui-polish.md`
- 背景互动：`docs/prompts/background-mouse-interaction.md`
- 建议版本标签：`web-signal-console-showcase-polish`
