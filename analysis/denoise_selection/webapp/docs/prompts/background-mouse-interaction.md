# AI 提示词：Denoise Studio 背景动效 + 鼠标交互

> 复制整段给 Cursor / Claude，在 **现有 Signal Console 主题** 上迭代背景层。  
> 当前已实现基础版：`useStudioPointer`、`ScopeCanvas`、`AmbientBackground`。

---

## 角色与目标

你是资深创意前端工程师，负责为 **Denoise Studio**（智能音频降噪 Web 平台）增强**全屏背景动效**，要求：

1. 与现有 **Signal Console** 美学一致（广播机架、示波器、磷光青 `#14f5c8`、琥珀 `#ffb020`、深色底）
2. 背景**随鼠标移动产生视差、光晕、波形调制**，但不干扰内容阅读与操作
3. **性能优先**：60fps 目标，移动端降级，尊重 `prefers-reduced-motion`
4. **只改 frontend**，路径：`analysis/denoise_selection/webapp/frontend/`

---

## 现有技术栈（必须遵守）

- React 18 + TypeScript + Vite
- 纯 CSS（`src/styles/studio-console.css` 等），**禁止** Tailwind / MUI
- 已有组件：`AmbientBackground.tsx`、`ScopeCanvas.tsx`、`hooks/useStudioPointer.ts`
- 字体：Antonio / Newsreader / Fragment Mono（勿换成 Inter、Space Grotesk）
- 背景层 `pointer-events: none`，不可阻挡点击

---

## 美学约束（避免 AI 俗套）

- **禁止**：紫色渐变、blob 漂浮、毛玻璃泛滥、Inter 字体
- **推荐**：示波器扫描线、VU 表脉冲、频谱柱状微动、网格透视、信号粒子、CRT 轻微畸变
- 动效应像**电台调音台待机画面**，而非屏保

---

## 交互规格（核心需求）

### 1. 鼠标位置追踪

- 归一化坐标 `pointer.x / pointer.y` ∈ [0,1]，使用 **lerp 平滑**（系数 0.06–0.12），避免抖动
- 鼠标离开窗口时缓回中心 `(0.5, 0.4)`
- 通过 CSS 变量下发：`--pointer-x`、`--pointer-y`、`--pointer-dx`、`--pointer-dy`、`--grid-shift-x/y`

### 2. 分层视差（由远到近）

| 层级 | 元素 | 鼠标响应 |
|------|------|----------|
| L0 | 纯色底 + 噪点 | 无 |
| L1 | 粗网格 48px | 平移 ±12–24px，光晕 mask 跟随指针 |
| L2 | 细网格 12px | 平移量 ×1.5 |
| L3 | 光标磷光晕 | `radial-gradient` 中心 = 指针位置，opacity 0.3–0.5 |
| L4 | 信号粒子 12–20 个 | `translate` 与 `--pointer-dx/dy` 成比例，depth 0.4–1.0 |
| L5 | Canvas 示波器双波形 | 振幅 ∝ `pointer.y`，相位 ∝ `pointer.x`，频率微调 |

### 3. Canvas 示波器（`ScopeCanvas.tsx`）

- 底部 20–30vh，左右 fade mask
- 双线：signal 色 + amber 色，叠加正弦 + 谐波
- `requestAnimationFrame` 驱动，DPR capped at 2
- 鼠标激活时透明度提高 15–20%
- 可选进阶：缓慢「假 FFT」柱状图在波形后方，高度随 `pointer.x` 偏移

### 4. 可选进阶交互（若工期允许）

- **点击涟漪**：pointer down 时从点击处扩散一圈 signal 色 ring，1.2s 消失
- **滚动视差**：`window.scrollY` 让网格 `translateY` 轻微偏移
- **任务状态联动**：当 `task.status === 'processing'` 时，VU 粒子脉冲加速、波形振幅 +20%
- **触摸设备**：用 `touchmove` 等效 `mousemove`，无触摸时保持自动缓慢漂移（idle drift）

---

## 性能与无障碍

```ts
// 必须实现
- matchMedia('(prefers-reduced-motion: reduce)') → 静态背景，无 rAF 循环
- 移动端 (max-width: 768px) → 减少粒子数、降低 canvas 高度、可选暂停 canvas
- 页面 hidden (document.visibilityState) → 暂停 rAF
- 单帧耗时 > 16ms 时自动降低粒子/网格细层
```

---

## 建议文件结构

```
src/
  hooks/
    useStudioPointer.ts      # 已有，可扩展 touch + idle drift
    useBackgroundMotion.ts   # 可选：统一 motion 偏好与 visibility
  components/
    AmbientBackground.tsx    # 组合各层
    ScopeCanvas.tsx          # 示波器 canvas
    SpectrumBars.tsx         # 可选 FFT 装饰
  styles/
    studio-console.css       # 背景层样式，勿污染 .glass-card 业务区
```

---

## 实现步骤（供 AI 按序执行）

1. 阅读 `AmbientBackground.tsx`、`studio-console.css`、`tokens.css`
2. 扩展 `useStudioPointer`：touch、leave、reduced-motion
3. 增强 CSS 层：cursor glow、双网格视差、粒子
4. 增强 `ScopeCanvas`：鼠标调制 + theme 色读取
5. 验证：`npm run build`、`npm test` 不破坏
6. 肉眼检查：移动鼠标时网格、光晕、波形、粒子均有**可感知但克制**的响应

---

## 验收标准

- [x] 鼠标移动时，至少 3 个视觉层有明显联动（网格 / 光晕 / 粒子 / 示波器）
- [x] 前景文字与卡片对比度仍 WCAG 友好（背景 opacity ≤ 0.55）
- [x] 指针更新走 rAF + 直接写 CSS 变量，避免每帧 React re-render
- [x] `prefers-reduced-motion: reduce` 下无动画
- [x] 浅色主题 `data-theme="light"` 下光晕/波形仍可见（读取 `--signal` / `--amber`）
- [x] 点击涟漪、滚动视差、触摸追踪、idle 漂移、任务 processing 加速
- [x] 移动端降级（少粒子、无细网格、无 canvas）
- [x] `document.visibilityState` 隐藏时暂停 canvas 绘制

---

## 参考代码锚点（当前实现）

```tsx
// AmbientBackground 设置 CSS 变量
style={{
  "--pointer-x": `${pointer.x * 100}%`,
  "--pointer-y": `${pointer.y * 100}%`,
  "--pointer-dx": String((pointer.x - 0.5) * 100),
  "--grid-shift-x": `${(pointer.x - 0.5) * 24}px`,
}}
```

```css
.studio-cursor-glow {
  background: radial-gradient(520px circle at var(--pointer-x) var(--pointer-y), ...);
}
.studio-grid {
  transform: translate(var(--grid-shift-x), var(--grid-shift-y));
}
```

---

## 一句话版（快速粘贴）

> 在 Denoise Studio 的 Signal Console 深色主题上，为 `AmbientBackground` 增加多层鼠标交互背景：平滑指针追踪、网格视差、磷光光晕、信号粒子、Canvas 双波形示波器（振幅/相位随鼠标变化）；保持 pointer-events:none、纯 CSS+Canvas、禁止 Tailwind/紫色渐变；尊重 prefers-reduced-motion；只改 `webapp/frontend`。
