# AI 提示词：Denoise Studio Signal Console — 全站 UI 精修（基于当前截图）

> 复制整段给 Cursor / Claude。在 **已上线的 Signal Console + 互动背景** 基础上迭代，不要推倒重来。  
> 参考截图：Home / Upload / Overview / Charts / History（浅色主题为主）。

---

## 角色与目标

你是资深创意前端工程师，负责 **Denoise Studio** Web 端的**视觉一致性、信息层级、专业音频工具感**提升。

**当前优点（必须保留）：**
- Signal Console 气质：机架 UI、Antonio 大标题、磷光青 `#14f5c8` / 琥珀 `#ffb020`
- 背景：网格 + 示波器 Canvas + 鼠标视差 + 点击涟漪（见 `background-mouse-interaction.md`）
- 业务完整：Upload 分组 Method、Overview pipeline、History method/route 列

**本次目标：** 解决截图中暴露的「内页偏平、卡片同质、浅色对比不足、Plotly/表格不够机架化」等问题，让 **Home 的戏剧感延伸到所有路由**。

---

## 技术约束（必须遵守）

| 项 | 要求 |
|----|------|
| 路径 | 仅 `analysis/denoise_selection/webapp/frontend/` |
| 栈 | React 18 + TS + Vite，纯 CSS（`studio-console.css` 等） |
| 禁止 | Tailwind、MUI、Ant Design、Inter/Roboto、紫色渐变 |
| 字体 | Antonio（Display）+ Newsreader（正文）+ Fragment Mono（数据） |
| API/路由 | 不改 `api.ts`、`router.tsx` 契约 |
| 测试 | `npm run build` + `npm test` 通过 |
| i18n | 新增文案写入 `src/i18n/index.ts` 中英文键 |

---

## 截图诊断 — 待改进清单（按优先级）

### P0 — 浅色主题与对比度（截图多为 Light）

**问题：** 浅色下背景波形/网格偏淡，卡片与背景对比略弱；`--signal` 在浅底上饱和度不足。

**改进：**
1. 在 `[data-theme="light"]` 单独调校：
   - `--signal: #007a62`，`--signal-glow` 提高可见度
   - 背景网格 `opacity` 0.06→0.12，示波器 canvas `opacity` 0.35→0.55
   - 卡片 `box-shadow` 略加深，边框 `--panel-border-strong` 更明显
2. 光标光晕在浅色下改用「青绿光斑 + 浅灰外圈」，避免发白一片
3. 验收：WCAG AA，正文对比度 ≥ 4.5:1

**文件：** `tokens.css`、`studio-console.css`、`ScopeCanvas.tsx`（读取 theme 色）

---

### P0 — 内页与首页视觉断层

**问题：** Home 有大字标 + 倾斜 MOD-01 机架卡；Upload/Overview/Charts 仅为普通白卡片，品牌感断裂。

**改进 — 引入统一 `RackPanel` 组件：**

```tsx
// 建议新建 components/RackPanel.tsx
// props: moduleId="MOD-02", label="INPUT", led="active"|"processing"|"error"|"idle", title, subtitle, children
```

- 顶部细条：`MOD-xx / 通道名` + 右侧 LED（与 Home `console-module-head` 一致）
- 可选轻微 `rotate(-0.6deg)` 仅用于 Home 右侧统计卡，**业务页保持 0deg**
- 所有 `GlassCard` 逐步换为 `RackPanel` 或给 `GlassCard` 增加 `moduleId` / `channel` props

**优先页面：** Upload → Overview 顶部状态条 → Progress → Charts 工具条

---

### P1 — Upload 页（截图 2）

| 问题 | 方案 |
|------|------|
| 拖拽区视觉权重低 | 加大 `file-drop` 高度；有文件时显示波形缩略装饰线（CSS 即可） |
| Method 下拉仍像系统控件 | 自定义 `MethodSelector`：分组标签 + 选中项旁 LED + hint 区做成机架「LCD 读数」样式 |
| deepfilter 环境提示不够醒目 | hint 区左侧加琥珀色 `ENV` 徽章：`DEEPFILTER_CONDA_ENV=dfnet311` |
| 主 CTA「UPLOAD AND PROCESS」偏灰 | `glass-btn-primary` 在 light 下填充 `--signal-dim`，文字 `--signal`，hover 发光 |
| 流程 hint 一行字太弱 | 改为与 Home 一致的 `console-flow` 胶囊，当前步 Upload 高亮 |

**文件：** `UploadConfigPage.tsx`、`MethodSelector.tsx`、`upload-overview.css`

---

### P1 — Overview 页（截图 3）

| 问题 | 方案 |
|------|------|
| 状态区与 Pipeline 分离感强 | 合并为顶部 **「任务机架」** 横条：文件名 + StatusBadge + method/route 单行 mono |
| Pipeline deepfilter 失配告警不够「报警灯」 | `pipeline-alert` 时卡片顶条改红色 + LED 快闪动画 |
| Audio Compare 像普通表单 | 改成 **调音台推子条**：A/B/R 三轨并排，每轨 LED + 音量滑条纵向或横向条纹化 |
| 波形卡片加载空窗 | 已有 skeleton，加深对比、加「SCANNING…」mono 文案 |
| 指标区 8 个 chip 平铺 | 改为 2×4 **机架读数**：大数字 + 小标签，route/reason 占整行宽 |

**文件：** `ResultOverviewPage.tsx`、`AudioComparePlayer.tsx`、`PipelineSummary.tsx`、`upload-overview.css`

---

### P1 — Charts 页（截图 4）

| 问题 | 方案 |
|------|------|
| Plotly 默认色与 Signal Console 不协调 | 扩展 `plotTheme.ts`：背景 `#fafbfc`、网格 `#e2e8f0`、曲线 primary `#007a62` / secondary `#c47a00` |
| 图表卡片间距紧、信息密度高 | `chart-grid` gap 16→20px；`plot-shell` 顶栏高度统一 |
| 筛选栏与图表区割裂 | 筛选关键词匹配时 group title + plot title **高亮 mark**（已有 highlight，加强颜色） |
| 折叠组标题不够「模块感」 | `chart-group-header` 左侧加 `GRP-01` 式 mono 编号 |
| 移动端双列波形挤压 | `<768px` 强制单列（已有），Plotly `height` 跟随 `chartHeight` 选择器 |

**文件：** `ChartCenterPage.tsx`、`plotTheme.ts`、`glass.css` chart 区

---

### P1 — History 页（截图 5）

| 问题 | 方案 |
|------|------|
| 表格像默认 HTML table | 行 hover 微高亮；表头 sticky；`Pipeline` 列 mono + 溢出 tooltip |
| Status 徽章与行对齐弱 | 状态列固定宽；`failed` 行左侧 2px 红条 |
| method=deepfilter 且 pipeline 非 deepfilter | 行背景淡红（读 task JSON 的 route） |
| 空状态仅有文案 | 机架空槽插画 + CTA「开始分析」链到 /upload |
| 操作按钮三枚并排拥挤 | `SELECT` ghost、`OPEN` primary、`DELETE` danger 色区分 |

**文件：** `HistoryPage.tsx`、`upload-overview.css`

---

### P2 — 导航与全局

| 问题 | 方案 |
|------|------|
| Task ID 过长截断 | 显示 `ac1c9…3bb7` 缩写，hover 显示全量；Copy 成功 toast 样式化 |
| 当前路由指示在浅色下偏淡 | active 链接：底边 2px signal 实线 + 背景 `--signal-dim` |
| 每张卡片右上角 LED 重复、干扰 | 仅 **RackPanel 顶栏** 保留 LED；普通子卡片 `showLed={false}` |
| 页面切换生硬 | `page-route` 增加 280ms fade + 8px slide（`motion.css`） |
| Progress 页简陋 | VU 条 + 百分比 mono 大字 + processing 时背景 `studio-atmosphere-processing` 联动（已部分实现，UI 补全） |

**文件：** `GlassNav.tsx`、`GlassCard.tsx`、`TaskProgressPage.tsx`、`motion.css`

---

### P2 — 微交互与无障碍

- 所有 `glass-btn`：`focus-visible` 2px `--focus-ring` 外框
- 滑条 `input[type=range]`：轨道/拇指改成机架推子样式（`studio-console.css`）
- `prefers-reduced-motion`：保留静态背景，禁用 tilt/涟漪/LED 脉冲
- 键盘：`FileDropZone` Enter/Space 已支持，补充 `aria-live` 给 Progress/Upload 状态消息

---

## 设计系统补充（CSS 变量）

在 `tokens.css` 增加机架语义 token，供全站复用：

```css
--rack-module-bg: var(--glass-bg-strong);
--rack-channel-label: var(--font-mono);
--rack-led-on: var(--signal);
--rack-led-warn: var(--amber);
--rack-led-fault: var(--danger);
--rack-lcd-bg: var(--bg-base);
--rack-lcd-text: var(--signal);
```

---

## 建议实施顺序（供 AI 分 PR / commit）

1. **浅色主题调校** + Plotly theme 统一（见效快，风险低）
2. **`RackPanel` 组件** + Upload / Overview 接入
3. **Audio Compare 调音台化** + Pipeline 告警强化
4. **History 表格机架化** + deepfilter 失配行高亮
5. **Charts 分组编号 + 筛选高亮增强**
6. **导航 Task 缩写 + 卡片 LED 降噪**
7. 全站 `npm run build && npm test`，中英文截图对比

---

## 验收标准

- [x] 浅色 / 深色主题下，背景动效与前景卡片均清晰可辨
- [x] Home 与 Upload/Overview 至少共享同一套「MOD-xx 机架头」语言
- [x] Upload 选 deepfilter 时，环境要求一处可见、不可误解
- [x] Overview 的 method/route/reason 在 3 秒内可扫读；失配时红色告警醒目
- [x] History 可一眼区分 completed / failed / pipeline 异常
- [x] Plotly 图表配色与 Signal Console 一致，无默认 Plotly 蓝紫突兀感
- [x] 无新增 UI 框架；build + test 通过

---

## 一句话版（快速粘贴）

> 在 Denoise Studio Signal Console 现有代码上精修：强化浅色主题对比、用 RackPanel 统一内页机架语言、Upload Method LCD 提示、Overview 调音台试听区、Plotly 青琥珀主题、History 表格状态/失配高亮、导航 Task 缩写；保留 Antonio/Newsreader/Fragment Mono 与鼠标互动背景；只改 frontend，禁止 Tailwind/紫色渐变。

---

## 相关文档

- 背景互动：`docs/prompts/background-mouse-interaction.md`（已实现，勿重复造轮子）
- 启动脚本：`start-webapp.ps1`
- 版本标签：`web-signal-console-interactive`
