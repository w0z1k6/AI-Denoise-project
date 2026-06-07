# AI 提示词：Denoise Studio Signal Console — 降噪耳机模块（机架化融入）

> 复制整段给 Cursor / Claude。在 **已上线的 Signal Console + RackPanel + Signal Lab** 基础上，将用户提供的**新拟物降噪耳机卡片**融入为**机架监听单元**，禁止做成独立「消费电子产品」落地页。  
> 参考素材：下方「源 CSS」；前置版本：`web-signal-console-showcase-polish`。

---

## 角色与目标

你是资深创意前端工程师 + 硬件 HMI 方向，负责把「降噪耳机」视觉**自然嵌入** Denoise Studio 的**广播机架 / Signal Console** 语言，而不是贴一张违和的拟物插图。

**核心原则 — 不违和 = 有语义、有边框、有状态：**

| ✅ 正确融入 | ❌ 违和做法（历史曾回退） |
|------------|-------------------------|
| 作为 **Rack 模块** `MOD-HS01 / MONITOR` 嵌在 Home / Cinema / ABX 侧边 | 全屏居中巨大耳机、盖住示波器背景 |
| LED / 腔体 / 头梁线 **绑定播放、处理、ABX 状态** | 纯装饰、与业务无关的绿色 `#66f66f` 常亮 |
| 颜色全部走 **`tokens.css`**（`--signal` / `--amber` / `--rack-*`） | 硬编码 `#e8e9eb`、`#66f66f` 原样粘贴 |
| 外框用 **`RackPanel` 或 `console-module` 壳**，与 MOD-01 统计卡同级 | 单独 floating card，阴影风格与 Glass 冲突 |
| 深色 / 浅色主题双适配，对比度 AA | 仅浅灰新拟物，暗色下发脏 |

**产品叙事（文案层）：**  
这不是「卖耳机」，而是调音台上的 **「参考监听 / ANC 试听单元」** —— 用户戴耳机做 ABX、对比降噪前后，与 `AudioComparePlayer`、`CompareCinema` 同一工作流。

---

## 技术约束（必须遵守）

| 项 | 要求 |
|----|------|
| 路径 | 仅 `analysis/denoise_selection/webapp/frontend/` |
| 栈 | React 18 + TS + Vite，纯 CSS（新建 `styles/headphone-rack.css`） |
| 禁止 | Tailwind、MUI、紫色渐变、Inter/Roboto、Three.js、原 CSS 数值照搬 |
| 字体 | Antonio（标签）+ Fragment Mono（MOD 编号）+ Newsreader（说明） |
| API/路由 | 不改 `api.ts`、`router.tsx`；可接 `taskId`、播放状态 props |
| 复用 | `RackPanel`、`rack-led-*`、`useBackgroundMotion`（processing 类）、`pointerStore`（可选微倾） |
| 测试 | `npm run build` + `npm test` 通过 |
| i18n | 文案键写入 `src/i18n/index.ts` 中英文 |

---

## 源素材（用户提供 — 仅作结构参考，必须 token 化）

```html
<!-- 结构语义：耳罩壳体 + 头梁分割线 + 腔体开孔 + 状态 LED + 标签 -->
<div class="card">
  <div class="line"></div>
  <div class="cavity"></div>
  <div class="led"></div>
  <div class="text">ANC</div>
</div>
```

```css
/* 源样式 — 禁止直接复制 box-shadow 色值；保留几何比例思路 */
.card {
  width: 270px;
  height: 220px;
  background-color: #e8e9eb;
  border-radius: 70px;
  /* 多层 inset + 外阴影 → 改写为 --hp-shell-shadow */
}
.card .line { /* 头梁横线 */ }
.card .cavity { /* 耳罩腔体渐变槽 */ }
.card .led { /* 原 #66f66f → 改为 var(--signal) */ }
.card .text { /* 原淡灰字 → 改为 mono 机架标 */ }
```

**保留的几何特征：** 大圆角耳罩轮廓（`border-radius: 70px` 量级）、横向头梁线、中央腔体槽、单点 LED。  
**必须改写的特征：** 背景灰、绿色 LED、过重新拟物阴影、固定 270×220 在移动端溢出。

---

## 设计系统映射（`headphone-rack.css` + `tokens.css`）

在 `tokens.css` 增加耳机语义变量（深浅主题分别定义）：

```css
--hp-shell-bg: var(--bg-elevated);
--hp-shell-border: var(--panel-border);
--hp-shell-shadow: var(--glass-shadow);
--hp-cavity-bg: linear-gradient(180deg, var(--bg-surface), var(--bg-elevated));
--hp-line: var(--panel-border);
--hp-label: var(--text-tertiary);
--hp-led-on: var(--signal);
--hp-led-glow: var(--signal-glow);
--hp-led-warn: var(--amber);
--hp-led-fault: var(--danger);
--hp-aspect: 270 / 220; /* 比例锁，非固定 px */
```

| 源 CSS | Signal Console 映射 |
|--------|---------------------|
| `#e8e9eb` 壳体 | `--hp-shell-bg`，浅 `#f2f4f8` / 深 `#141a24` |
| `#66f66f` LED | `--hp-led-on`（=`--signal`），processing 时 `--amber` |
| `#b4b2b2` 头梁线 | `--hp-line` |
| 多层 inset 阴影 | 简化为 **2 层 inset + 1 层外阴影**，避免与 `glass-card` 打架 |
| `.text` 淡灰 | `font-family: var(--font-mono)`，`letter-spacing: 0.14em`，`ANC` / `REF` |

---

## 组件规格 — `HeadphoneRackUnit.tsx`

```tsx
// components/HeadphoneRackUnit.tsx
export type HeadphoneLed = "idle" | "active" | "processing" | "error";

type Props = {
  /** 机架通道名，默认 MONITOR */
  channel?: string;
  /** LED 状态，与 rack-led 语义一致 */
  led?: HeadphoneLed;
  /** 耳罩内标签：ANC | REF | ABX */
  label?: string;
  /** 可选副标题 mono 一行 */
  hint?: string;
  /** 播放中微动画（腔体亮度脉动） */
  pulse?: boolean;
  /** 紧凑模式（Cinema 侧边） */
  compact?: boolean;
  className?: string;
};
```

**DOM 结构（accessibility）：**

```tsx
<div className="hp-rack-unit" role="img" aria-label={ariaLabel}>
  <div className="hp-shell">
    <div className="hp-band-line" aria-hidden="true" />
    <div className="hp-cavity" aria-hidden="true" />
    <span className={`hp-led hp-led-${led}`} aria-hidden="true" />
    <span className="hp-label">{label}</span>
  </div>
  {hint ? <p className="hp-hint">{hint}</p> : null}
</div>
```

**状态机（必须由父组件传入，禁止写死常亮）：**

| 场景 | `led` | `pulse` | `label` |
|------|-------|---------|---------|
| 空闲 / 无 task | `idle` | false | `REF` |
| 音频播放中 | `active` | true | `ANC` |
| 任务 processing | `processing` | true | `ANC` |
| 播放失败 / 无文件 | `error` | false | `—` |
| ABX 试听轮次 | `active` | true | `ABX` |

---

## 推荐植入位置（按优先级，择 2–3 处即可，勿全站堆砌）

### P0 — Home 机架区（与 MOD-01 并列，最不违和）

**位置：** `HomePage.tsx` → `console-rack` 内，**MOD-01 统计卡下方**或右侧叠放第二模块 `MOD-HS01 / MONITOR`。

```
┌─ console-hero ─────────┐  ┌─ console-rack ──────────────┐
│ Denoise Studio         │  │ MOD-01 / INPUT  (现有)      │
│ CTA…                   │  │ VU + readouts               │
└────────────────────────┘  │ MOD-HS01 / MONITOR (新增)   │
                            │  [HeadphoneRackUnit]        │
                            │  「参考监听 · 降噪对比」      │
                            └─────────────────────────────┘
```

- 外壳复用 `.console-module`，**`rotate(-0.6deg)`** 与现卡一致，不要更大倾斜
- 有 `taskId` 且 status=completed → `led=active`；processing → `processing`
- 点击耳机模块区域 → 链到 `/showcase/cinema` 或 `/overview`（扩大 hit area，非仅耳罩）

**文件：** `HomePage.tsx`、`home.css`、`headphone-rack.css`

---

### P0 — Compare Cinema 右侧（语义最强）

**位置：** `CompareCinemaPage.tsx` 右侧 VU 列与波形之间，作为 **「监听参考硬件」** 图示。

- `compact` 模式：宽度 `min(200px, 28vw)`，高度按比例
- `led` / `pulse` 与 `playing` 同步（已有 `timeupdate` VU 逻辑）
- 不替代调音台推子，仅作视觉锚点

**文件：** `CompareCinemaPage.tsx`、`showcase.css`（或 `headphone-rack.css`）

---

### P1 — ABX 盲听 Panel（功能耦合）

**位置：** `ABXTestPanel.tsx` 标题旁或结果区上方。

- 每轮 ABX 开始：`led=processing` 300ms → `active`
- 猜对/猜错不改变耳机形态，仅 LED 短暂 amber flash
- 标签固定 `ABX`

---

### P2 — Showcase Hub bento 第五格（可选，低优先）

- **不要**单独开第六张 bento；若加则替换「纯装饰」之一或作为 MOD-S04 Cinema 卡内嵌小耳机图标（32px 级），非 270px 大卡

---

### 禁止植入位置

- `GlassNav` logo 区（与 VU 品牌冲突）
- 全站 `AmbientBackground` 层（遮挡示波器、破坏视差）
- Upload / Progress 表单区（与输入无关）
- 弹窗 Modal 居中（无业务需求）

---

## 样式细则（`headphone-rack.css`）

1. **壳体 `.hp-shell`**
   - `aspect-ratio: var(--hp-aspect)`；`max-width: 270px`；`width: 100%`
   - `border: 1px solid var(--hp-shell-border)`；`border-radius: clamp(48px, 18vw, 70px)`
   - 阴影：`box-shadow: var(--hp-shell-shadow)` + 一层轻 inset（用 token，勿 7 层硬编码）

2. **头梁线 `.hp-band-line`**
   - `top: 30%`；高度 2px；左右各 5% 白色高光改为 `var(--glass-inner-highlight)` 伪元素

3. **腔体 `.hp-cavity`**
   - 宽 55%；高 `clamp(12px, 4vw, 20px)`；渐变用 `--hp-cavity-bg`
   - `pulse` 时：`animation: hpCavityPulse 1.2s ease-in-out infinite`（`prefers-reduced-motion` 关闭）

4. **LED `.hp-led`**
   - 复用视觉语言：`.hp-led-active` = `rack-led-active` 同款 glow
   - **删除** 原 `#66f66f` / `#3eff4b`

5. **机架外壳包裹 `.hp-rack-wrap`**
   - 放在 `RackPanel` 或 `.console-module` 内时，外壳 **不再** 叠加过大外阴影，避免双重阴影

6. **浅色主题**
   - 壳体略深于页面底 `--bg-elevated`，腔体保持可读凹槽感
7. **深色主题**
   - 壳体 `--bg-elevated`，头梁线提高对比，避免「灰块糊在背景上」

---

## 微交互（克制）

| 交互 | 实现 |
|------|------|
| 播放中 | 腔体 pulse + LED `active` |
| 鼠标靠近（Home/Cinema） | 整体 `transform: translateY(-2px)`，**不**跟指针大幅视差 |
| processing | 复用 `studio-atmosphere-processing` 时 LED 切 amber blink（与 `rack-led-processing` 一致） |
| hover | 边框 `--panel-border-strong`，无弹跳 |

---

## 建议实施顺序

1. `tokens.css` 耳机变量 + `headphone-rack.css` + `HeadphoneRackUnit.tsx`（静态四态）
2. **Home `MOD-HS01`** 接入 + `taskId` 状态
3. **Compare Cinema** `compact` 接入 + `playing` 联动
4.（可选）ABX Panel 接入
5. i18n + `npm run build && npm test`

---

## 验收标准

- [ ] 耳机模块出现在 **Rack 壳**（`console-module` / `RackPanel`）内，非孤立 floating card
- [ ] 无硬编码 `#66f66f`、`#e8e9eb`；深浅主题均可读
- [ ] LED 随播放/processing/idle 变化，非常亮装饰
- [ ] Home 布局不挤压 hero；移动端耳机 `max-width: 100%` 不横向溢出
- [ ] Cinema / Overview 原有试听功能无回归
- [ ] `prefers-reduced-motion` 下无 pulse / blink
- [ ] `npm run build` + `npm test` 通过

---

## i18n 键清单（示例）

| 键 | zh | en |
|----|----|----|
| `hpModuleId` | 参考监听 | Reference monitor |
| `hpModuleChannel` | MONITOR | MONITOR |
| `hpHomeHint` | 降噪前后 A/B 试听参考 | A/B reference for denoise compare |
| `hpLabelRef` | REF | REF |
| `hpLabelAnc` | ANC | ANC |
| `hpLabelAbx` | ABX | ABX |
| `hpAriaIdle` | 监听单元待机 | Monitor unit idle |
| `hpAriaPlaying` | 监听单元工作中 | Monitor unit active |

---

## 一句话版（快速粘贴）

> 将用户新拟物降噪耳机 CSS 改写为 Signal Console 机架模块 `MOD-HS01/HeadphoneRackUnit`：token 化颜色与阴影，LED 绑定播放/processing，植入 Home 机架与 Compare Cinema（可选 ABX）；包在 RackPanel/console-module 内，禁止原样绿 LED 与全屏装饰；纯 CSS+TS，build+test 通过。

---

## 相关文档

- 机架语言：`docs/prompts/signal-console-ui-polish.md`
- Showcase：`docs/prompts/signal-console-showcase-pages.md`
- 背景层：`docs/prompts/background-mouse-interaction.md`（耳机 **不得** 放入背景层）
- 建议版本标签：`web-signal-console-headphone-rack`
