# AI 提示词：Denoise Studio Signal Console — 炫酷展示页扩展

> 复制整段给 Cursor / Claude。在 **已上线的 Signal Console + RackPanel + 互动背景** 基础上**新增展示路由**，不要推倒重来业务页。  
> 前置版本：`web-signal-console-rack-polish`（机架精修）、`web-signal-console-interactive`（背景互动）。

---

## 角色与目标

你是资深创意前端工程师 + 音频可视化方向，为 **Denoise Studio** 增加若干**炫酷但克制**的展示页面，用于：

1. **演示平台能力**（算法矩阵、链路路由、指标剧场、A/B 影院）
2. **强化品牌记忆点**（广播调音台、机架模块、示波器、VU 表——不是通用 SaaS 仪表盘）
3. **与现有工作流衔接**（可从 Home / Overview 跳入，有 task 时读真数据，无 task 时用 demo 态）

**「炫酷」在本项目中的定义：**

| ✅ 要做 | ❌ 禁止 |
|--------|--------|
| 机架模块阵列、LED 脉冲、LCD 读数滚动 | 紫色渐变、霓虹赛博、毛玻璃泛滥 |
| Canvas 示波器 / 频谱 / 路由动画 | Three.js 大场景、粒子风暴屏保 |
| 鼠标视差与背景联动（复用 `useStudioPointer`） | 每帧 React setState 全页重绘 |
| 大字号 Antonio 标题 + mono 数据层 | Inter / Roboto / Space Grotesk |
| 真实 API 数据 + 优雅空状态/demo | 假数据硬编码冒充已完成任务 |

---

## 现有资产（必须复用，勿重复造轮子）

| 资产 | 路径 | 用途 |
|------|------|------|
| 机架卡片 | `components/RackPanel.tsx` | 所有展示区块顶栏 `MOD-xx / CHANNEL` + LED |
| 背景层 | `AmbientBackground.tsx`、`ScopeCanvas.tsx`、`useStudioPointer.ts` | 全站氛围；展示页可增强局部 Canvas，不替换全局背景 |
| 指针 store | `lib/pointerStore.ts` | Canvas 读取 `--pointer-x/y` 做振幅/相位调制 |
| 算法清单 | `lib/methodOptions.ts` | Algorithm Atlas 数据源 |
| 管线工具 | `lib/pipelineUtils.ts` | 失配检测、Task ID 缩写 |
| Plotly 主题 | `lib/plotTheme.ts` | 图表子区配色 |
| 样式体系 | `tokens.css`、`studio-console.css`、`rack-polish.css`、`home.css` | 新页写 `showcase.css`，变量只引用 token |
| i18n | `i18n/index.ts` | 中英文键 |

**当前路由（业务，保持不动）：** `/` `/upload` `/progress` `/overview` `/charts` `/history`

**本次新增路由（展示专区）：**

```
/showcase              → ShowcaseHubPage      展示入口 / 模块导航
/showcase/algorithms   → AlgorithmAtlasPage   算法机架阵列
/showcase/pipeline     → PipelineTheaterPage  链路剧场（路由动画）
/showcase/monitor      → SignalMonitorPage    指标遥测大屏
/showcase/cinema       → CompareCinemaPage    沉浸式 A/B 试听影院
```

导航：在 `GlassNav.tsx` 增加一项 **「展示」**（`navShowcase`），或 Home 底部增加「进入 Signal Lab」入口；展示子页可用二级 tab，不必全部塞进顶栏。

---

## 技术约束（必须遵守）

| 项 | 要求 |
|----|------|
| 路径 | 主要改 `analysis/denoise_selection/webapp/frontend/` |
| 栈 | React 18 + TS + Vite，纯 CSS（新建 `styles/showcase.css`） |
| 禁止 | Tailwind、MUI、Ant Design、紫色渐变、Inter/Roboto |
| 字体 | Antonio（Display）+ Newsreader（正文）+ Fragment Mono（数据） |
| API | **可**在 `api.ts` 只读调用现有接口；**禁止**改后端契约 |
| 路由 | **可**扩展 `app/router.tsx`；保持业务路由 path 不变 |
| 性能 | Canvas `requestAnimationFrame`；DPR cap 2；`prefers-reduced-motion` 静态降级 |
| 测试 | `npm run build` + `npm test` 通过 |
| i18n | 所有可见文案写入 `src/i18n/index.ts` 中英文键 |

---

## 全局展示语言（Design System 扩展）

在 `tokens.css` 或 `showcase.css` 增加展示语义 token（勿硬编码色值）：

```css
--showcase-hero-size: clamp(2.8rem, 8vw, 5rem);
--showcase-glow: var(--signal-glow);
--showcase-grid-gap: 20px;
--showcase-canvas-fade: linear-gradient(90deg, transparent, black 8%, black 92%, transparent);
--showcase-demo-badge: var(--amber);
```

**共享组件（建议新建）：**

```tsx
// components/showcase/ShowcaseHero.tsx
// props: eyebrow, title, lede, actions — 复用 home.css 的 console-eyebrow/title 变体

// components/showcase/RackModuleGrid.tsx
// props: modules: { id, channel, label, led, hint }[] — 响应式机架网格

// components/showcase/LcdTicker.tsx
// props: lines: string[] — mono 滚动读数（CSS animation，reduced-motion 静止）

// components/showcase/MiniScope.tsx
// props: variant: 'signal'|'amber', height — 轻量 Canvas，逻辑可参考 ScopeCanvas 精简版

// components/showcase/VuMeterBar.tsx
// props: value 0-1, label — 纵向/横向 VU，processing 时脉冲
```

**页面壳：** 所有展示页外包一层 `showcase-page stagger`，顶区用 `ShowcaseHero`，内容区用 `RackPanel` 分模块。

---

## 页面规格（按优先级）

### P0 — `/showcase` Showcase Hub（展示入口）

**目标：** 像调音台背板的「功能选择区」，一眼看到 4 个子模块，戏剧感不低于 Home。

**布局：**

```
┌─────────────────────────────────────────────────────┐
│  EYEBROW: SIGNAL LAB · MOD-SHOWCASE                 │
│  大标题: SIGNAL LAB（Antonio 全大写）                  │
│  副文案 + CTA「开始分析」/「用当前任务探索」              │
├──────────────────────┬──────────────────────────────┤
│  MOD-S00 / NAV       │  2×2 bento 导航卡（带 MiniScope）│
│  当前 task 摘要 LCD   │  → Algorithms / Pipeline /    │
│  （有 task 显示缩写 ID）│     Monitor / Cinema          │
└──────────────────────┴──────────────────────────────┘
```

**交互：**

- 四张 bento 卡 hover：边框 `--panel-border-strong` + 底部 MiniScope 振幅略增（读 pointer）
- 有 `taskId` 时 LCD 显示 `method · route`；无 task 显示 demo 文案 + 链到 `/upload`
- 背景：保持全局 `AmbientBackground`，本页可在 hero 后加一层淡 `studio-scanline`

**文件：** `pages/showcase/ShowcaseHubPage.tsx`、`styles/showcase.css`

---

### P0 — `/showcase/algorithms` Algorithm Atlas（算法机架阵列）

**目标：** 把 `METHOD_OPTIONS` 可视化成**机架模块墙**，比 Upload 下拉更有「硬件目录」感。

**布局：**

- 顶栏 `RackPanel` `MOD-S01 / ATLAS`
- 按 `METHOD_GROUP_ORDER` 分 4 组：`GRP-REC` / `GRP-MATH` / `GRP-DL` / `GRP-BASE`
- 每组内卡片：`method value` mono + `labelKey` 标题 + `hintKey` 折叠 hint（LCD 样式）
- 选中项：左侧 2px `--signal` 条 + LED `active`；其余 `idle`

**炫酷点：**

1. 点击模块：右侧「规格抽屉」滑出（纯 CSS `transform`，非 MUI Drawer）显示 hint 全文
2. 选中 `deepfilter` 时顶部固定琥珀 `ENV` 条：`DEEPFILTER_CONDA_ENV=dfnet311`
3. 组标题旁 `MiniScope` 随组内选中项变化频率（纯视觉，非真实 DSP）

**数据：** 仅前端 `methodOptions.ts` + i18n，不调 API。

**文件：** `pages/showcase/AlgorithmAtlasPage.tsx`、`components/showcase/RackModuleGrid.tsx`

---

### P1 — `/showcase/pipeline` Pipeline Theater（链路剧场）

**目标：** 用动画解释「音频如何从 INPUT → 算法链 → OUTPUT」，强化 method/route/reason 认知。

**布局：**

- `RackPanel` `MOD-S02 / ROUTE`
- 横向「信号流」SVG 或 CSS 管线：节点圆角方盒 + mono 标签
- 下方「场景预设」胶囊：`Auto` / `DeepFilter` / `OM-LSA` / `WPE` / `Baseline`（切换 demo 路由表）

**炫酷点：**

1. 切换预设时：节点依次点亮（stagger 80ms），LED 从 `idle`→`processing`→`active`
2. 信号 dot 沿管线移动（CSS `offset-path` 或 rAF 更新 `transform`）
3. 若有当前 `taskId`：增加「加载真实链路」按钮，调 `getMetrics` / `getHistory` 填充 route + reason；失配时顶栏 `rack-panel-alert`

**Demo 路由表示例（可放 `lib/showcasePresets.ts`）：**

```ts
export const PIPELINE_PRESETS = [
  { id: "auto", route: ["analyze", "route", "denoise", "metrics"], reason: "scene-adaptive" },
  { id: "deepfilter", route: ["deepfilter", "metrics"], reason: "DeepFilterNet3" },
  // ...
];
```

**文件：** `pages/showcase/PipelineTheaterPage.tsx`、`lib/showcasePresets.ts`、`styles/showcase.css`（`.pipeline-theater-*`）

---

### P1 — `/showcase/monitor` Signal Monitor（指标遥测大屏）

**目标：** 把 Overview 的 8 个指标做成**演播室监视器墙**，适合答辩/demo 投屏。

**布局：**

- 全宽 `RackPanel` `MOD-S03 / TELEMETRY`
- 2×4 `metric-readout` 大数字（复用 `rack-polish.css`），数值用 `font-display` 1.8rem+
- 每格底部 `VuMeterBar` 用指标归一化值驱动（无数据时 demo 正弦摆动）
- 底栏 `LcdTicker` 滚动：`sample_rate` / `length_sec` / `method` / `route`

**数据策略：**

| 状态 | 行为 |
|------|------|
| 有 `taskId` 且 completed | `getMetrics(taskId)` 真数据 |
| 有 task 未完成 | 显示 processing + 轮询 `getTask` |
| 无 task | demo 数值 + 徽章 `DEMO`（琥珀） |

**炫酷点：**

- 数字变化时短暂 `signal-glow` flash（CSS keyframes，150ms）
- 可选：从 Plotly payload 挑 1 张频谱图嵌小窗（`getPlots`，懒加载）

**文件：** `pages/showcase/SignalMonitorPage.tsx`、`components/showcase/VuMeterBar.tsx`、`LcdTicker.tsx`

---

### P2 — `/showcase/cinema` Compare Cinema（A/B 试听影院）

**目标：** 全屏沉浸试听，比 Overview 的 `AudioComparePlayer` 更有「放映室」感。

**布局：**

- 页面级 `showcase-cinema`：减少 `page-shell` 左右 padding（`showcase.css` 覆盖）
- 顶栏极简：文件名 + `StatusBadge` + 退出「返回 Overview」
- 中央：双波形叠层或左右分屏（WaveSurfer 两实例，或静态波形图 + 进度条）
- 底部：**大型**调音台推子条（复用 `mixer-strip` 样式放大），A/B/R 三轨
- 两侧：纵向 VU 表（`VuMeterBar` 竖版）

**数据：** `audioUrl(taskId, kind)`；无 task 时全页空状态 + CTA `/upload`。

**炫酷点：**

1. 播放时背景 `studio-atmosphere-processing` 类联动（已有 hook，传 taskId）
2. 切换 A/B 时 15ms crossfade（复用 `AudioComparePlayer` 逻辑，抽 `lib/audioCrossfade.ts`）
3. 空格键 play/pause，`1`/`2`/`3` 切轨（`useEffect` keyboard，focus 在页面容器）

**文件：** `pages/showcase/CompareCinemaPage.tsx`；可重构 `AudioComparePlayer` 共享逻辑，**勿破坏** Overview 现有行为。

---

## 路由与导航改动清单

```tsx
// app/router.tsx — 新增（保持原 Route 不变）
import ShowcaseHubPage from "../pages/showcase/ShowcaseHubPage";
// ...

<Route path="/showcase" element={<ShowcaseHubPage taskId={taskId} />} />
<Route path="/showcase/algorithms" element={<AlgorithmAtlasPage />} />
<Route path="/showcase/pipeline" element={<PipelineTheaterPage taskId={taskId} />} />
<Route path="/showcase/monitor" element={<SignalMonitorPage taskId={taskId} />} />
<Route path="/showcase/cinema" element={<CompareCinemaPage taskId={taskId} />} />
```

```tsx
// GlassNav.tsx — navPaths 增加（建议放 History 前）
{ to: "/showcase", key: "navShowcase", end: false }
```

```tsx
// HomePage.tsx — console-actions 或 console-bento 下增加
<Link to="/showcase" className="console-cta-ghost">{t("homeEnterShowcase")}</Link>
```

**二级导航（展示区内）：** 新建 `components/showcase/ShowcaseSubNav.tsx`，在 5 个 showcase 页顶部共享，active 底边 2px `--signal`。

---

## 动效与性能规范

1. **Canvas：** 与 `ScopeCanvas.tsx` 一致——单 rAF 循环、resize observer、tab hidden 时 pause
2. **视差：** 展示页局部动效优先读 `pointerStore` 或 CSS 变量，禁止鼠标移动触发父组件 re-render
3. **Reduced motion：** 关管线 dot 移动、关 ticker 滚动、关 LED blink，保留静态布局与数据
4. **移动端：** `<768px` 机架网格改 1 列；Cinema 改单列推子；Monitor 改 2×2
5. **无障碍：** 键盘可聚焦 bento 卡；Cinema 有 `aria-live` 播放状态；装饰 Canvas `aria-hidden`

---

## 建议实施顺序（可分 PR）

1. **基础设施：** `showcase.css`、`ShowcaseSubNav`、`router` + `GlassNav` + i18n 键骨架
2. **Showcase Hub**（最快建立「展示区」存在感）
3. **Algorithm Atlas**（纯前端，无 API 依赖）
4. **Pipeline Theater**（preset + 可选真 task 链路）
5. **Signal Monitor**（接 API，demo 回退）
6. **Compare Cinema**（重构音频逻辑需谨慎，最后做）
7. `npm run build && npm test` + 中英文浅色/深色截图

---

## 验收标准

- [x] 5 条 showcase 路由可访问，二级导航高亮正确
- [x] 视觉与 Home / Upload / Overview 共用 RackPanel + token，无新 UI 框架
- [x] 浅色 / 深色下展示页对比度清晰，正文 ≥ 4.5:1
- [x] 无 task 时各页有明确 demo/空状态，不报错
- [x] 有 completed task 时 Monitor / Pipeline / Cinema 可展示真 method/route/metrics/audio
- [x] 动效在 reduced-motion 下合理降级；移动端无严重卡顿
- [x] `npm run build` + `npm test` 通过
- [x] 禁止紫色渐变、Inter、重型 3D 库

---

## i18n 键清单（需新增，示例）

| 键 | zh | en |
|----|----|----|
| `navShowcase` | 展示 | Showcase |
| `homeEnterShowcase` | 进入 Signal Lab | Enter Signal Lab |
| `showcaseHubTitle` | Signal Lab | Signal Lab |
| `showcaseHubSubtitle` | 算法机架 · 链路剧场 · 遥测监视 · 试听影院 | Algorithm rack · Pipeline theater · Telemetry · Cinema |
| `showcaseAlgoTitle` | 算法机架图鉴 | Algorithm Atlas |
| `showcasePipelineTitle` | 链路剧场 | Pipeline Theater |
| `showcaseMonitorTitle` | 信号遥测 | Signal Monitor |
| `showcaseCinemaTitle` | 试听影院 | Compare Cinema |
| `showcaseDemoBadge` | 演示数据 | Demo data |
| `showcaseLoadTask` | 载入当前任务 | Load current task |
| `showcaseNoTask` | 暂无任务，请先上传分析 | No task yet — upload first |

（实现时按页面补充，保持中英文键对称。）

---

## 一句话版（快速粘贴）

> 在 Denoise Studio Signal Console 上新增 /showcase 展示区：Hub 入口 + Algorithm Atlas 机架墙 + Pipeline Theater 路由动画 + Signal Monitor 指标大屏 + Compare Cinema 沉浸 A/B；复用 RackPanel/ScopeCanvas/useStudioPointer/plotTheme，纯 CSS+Canvas，可扩展 router 与 i18n，禁止 Tailwind/紫色渐变/Three.js；有 task 读真 API，无 task demo 态；build+test 通过。

---

## 相关文档

- 背景互动：`docs/prompts/background-mouse-interaction.md`
- 机架精修：`docs/prompts/signal-console-ui-polish.md`
- 启动：`start-webapp.bat` / `start-webapp.ps1`
- 建议版本标签：`web-signal-console-showcase`
