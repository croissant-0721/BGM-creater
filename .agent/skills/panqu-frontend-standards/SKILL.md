---
name: Panqu AI Frontend Standards
description: Frontend style guidelines and DaisyUI component standards for Panqu AI project.
---

# 盼趣 AI 前端样式及规范 (Frontend Standards)

> 基于 admin-dashboard.html 和 Projects.html 生成的统一前端规范
> **核心原则: 严格遵守 DaisyUI 组件标准和 HTML 结构**

## 技术栈 (Technology Stack)

- **Tailwind CSS** - 实用工具优先的 CSS 框架
- **DaisyUI v5+** - 基于 Tailwind 的最新版组件库
- **RemixIcon v3.5.0** - 图标库
- **Inter** - 主要字体 (Google Fonts)
- **Chart.js v4.4.1** - 数据可视化

---

## DaisyUI 核心原则 (Core Principles)

### ⚠️ 必须遵守的规则

1. **使用 DaisyUI 标准组件类**: 使用 `.navbar`, `.btn`, `.card`, `.dropdown`, `.menu` 等。
2. **遵循标准 HTML 结构**:
   - Navbar 必须包含 `.navbar-start`, `.navbar-center`, `.navbar-end`。
   - Menu 必须遵循 `ul.menu > li > a` 结构。
   - Card 必须遵循 `.card > figure + .card-body` 结构。
3. **最小化自定义 CSS**: 95% 使用 DaisyUI 标准类，仅 5% 用于渐变、特殊动画和项目特定增强。
4. **不要覆盖 DaisyUI 核心样式**: 不要在自定义 CSS 中重新定义 DaisyUI 类的显示属性。
5. **使用主题变量**: 使用 `bg-primary`, `text-base-content` 等，不要硬编码颜色。

---

## 颜色与字体 (Colors & Typography)

### 品牌色

- **Kline (盼趣蓝)**: `#002FA7` (主色), 用于按钮、图标、按钮背景。
- **渐变文本**: 使用 `.gradient-text` 类。
- **暗色模式文字**: 必须在暗黑模式下使用白色或接近白色 (90-95% 白色)，确保可读性。

### Avatar
```html
<div class="avatar placeholder">
  <div class="bg-primary text-primary-content rounded-full w-10">
    <span class="text-sm font-bold">C</span>
  </div>
</div>
```

---

## 设置与侧边栏 (Settings & Sidebar)

### 垂直导航侧边栏
```html
<div class="grid grid-cols-1 md:grid-cols-12 gap-8">
  <div class="md:col-span-3">
    <ul class="menu bg-base-100 rounded-2xl p-2 shadow-sm border border-base-200">
      <li><a class="active"><i class="ri-user-line"></i> 个人信息</a></li>
      <li><a><i class="ri-shield-keyhole-line"></i> 修改密码</a></li>
    </ul>
  </div>
  <div class="md:col-span-9">
    <div class="tab-pane fade-in bg-base-100 rounded-2xl p-8 border border-base-200">
      <!-- 内容区 -->
    </div>
  </div>
</div>
```

### 带验证的输入框
```html
<div class="form-control">
  <label class="label"><span class="label-text">输入标题</span></label>
  <input type="text" class="input input-bordered w-full focus:border-kline" />
  <div class="text-error text-xs mt-1 hidden">错误信息提示</div>
  <label class="label"><span class="label-text-alt text-base-content/40">辅助说明文本</span></label>
</div>
```
### 字体规范

- **主标题**: `text-3xl font-bold` (30px)
- **卡片标题**: `text-xl` / `text-lg`
- **统计数据**: `text-2xl font-bold`
- **正文**: `text-sm` (14px)
- **描述文本**: `text-base-content/60` (半透明)

---

## 布局系统 (Layout System)

### 容器与网格

- **主容器**: `container mx-auto px-4 py-8 max-w-7xl`
- **响应式网格**: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6`
- **侧边栏导航布局**: `md:grid-cols-12` 结构，左侧 `md:col-span-3` (导航)，右侧 `md:col-span-9` (内容)。
- **间距**: 统计卡片使用 `p-5`，信息卡片使用 `p-4`，设置页内容建议使用 `p-8`。

---

## 表单与验证 (Forms & Validation)

### 标准模式
- **验证反馈**: 失败时使用 `text-error text-xs mt-1` 显示错误信息，并配合 `hidden` 类进行动态切换。
- **输入框状态**: 使用 `focus:border-kline` 提供品牌化的焦点反馈。
- **辅助文本**: 使用 `label-text-alt text-base-content/40`。

---

## 动画效果 (Animations)

- **淡入动画**: 使用 `.fade-in` 类 (`@keyframes fadeIn`)。
- **悬停缩放**: `hover:scale-105 transition-transform`。
- **卡片增强**: `.card-hover` 结合投影效果。

---

## 代码组织 (Code Organization)

### 文件预览与引入

- **自定义样式位置**: `assets/css/project/project-styles.css`
- **引入顺序**:
  1. DaisyUI + Tailwind (CDN)
  2. Tailwind Config (JavaScript)
  3. 项目特定样式 (CSS)

---

## 参考资料 (Resources)

- [组件规范与示例 (examples/components.md)](examples/components.md)
- [更新日志与版本历史 (resources/CHANGELOG.md)](resources/CHANGELOG.md)

---

## 最佳实践清单 (Best Practices)

- [ ] 100% 遵循 DaisyUI 官方 HTML 结构。
- [ ] 优先使用 Tailwind 工具类而非定义新 CSS 类。
- [ ] 所有图片均设置 `loading="lazy"`。
- [ ] 页面加载必须配合 `.fade-in` 动画。
- [ ] 特殊数据卡片必须包含图标，间距使用 `gap-2`。
