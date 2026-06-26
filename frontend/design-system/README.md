# Design System

这是当前前端的统一 UI 规范入口，目标是把系统保持成一套真正的 SaaS BI 产品界面，而不是开发后台。

## 产品定位

- 深色科技风 BI 驾驶舱
- 融资演示级 SaaS 视觉壳
- 高信息密度卡片系统
- 所有页面统一走商业产品表达，不展示工程调试信息

## 设计规则

### 1. 视觉风格

- 主色：深蓝黑背景 + 蓝紫品牌高亮
- 卡片圆角：`12px / 16px / 20px`
- 阴影：柔和深色投影，不做浮夸发光
- 信息层级：标题 / 副标题 / 核心数值 / 标签 / 操作按钮

### 2. 布局规范

- Dashboard 必须使用 Grid 驾驶舱结构
- 页面内容必须卡片化，不允许纯文本堆叠
- 顶部导航负责全局业务
- 左侧导航负责当前系统入口
- 技术信息统一收口到 `/system/admin`

### 3. 图表规范

- 趋势：Line Chart
- 对比：Bar Chart
- 结构：Pie / Donut Chart
- 强度：Heatmap

### 4. 组件来源

- `colors.ts`：颜色规范
- `typography.ts`：字体规范
- `spacing.ts`：间距规范
- `themes/dark.ts`：深色主题
- `components/`：按钮、卡片、输入框、状态徽章、表格、弹窗、卡片块

## 业务页使用规则

1. 页面和业务组件统一从 `@/design-system/components` 引入
2. 所有业务页面统一使用 `XBorderLayout`
3. 不允许页面直接展示 API 字段结构、raw JSON、debug log
4. 所有状态统一使用 `Badge / StatusBadge / StatusAlert`
5. 所有列表优先提供“表格 + 卡片”两种展示能力
6. 所有新增 UI 只能重组真实接口结果，禁止 mock 数据替代
