# Live Capture 美学 — 前后对比示例

## 问题截图典型症状

- 示波器区：纯灰矩形，无网格、无角标、无 idle 提示 → 像加载失败
- Monitor 区：仅一行 checkbox + 小字 → 空洞，无「监听通路」语义
- 流程条：active 态不明显，与标题区脱节
- Transport：REC 钮孤立，右侧读数像普通文本而非 LCD
- 无 L1/L2/L3 层级 → 用户分不清预览 vs 正式管线

## 改版后应对

| 区域 | 改版要素 |
|------|----------|
| 示波器 | `live-scope-frame` 四角 bracket + 网格 + idle hint + 录音 scan line |
| Monitor | `LiveMonitorUnit` 耳罩拟物 + latency badge + 右侧 control 列 |
| 层级 | `live-tier-strip` L1/L2/L3 pill |
| VU | 竖向 `VuMeterBar` IN / ANC |
| Transport | LCD 底板 `record-transport-readouts` + status 药丸 |
| 模块 | `live-module::before` 顶 accent 条，渐变底 |

## 代码锚点

```
frontend/src/styles/live-capture.css
frontend/src/components/live/LiveWaveformScope.tsx
frontend/src/components/live/LiveMonitorUnit.tsx
frontend/src/pages/LiveCapturePage.tsx
```

## 最小 diff 策略（仅救火示波器空灰盒）

若时间紧，至少做：

1. `LiveWaveformScope` 内 `drawGrid()` + 四角 bracket
2. idle 时 `recordScopeIdle` 文案居中
3. `live-scope-frame` CSS 内阴影

其余 Monitor/Transport 可第二期迭代。

## 与 skill 文档关系

本 examples 为轻量对照；完整万字中文教义见 `reference.md`（机架/token/逐页注解/FAQ）与 `doctrine-zh.md`（仪器伦理/CSS 词典/答辩脚本）。Agent 接到「优化 Live 页美学」时：先 examples 定位差距，再 reference 附录 A.9 深读，最后 doctrine 第二十一~三十章查实现模式。改完回到 examples 表核对是否闭环。本文件汉字较少，万字主体在 reference 与 doctrine-zh。
