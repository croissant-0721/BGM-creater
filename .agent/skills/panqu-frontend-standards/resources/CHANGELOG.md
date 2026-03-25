# 更新日志 (Changelog)

## 2026-01-20 (v3.1.0)
- **DaisyUI 规范调整与优化**
  - 明确自定义类的使用规范: `navbar-with-sidebar` 和 `gradient-text`
  - 新增自定义类必须在独立 CSS 文件中定义的要求
  - 优化项目页面导航栏结构，确保完全符合 DaisyUI 标准
  - 规范化 Stats 组件的使用方式

- **组件规范完善**
  - 新增 Stats 组件标准结构 and 使用规范
  - 新增 Join 组件规范（用于搜索框和分页）
  - 新增 Indicator 组件规范（用于通知徽章）
  - 完善 Form Control 组件规范

- **项目结构优化**
  - 要求所有自定义样式必须放在 `assets/css/` 目录下
  - 规范化 Tailwind 配置文件的位置 and 命名
  - 明确项目特定样式文件的组织方式

- **最佳实践更新**
  - 强调 95% 使用 DaisyUI 标准类，仅 5% 使用自定义类
  - 自定义类仅用于: 渐变效果、特殊动画、项目特定布局增强
  - 禁止覆盖 DaisyUI 核心组件样式

## 2025-01-20 (v3.0.1)
- **组件规范完善**
  - 新增 Swap 组件规范(主题切换按钮)
  - 新增 Modal 组件规范(HTML Dialog 方式)
  - 更新 Avatar 组件规范(修正用户头像示例结构)
  - 添加 RemixIcon 图标居中问题解决方案

- **HTML 结构标准化**
  - Modal 使用 `<dialog>` 元素 and 标准结构
  - Avatar 使用正确的嵌套结构: `avatar.placeholder` > `div` > `span`
  - Swap 组件图标居中: 添加 flex 布局到 `<i>` 标签
  - 移除不必要的 text-center and 自定义布局类

- **CSS 优化**
  - 项目样式文件添加 swap 图标居中样式
  - 强调遵循 DaisyUI 官方文档标准
  - 避免覆盖 DaisyUI 默认样式

## 2025-01-20 (v3.0.0)
- **DaisyUI 标准化重大更新**
  - 新增 "DaisyUI 核心原则" 章节，强调必须严格遵守 DaisyUI 标准
  - 明确要求使用 navbar-start/navbar-end 替代自定义 flex 布局
  - 规范化所有组件的 HTML 结构，必须符合 DaisyUI 标准
  - 强调不要在自定义 CSS 中覆盖 DaisyUI 样式
  - 要求使用 DaisyUI 变量而非硬编码颜色

- **项目页面导航栏规范**
  - 添加项目页面标准导航栏结构
  - 规范化导航菜单使用 `.menu.menu-horizontal`
  - 明确菜单项内的图标 and 文字由 DaisyUI 自动处理
  - 添加 navbar-end 按钮组规范 (主题切换、通知、用户头像)
  - 统一使用 `dropdown.dropdown-end` 对齐下拉菜单

- **组件结构标准化**
  - Card 组件必须使用标准结构: `.card` > `figure` + `.card-body`
  - Dropdown 组件标准结构: `div.dropdown` > `div[tabindex]` + `ul.dropdown-content`
  - Menu 组件标准结构: `ul.menu` > `li` > `a`
  - Modal 组件标准结构: `dialog.modal` > `div.modal-box` + `form.modal-backdrop`

- **常见错误示例**
  - ❌ 使用 `flex-1/flex-none` 替代 `navbar-start/navbar-end`
  - ❌ 在 menu 链接内添加 `flex items-center gap-2`
  - ❌ 自定义按钮大小，应使用 DaisyUI 的 `btn-sm/btn/btn-lg`
  - ❌ 硬编码样式，应使用 DaisyUI 主题变量

## 2025-01-18 (v2.2.0)
- **暗黑模式文字优化**
  - 所有文字在暗黑模式下统一使用白色或接近白色 (90-95% 白色)
  - 提升次要文字透明度: `/60` 从 70% 提升到 95%, `/70` 提升到 95%
  - 优化品牌色在暗黑模式下的对比度
  - 新增全面的暗黑模式文字颜色优化规则

- **页面结构统一**
  - 统一所有账单页面的 HTML 结构 and 缩进
  - 统一图表容器高度为 `h-64` (256px)
  - 统一统计卡片使用 `text-base-content` 颜色
  - 统一 z-index 为 `z-[1]`
  - 添加图标到所有统计卡片

- **组件规范更新**
  - 统计卡片必须包含图标: `flex items-center gap-2`
  - 图标颜色使用 `text-base-content/50`
  - 标准化下拉菜单 z-index and 样式

## 2025-01-18 (v2.1.0)
- **Logo 规范更新**
  - 添加品牌 logo 图片资源规范
  - 更新导航栏 and 页脚的 logo 使用方式
  - 支持 logo 图片 + 渐变文字组合
  - 保留侧边栏的图标 + 文字选项
  - 统一 logo 高度为 `h-8` (32px)

## 2025-01-10 (v2.0.0)
- **尺寸标准化调整**
  - 优化表格单元格尺寸: padding 从 1rem 减小到 0.75rem, 字号从 0.875rem 减小到 0.8125rem
  - 调整页面标题: 从 `text-4xl md:text-5xl` 改为 `text-3xl` (固定尺寸)
  - 优化数字显示: 统一使用 `text-2xl` 替代 `text-3xl md:text-4xl`
  - 卡片内边距微调: 统计卡片使用 `p-5`, 信息卡片使用 `p-4`
  - 更新所有相关组件规范 and 示例代码
  - 统一为标准 DaisyUI 的紧凑风格

## 2025-01-09 (v1.0.0)
- 初始版本
- 基于 index.html and admin-dashboard.html 生成
- 包含完整的颜色、字体、布局、组件规范
- 添加动画效果 and 主题切换规范
- 添加响应式设计 and 最佳实践
