---
name: denoise-studio-signal-console-design
description: >-
  Guides aesthetic design and UI polish for Denoise Studio Signal Console webapp
  (React/Vite, pure CSS, rack/broadcast HMI language). Use when optimizing
  webapp visuals, Live Capture page, RackPanel modules, tokens, motion, i18n,
  or when the user asks for Signal Console design, 美学, UI polish, or 机架风格.
---

# Denoise Studio — Signal Console 美学设计 Skill

本 Skill 指导 Agent 在 **不引入 Tailwind/MUI/紫色渐变** 的前提下，将 Denoise Studio webapp 打磨为「**广播级调音台 / 机架信号控制台**」视觉，而非通用 SaaS 仪表盘。

## 何时启用

- 用户要求优化 webapp **美学、UI、视觉、动效、机架感**
- 新增或改版页面（尤其 `/record` Live Capture、Upload、Overview、Showcase）
- 评审截图反馈「空、平、像表单」时
- 撰写/执行 `docs/prompts/signal-console-*.md` 系列提示词

## 核心原则（30 秒版）

| 要做 | 禁止 |
|------|------|
| 机架模块 `MOD-xx / CHANNEL`、LED 语义、mono 数据层 | 紫色渐变、霓虹赛博、Inter/Roboto |
| `tokens.css` 变量，深浅主题双适配 | 硬编码 `#66f66f`、`#e8e9eb` |
| 真数据驱动 VU/LED（idle/active/processing） | 常亮装饰绿、假随机数字 |
| Canvas 示波器网格 + 扫描线 + 角落 bracket | Three.js 全屏粒子 |
| `prefers-reduced-motion` 降级 | 无视无障碍 infinite 动画 |

## 实施工作流

复制此清单并逐步执行：

```
美学迭代清单：
- [ ] 1. 读 reference.md 对应页面 archetype
- [ ] 2. 只改 frontend/；路径见 reference §文件组织
- [ ] 3. 先扩 tokens（若有新语义色），再写页面 CSS
- [ ] 4. 复用 RackPanel / VuMeterBar / motion.css stagger
- [ ] 5. 空状态必须有文案+视觉（网格/括号/提示），禁止大块灰矩形
- [ ] 6. i18n 中英文键同步写入 src/i18n/index.ts
- [ ] 7. npm run build && npm test（仅修复本次引入的 TS 错误）
```

## Live Capture（/record）快速规范

**叙事：** 现场采集台 MOD-07，三层降噪 L1 监听 / L2 预览 / L3 正式管线，UI 必须明示差异。

**布局骨架：**
1. `RackPanel` MOD-07 / LIVE + flow strip 01–04
2. `live-tier-strip` 三枚 pill（L1/L2/L3）
3. 双模块 grid：`MOD-07A INPUT`（示波器框 + 竖 VU）+ `MOD-07B MONITOR`（`LiveMonitorUnit` + ANC toggle）
4. `RecordTransport` 广播甲板（REC 圆钮 + LCD 读数区）
5. preview 相位：`AudioComparePlayer` + `MethodSelector` + Commit

**示波器：** `LiveWaveformScope` 必须有磷光网格、中心线、四角 bracket、idle 提示字、录音扫描线。

**文件：**
- `styles/live-capture.css`
- `components/live/LiveWaveformScope.tsx`
- `components/live/LiveMonitorUnit.tsx`
- `components/live/RecordTransport.tsx`
- `pages/LiveCapturePage.tsx`

## 描述「炫酷」的边界

在本项目中「炫酷」= **有语义的专业感**，不是游戏 UI：

- 机架通电：stagger 入场、LED blink、LCD 风格读数
- 播放/录音：VU 跳、示波器 glow、耳机腔体 pulse
- 路由切换：`motion.css` fadeInUp，showcase 子路由可禁用

## 附加资源

- **完整设计教义**：[reference.md](reference.md)
- **中文万字扩展卷**：[doctrine-zh.md](doctrine-zh.md)（与 reference 合读达约一万字）
- **Live Capture 前后对比**：[examples.md](examples.md)
- 项目内 AI 提示词：`analysis/denoise_selection/webapp/docs/prompts/signal-console-*.md`
- 复古仪器材质层（米白机身/磷光 CRT）：`.cursor/skills/denoise-studio-vintage-instrument-design/`

## 一句话委托模板

> 按 `denoise-studio-signal-console-design` skill：在既有 tokens/RackPanel 语言下优化 [页面名]，消除空白灰块，补全机架层次与状态联动，纯 CSS，i18n 双语，build/test 通过。

## 文档体量说明

本 skill 含 `reference.md` + `doctrine-zh.md` 等文档，**中文正文合计约一万字**，供深度改版与答辩美学对齐使用；日常迭代以本文清单为准即可。

启用后默认改动范围：`analysis/denoise_selection/webapp/frontend/`；Live 专项同步 `live-capture.css` 与 `components/live/*`。禁止在未获用户明确要求时引入新 UI 框架或修改后端 API。每次交付附「截图对比点」：示波器是否仍有空灰、LED 是否绑状态、tier 文案是否在。如此，设计 skill 才不仅是文档，而是可执行的审美契约。完整中文约一万字，见 reference 与 doctrine-zh。引用本 skill 时优先 @ 本目录或说明「Signal Console 美学 skill」。维护范围：analysis/denoise_selection/webapp/frontend 全站视觉，不含后端与论文 LaTeX 排版。
