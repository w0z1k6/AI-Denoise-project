# 复古电子仪器前端设计 — 完整参考

> 米白机身 · 磷光绿 CRT · 丝印刻度 · pilot 灯。与 Signal Console 机架语言叠加，不替代。

---

## 一、设计灵感与边界

### 1.1 参考对象（抽象特征，非临摹商标）

- **台式示波器**：米色/灰米色前面板、中央矩形 CRT、下方旋钮列、右上角 pilot 灯
- **台式万用表 / 信号发生器**：丝印字、浅灰塑胶、深色 LCD 绿字（磷光屏更偏「自发光绿」）
- **实验室电源**：倒角机身、内凹屏幕、金属质感滚花（仅用 CSS 暗示，不做复杂 3D）

### 1.2 不是什么

- 不是蒸汽朋克铜管齿轮
- 不是赛博朋克粉紫霓虹 HUD
- 不是 Apple 纯白极简卡片
- 不是 Skeuomorphism 7 层阴影手机拟物

### 1.3 在 Denoise Studio 中的位置

```
┌─ RackPanel (Signal Console 玻璃机架) ─────────────┐
│  MOD-07 / LIVE  flow  tier                        │
│  ┌─ .vintage-instrument 米白机身 ─────────────┐   │
│  │  silk: CH1 / TIME          pilot STBY/LIVE │   │
│  │  ┌─ bezel ─────────────────────────────┐   │   │
│  │  │  CRT: 磷光网格 + 波形 + 扫描线      │   │   │
│  │  └────────────────────────────────────┘   │   │
│  │  VU 槽 + 丝印 IN/ANC                       │   │
│  └────────────────────────────────────────────┘   │
│  RecordTransport 复古甲板                          │
└───────────────────────────────────────────────────┘
```

---

## 二、色彩系统

### 2.1 机身（Chassis）

暖灰米白，略带黄绿灰（实验室老化塑胶感）：

- 主面 `--vint-chassis`：大面积前面板
- 中间 `--vint-chassis-mid`：模块分区
- 阴影边 `--vint-chassis-shadow`：底边与 bezels
- 高光 `--vint-chassis-highlight`：顶边 1px 模拟注塑高光

**渐变示例（CSS）：**

```css
background: linear-gradient(180deg, var(--vint-chassis-highlight) 0%, var(--vint-chassis) 35%, var(--vint-chassis-mid) 100%);
```

### 2.2 CRT 腔体

屏内 **近黑偏绿**，勿纯 `#000`：

- `--vint-crt-bg: #0a120c`
- 四角 vignette：`radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.5) 100%)` 叠在 canvas 上或 canvas 内绘制

### 2.3 磷光（Phosphor P31 语感）

| 用途 | 色 |
|------|-----|
| 波形主线 | `--vint-phosphor` |
| 网格/刻度 | `--vint-phosphor-grid`（低 alpha） |
| 辉光 bloom | shadowBlur 8–14 + `--vint-phosphor-glow` |
| 过曝感（强信号） | 临时提高 lineWidth，勿纯白 |

磷光绿 **偏黄绿** `#3dff7a`，避免 `#00ff00` 纯绿廉价屏保感。

### 2.4 丝印（Silkscreen）

刻度与标签：`--vint-silk`，小号 caps，`letter-spacing: 0.14em`，可选：

```css
text-shadow: 0 1px 0 var(--vint-chassis-highlight), 0 -1px 0 rgba(0,0,0,0.12);
```

模拟凹刻丝印。

### 2.5 Pilot 灯

- REC：`--vint-pilot-red` 圆点 + 外晕，非扁平 danger token  alone
- STBY/LIVE：磷光绿小字或双色 LED（绿=live，灭=stby）

---

## 三、造型与层次

### 3.1 圆角与倒角

- 机身外圆角：`8px–12px`（仪器），非 `24px` SaaS 卡
- CRT 开窗：内圆角 `4px–6px`，双层 border（bezel 外浅、内深）

### 3.2 阴影公式（克制）

```css
/* 机身抬起 */
box-shadow: var(--vint-raised);
/* CRT 内凹 */
box-shadow: var(--vint-inset-crt);
```

最多 **外 1 层 + inset 1 层**，禁止 5 层新拟物。

### 3.3 角标 bracket

保留 Signal Console 四角 bracket，颜色改为 **磷光 dim** 而非 signal 墨绿，更像 CRT 取景。

---

## 四、Canvas 示波器绘制规范

适用于 `LiveWaveformScope.tsx` 在 `.vintage-instrument` 祖先下：

### 4.1 每帧顺序

1. 填充 `--vint-crt-bg`
2. 绘制磷光网格（竖 10 div / 横 8 div，线 alpha 0.12–0.18）
3. 中心线略亮
4. （可选）静态 scanline 纹理：水平线 alpha 0.04 整屏
5. 时域波形：stroke `--vint-phosphor`，recording 时 lineWidth 2，`shadowBlur` 10
6. 垂直扫描线：recording 时 x 方向移动，alpha 0.12
7. idle 丝印提示字：磷光 dim，11px mono

### 4.2 读取 token

```ts
const phosphor = getComputedStyle(el).getPropertyValue("--vint-phosphor").trim();
const grid = getComputedStyle(el).getPropertyValue("--vint-phosphor-grid").trim();
```

父级必须有 `.vintage-instrument` 或 `data-vintage="on"`。

### 4.3 性能

- 网格可绘到 offscreen canvas 缓存，resize 时重建
- `prefers-reduced-motion`：无扫描线、无 shadowBlur、波形仍可用

---

## 五、VU / 电平表复古化

- 轨道：深色槽 `#0d140f` inset
- 填充：磷光绿渐变 `phosphor → phosphor-mid`
- 峰值 hold：短横线磷光 dim
- 标签 `IN`/`ANC`：丝印色，非 tertiary 灰

---

## 六、Transport / 旋钮区

- 条形容器：与机身同色 `--vint-chassis`
- REC：圆形 pilot + 凹座 `inset` + 红色发光
- LCD 区：嵌入 CRT 风格小窗，字色磷光，底 `--vint-crt-bg`
- 机械键：STOP 方形灰键，微 inset，字丝印色

---

## 七、主题策略

| 模式 | 机身 | 磷光 |
|------|------|------|
| 浅色（答辩默认） | 米白 `#e8e4da` | 中亮绿，grid 可见 |
| 深色 | 深褐灰机身 | 更亮磷光，grid 加强 |

用 `[data-theme="light"] .vintage-instrument` 与 dark 覆盖 token（见 `tokens-snippet.css`）。

可选：`data-vintage="on"` 挂在 `documentElement` 或仅 Live 页根，避免全站变米黄。

---

## 八、文件组织

| 文件 | 职责 |
|------|------|
| `styles/vintage-instrument.css` | 机身、bezel、VU、transport 复古皮 |
| `styles/live-capture.css` | 布局；引入 vintage 修饰符 |
| `components/live/LiveWaveformScope.tsx` | CRT 绘制逻辑 |
| `tokens-snippet.css` | skill 内 token 源，合并进项目 |

`styles.css` 增加：

```css
@import "./styles/vintage-instrument.css";
```

---

## 九、与姊妹 Skill 协作

1. 先满足 **Signal Console**：MOD、LED、flow、tier、空态
2. 再在 `.live-module-input` 加 `vintage-instrument`
3. 磷光色 **替代** 原 `--signal` 仅于 CRT 区域内；机架顶 LED 仍用 `--signal` / `--amber`

---

## 十、反模式

1. 全页米黄导致失去机架层次
2. 磷光过亮致投影过曝
3. 纯 `#00ff00` 波形
4. 机身纯灰无暖色
5. CRT 无 vignette 像扁平 div
6. 扫描线过快频闪
7. 复古耳机拟物回归（用户已删 MOD-07B）
8. Tailwind / 图片贴皮 CRT 边框

---

## 十一、验收清单

- [ ] 米白机身暖灰可见，非冷白卡
- [ ] CRT 内腔偏绿深色，有四角暗角
- [ ] 网格与波形同为磷光色系
- [ ] 波形有适度 bloom，recording 有扫描线
- [ ] 丝印 CH1/TIME/STBY 像面板字
- [ ] REC pilot 红灯有凹座与晕
- [ ] reduced-motion 降级
- [ ] token 无散落 hex（除 snippet 定义处）
- [ ] RackPanel 外框仍为 Console 语言

---

## 十二、推荐实施顺序（Live 页）

1. 复制 `tokens-snippet.css` → `vintage-instrument.css`
2. `LiveCapturePage` 的 `live-module-input` 加 `vintage-instrument`
3. 改 `live-capture.css` 机身/bezel
4. 改 `LiveWaveformScope` 读磷光 token
5. 复古化 `record-transport` 与 VU
6. 截图对比浅色答辩投屏

---

*version: vintage-instrument-skill v1 · pairs with signal-console-design v1*
