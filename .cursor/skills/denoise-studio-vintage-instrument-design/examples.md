# 复古仪器 — Live Capture 示例

## 目标观感

- 外面：暖米白塑胶前面板，略倒角，顶高光
- 中间：深绿黑 CRT 开窗，内凹
- 里面：磷光绿网格 + 波形 + 慢扫描线
- 字：丝印灰绿 `CH1 / TIME`、`STBY` / `LIVE`

## 最小 HTML 结构（示意）

```tsx
<section className="live-module live-module-input vintage-instrument" data-recording={...}>
  <header className="live-module-head">...</header>
  <div className="live-scope-meta vintage-silk">...</div>
  <div className="vintage-crt-bezel">
    <LiveWaveformScope className="vintage-crt" ... />
  </div>
  <div className="live-vu-row vintage-vu">...</div>
</section>
```

## CSS 片段（bezels）

```css
.vintage-instrument.live-module {
  background: linear-gradient(180deg, var(--vint-chassis-highlight), var(--vint-chassis-mid));
  border: 1px solid var(--vint-chassis-shadow);
  box-shadow: var(--vint-raised);
}

.vintage-crt-bezel {
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--vint-bezel);
  box-shadow: inset 0 1px 0 var(--vint-chassis-highlight), inset 0 -2px 4px rgba(0,0,0,0.15);
}

.vintage-crt-bezel .live-scope-frame {
  border: 2px solid var(--vint-bezel-inner);
  box-shadow: var(--vint-inset-crt);
  background: var(--vint-crt-bg);
}
```

## Canvas 磷光波形（要点）

```ts
ctx.strokeStyle = phosphor;
ctx.shadowColor = glow;
ctx.shadowBlur = recording ? 12 : 6;
ctx.lineWidth = recording ? 2 : 1.5;
// grid 用 phosphorGrid alpha 0.15
```

## 与 Signal Console 并存

- 外层 `RackPanel` **不要** `vintage-instrument`
- 仅 `live-module-input` 使用复古皮
- `rack-led` 颜色仍用 `--signal` / `--amber`

## 委托示例

> 按 vintage-instrument skill，给 LiveCapturePage 的 MOD-07A 套米白机身与磷光 CRT，改 LiveWaveformScope 绘制与 vintage-instrument.css，保留 flow/tier。
