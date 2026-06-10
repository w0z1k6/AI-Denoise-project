---
name: denoise-studio-vintage-instrument-design
description: >-
  Guides vintage electronic instrument UI for Denoise Studio (beige chassis,
  green phosphor CRT scopes, silkscreen labels, pilot LEDs). Use when the user
  wants retro oscilloscope aesthetics, 复古示波器, 米白机身, 绿色荧光屏, vintage
  hardware, CRT, or instrument-grade frontend polish on webapp components.
---

# Denoise Studio — 复古电子仪器前端设计 Skill

本 Skill 专注 **米白机身 + 绿色磷光屏** 的复古实验室仪器美学（Tek/Nagra/HP 老示波器语感），作为 `denoise-studio-signal-console-design` 的 **材质层**：机架语义（MOD/LED/flow）仍走 Signal Console；示波器、bezels、VU、transport 旋钮区走本 Skill。

## 何时启用

- 用户提到 **复古、示波器、米白、荧光绿、CRT、电子管、老设备、实验室仪器**
- 优化 `/record` 示波器区、Overview 波形、Charts 局部「仪器窗」
- 截图反馈「像现代网页不像老机器」
- 与 Signal Console skill **叠加使用**（先机架结构，再复古材质）

## 视觉一句话

> **米白注塑机身** 托住一块 **偏绿的深色 CRT**，上面是 **磷光绿波形** 与 **丝印灰字**；不是赛博霓虹，不是 Apple 白卡。

## 核心 token（必须先定义）

在 `styles/vintage-instrument.css` 或 `tokens.css` 增加 `data-vintage="on"` 或 `.vintage-instrument` 作用域：

| Token | 含义 | 参考 |
|-------|------|------|
| `--vint-chassis` | 机身米白 | `#e8e4da` / `#ddd8cb` |
| `--vint-chassis-dark` | 边框/阴影边 | `#b8b0a0` |
| `--vint-bezel` | 屏幕外框 | `#c9c2b4` |
| `--vint-crt-bg` | 屏内底（近黑偏绿） | `#0a120c` |
| `--vint-phosphor` | 主磷光绿 | `#3dff7a` |
| `--vint-phosphor-dim` | 网格/刻度 | `rgba(61,255,122,0.22)` |
| `--vint-phosphor-glow` | 辉光 | `rgba(61,255,122,0.55)` |
| `--vint-silk` | 丝印字 | `#6a6558` |
| `--vint-pilot-red` | REC  pilot | `#e23b2f` |

**禁止** 硬编码到组件；深浅主题下磷光亮度可调，机身 hue 保持暖灰。

## 实施工作流

```
复古仪器迭代清单：
- [ ] 1. 读 reference.md §磷光CRT + §机身注塑
- [ ] 2. 父级加 class `vintage-instrument`（或 data-vintage）
- [ ] 3. 新建/扩展 vintage-instrument.css，import 于 styles.css
- [ ] 4. LiveWaveformScope：磷光 stroke + CRT vignette + 扫描线
- [ ] 5. 机身：双层 border + inset + 圆角 6–10px（非大圆角卡片）
- [ ] 6. 标签：丝印 uppercase mono， engraved 阴影
- [ ] 7. prefers-reduced-motion：关扫描线/辉光脉动
- [ ] 8. 与 Signal Console 并存：保留 MOD-07A、flow、tier
```

## 组件映射（Denoise Studio）

| 区域 | 复古化处理 |
|------|------------|
| `LiveWaveformScope` | CRT 内腔 + 磷光网格 + bloom + 扫描线 |
| `.live-module-input` | 米白机身、屏幕开窗 inset |
| `live-scope-meta` | 丝印 `CH1` / `TIME` / `STBY` |
| `VuMeterBar` | 磷光填充条 + 深色槽 |
| `RecordTransport` | 机身条 + 红色 pilot REC + LCD 绿字 |
| `RackPanel` 外卡 | **保持** Signal Console 玻璃机架，仅内嵌仪器为复古 |

## 与 Signal Console 的分工

| Signal Console | Vintage Instrument |
|----------------|------------------|
| MOD-xx、LED 状态机、flow | 机身材料、CRT、磷光色 |
| 业务 i18n、L1/L2/L3 | 丝印风格、刻度字体 |
| 禁止紫色霓虹 | 禁止荧光粉/青赛博 |

**不要** 把整个 RackPanel 变成米色大塑料盒——复古窗在 **仪器面**，机架外框仍可 glass。

## 附加资源

- **完整教义**：[reference.md](reference.md)
- **中文扩展**：[doctrine-zh.md](doctrine-zh.md)
- **Live 示波器示例**：[examples.md](examples.md)
- **可复制 token 片段**：[tokens-snippet.css](tokens-snippet.css)
- 姊妹 skill：`.cursor/skills/denoise-studio-signal-console-design/`

## 一句话委托模板

> 按 `denoise-studio-vintage-instrument-design` skill：为 [组件/页面] 套用米白机身 + 磷光绿 CRT 复古仪器皮，token 化，保留 Signal Console 机架语义，纯 CSS + Canvas，reduced-motion 降级。
