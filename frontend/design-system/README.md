# Design System

这是当前前端统一视觉系统的入口。

## 设计目标

- 默认深色 SaaS 风格
- 所有页面统一视觉语言
- 所有业务页面统一布局
- 所有按钮、输入框、卡片、徽章、表格、弹窗统一来源

## 目录说明

- `colors.ts`：颜色规范
- `typography.ts`：字体规范
- `spacing.ts`：间距规范
- `themes/dark.ts`：深色主题
- `components/`：统一组件出口（按钮、卡片、输入框、状态徽章、统一页面布局等）

## 使用规则

1. 页面和业务组件统一从 `@/design-system/components` 引入组件
2. 业务页面统一使用 `PageLayout`
3. 不再直接在页面里堆新的独立 UI 风格
4. 构建前会执行 `npm run ui:sync` 做统一性检查
5. 所有状态统一走 `Badge / StatusBadge / StatusAlert`
