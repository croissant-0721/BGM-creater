# 盼趣AI 前端设计规范

> 版本: 1.0
> 更新时间: 2025-01-08
> 基于技术栈: Tailwind CSS + DaisyUI

## 📋 目录

- [配色方案](#配色方案)
- [字体规范](#字体规范)
- [布局系统](#布局系统)
- [组件库](#组件库)
- [动画效果](#动画效果)
- [响应式设计](#响应式设计)
- [代码规范](#代码规范)

---

## 🎨 配色方案

### 品牌色 - 克莱因蓝 (Klein Blue)

```css
/* 主品牌色 - 国际克莱因蓝标准值 */
--kline-600: #002FA7;

/* 克莱因蓝色板 */
--kline-50: #E8EEFF;
--kline-100: #C4D4FF;
--kline-200: #9DB6FF;
--kline-300: #7599FF;
--kline-400: #4D7CFF;
--kline-500: #2560FF;
--kline-600: #002FA7;  /* 主色 */
--kline-700: #002687;
--kline-800: #001D67;
--kline-900: #001447;
```

### Tailwind Config 配置

```javascript
colors: {
    kline: {
        DEFAULT: '#002FA7',
        50: '#E8EEFF',
        100: '#C4D4FF',
        200: '#9DB6FF',
        300: '#7599FF',
        400: '#4D7CFF',
        500: '#2560FF',
        600: '#002FA7',
        700: '#002687',
        800: '#001D67',
        900: '#001447',
    }
}
```

### 使用示例

```html
<!-- 主按钮 -->
<button class="bg-kline-600 text-white hover:bg-kline-700">
    克莱因蓝按钮
</button>

<!-- 文字高亮 -->
<span class="text-kline-600">克莱因蓝文字</span>

<!-- 图标 -->
<i class="ri-robot-2-fill text-kline-600 text-2xl"></i>
```

### 语义化颜色

使用 DaisyUI 语义化颜色，自动适配深浅主题：

```html
<!-- 主按钮 -->
<button class="btn btn-primary">主要操作</button>

<!-- 次要按钮 -->
<button class="btn btn-secondary">次要操作</button>

<!-- 强调按钮 -->
<button class="btn btn-accent">强调操作</button>

<!-- 成功/警告/错误 -->
<button class="btn btn-success">成功</button>
<button class="btn btn-warning">警告</button>
<button class="btn btn-error">错误</button>
```

### 渐变色

```css
/* 品牌渐变 */
.gradient-brand {
    background: linear-gradient(135deg, #002FA7 0%, #2560FF 50%, #4D7CFF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Hero 背景渐变 */
.hero-gradient {
    background: linear-gradient(135deg, #0a0a0a 0%, #001447 50%, #0a0a0a 100%);
}

/* CTA 渐变 */
.cta-gradient {
    background: linear-gradient(135deg, #002FA7 0%, #2560FF 100%);
}
```

---

## ✍️ 字体规范

### 字体家族

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### 字体大小层级

```html
<!-- 标题 H1 -->
<h1 class="text-5xl md:text-7xl font-bold">超大标题</h1>

<!-- 标题 H2 -->
<h2 class="text-4xl md:text-5xl font-bold">大标题</h2>

<!-- 标题 H3 -->
<h3 class="text-3xl font-bold">中标题</h3>

<!-- 标题 H4 -->
<h4 class="text-2xl font-bold">小标题</h4>

<!-- 正文 -->
<p class="text-lg">正文内容</p>

<!-- 辅助文字 -->
<p class="text-sm">辅助说明</p>

<!-- 小字 -->
<p class="text-xs">最小文字</p>
```

### 字重

```html
<!-- 常规 -->
<p class="font-normal">常规文字</p>

<!-- 中等 -->
<p class="font-medium">中等粗细</p>

<!-- 加粗 -->
<p class="font-bold">加粗文字</p>
```

### 文字颜色（深色模式）

```html
<!-- 主要文字 -->
<p class="text-white">白色主要文字</p>

<!-- 次要文字 -->
<p class="text-white/80">80%透明度白色</p>
<p class="text-white/70">70%透明度白色</p>
<p class="text-white/60">60%透明度白色</p>

<!-- 品牌色文字 -->
<p class="text-kline-600">克莱因蓝文字</p>
```

---

## 📐 布局系统

### 容器

```html
<!-- 标准容器 -->
<div class="container mx-auto px-4 max-w-7xl">
    <!-- 内容 -->
</div>

<!-- 小容器 -->
<div class="container mx-auto px-4 max-w-5xl">
    <!-- 内容 -->
</div>

<!-- 居中容器 -->
<div class="container mx-auto px-4 max-w-3xl">
    <!-- 内容 -->
</div>
```

### 间距规范

```html
<!-- Section 内边距 -->
<section class="py-20"> <!-- 大间距 80px -->
<section class="py-16"> <!-- 中间距 64px -->
<section class="py-12"> <!-- 小间距 48px -->
<section class="py-8">  <!-- 微间距 32px -->

<!-- Grid 间距 -->
<div class="grid gap-6">  <!-- 标准间距 -->
<div class="grid gap-4">  <!-- 紧凑间距 -->
<div class="grid gap-8">  <!-- 宽松间距 -->

<!-- Flex 间距 -->
<div class="flex gap-3">
```

### 网格系统

```html
<!-- 响应式网格 -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- 自适应列 -->
</div>

<!-- 固定列数 -->
<div class="grid grid-cols-4 gap-6">
    <!-- 4列网格 -->
</div>

<!-- 不等宽列 -->
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div class="lg:col-span-2">占2列</div>
    <div>占1列</div>
</div>
```

---

## 🧩 组件库

### 按钮

#### 主要按钮（克莱因蓝）

```html
<a href="#" class="btn btn-lg hover:scale-105 transition-transform text-white border-0"
   style="background-color: #002FA7;">
    <i class="ri-rocket-line"></i>
    主要按钮
</a>
```

#### 次要按钮（描边）

```html
<a href="#" class="btn btn-outline btn-sm hover:scale-105 transition-transform
   border-kline hover:bg-kline hover:text-white">
    次要按钮
</a>
```

#### 幽灵按钮

```html
<a href="#" class="btn btn-ghost hover:text-kline">
    幽灵按钮
</a>
```

#### 按钮尺寸

```html
<button class="btn btn-lg">大按钮</button>
<button class="btn">默认按钮</button>
<button class="btn btn-sm">小按钮</button>
<button class="btn btn-xs">超小按钮</button>
```

### 卡片

#### 基础卡片

```html
<div class="card bg-base-100 shadow-xl card-hover transition-all duration-300">
    <div class="card-body">
        <h3 class="card-title">卡片标题</h3>
        <p class="text-base-content/70">卡片内容</p>
    </div>
</div>
```

#### 带图片卡片

```html
<div class="card bg-base-100 shadow-xl card-hover transition-all duration-300">
    <figure class="relative">
        <img src="image.jpg" alt="描述" class="w-full h-48 object-cover" />
        <div class="absolute inset-0 bg-black/50 flex items-center justify-center
            opacity-0 hover:opacity-100 transition-opacity cursor-pointer">
            <button class="btn btn-circle btn-lg text-white border-0"
               style="background-color: #002FA7;">
                <i class="ri-play-fill text-3xl"></i>
            </button>
        </div>
    </figure>
    <div class="card-body">
        <h3 class="card-title">卡片标题</h3>
    </div>
</div>
```

### Badge 标签

```html
<!-- 主要标签 -->
<div class="badge badge-primary badge-lg">
    <i class="ri-sparkling-fill mr-1"></i>
    NEW
</div>

<!-- 次要标签 -->
<div class="badge badge-secondary">Beta</div>

<!-- 自定义颜色标签 -->
<div class="badge" style="background-color: #002FA7; color: white;">
    自定义
</div>
```

### 导航栏

```html
<div class="navbar bg-base-100/80 backdrop-blur-md shadow-lg sticky top-0 z-50">
    <div class="flex-1">
        <a href="#" class="btn btn-ghost text-xl">
            <i class="ri-robot-2-fill text-kline-600 text-2xl"></i>
            <span class="gradient-text font-bold">盼趣AI</span>
        </a>
    </div>
    <div class="flex-none">
        <ul class="menu menu-horizontal px-1 gap-2 hidden md:flex">
            <li><a href="#" class="hover:text-kline-600 transition-colors font-medium">导航</a></li>
        </ul>
    </div>
</div>
```

### 表单元素

```html
<!-- 输入框 -->
<input type="text" placeholder="请输入..."
    class="input input-bordered w-full focus:outline-none focus:ring-2 focus:ring-kline-600" />

<!-- 下拉选择 -->
<select class="select select-bordered w-full focus:outline-none focus:ring-2 focus:ring-kline-600">
    <option>选项1</option>
    <option>选项2</option>
</select>

<!-- 进度条 -->
<progress class="progress progress-kline-600 w-full" value="70" max="100"></progress>
```

### 表格

```html
<div class="overflow-x-auto">
    <table class="table table-zebra table-pin-rows">
        <thead class="bg-base-200">
            <tr>
                <th>列名</th>
                <th>列名</th>
            </tr>
        </thead>
        <tbody>
            <tr class="hover:bg-base-200/50 transition-colors">
                <td>数据</td>
                <td>数据</td>
            </tr>
        </tbody>
    </table>
</div>
```

---

## 🎭 动画效果

### 淡入动画

```css
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in {
    animation: fadeIn 0.8s ease-out;
}
```

### 悬停效果

```html
<!-- 卡片悬停 -->
<div class="card-hover hover:scale-105 transition-all duration-300">
    <!-- 内容 -->
</div>

<!-- 按钮悬停 -->
<button class="hover:scale-105 transition-transform">
    按钮
</button>

<!-- 链接悬停 -->
<a href="#" class="hover:text-kline-600 transition-colors">
    链接
</a>
```

### 脉冲动画

```html
<!-- 脉冲标签 -->
<div class="badge badge-secondary animate-pulse">
    Live
</div>
```

---

## 📱 响应式设计

### 断点系统

```css
/* 移动端优先 */
sm: 640px   /* 小屏幕 */
md: 768px   /* 平板 */
lg: 1024px  /* 桌面 */
xl: 1280px  /* 大桌面 */
2xl: 1536px /* 超大屏幕 */
```

### 响应式示例

```html
<!-- 文字大小 -->
<h1 class="text-5xl md:text-7xl font-bold">响应式标题</h1>

<!-- 布局切换 -->
<div class="flex flex-col md:flex-row gap-4">
    <!-- 移动端垂直，桌面端水平 -->
</div>

<!-- 网格列数 -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- 响应式列 -->
</div>

<!-- 显示/隐藏 -->
<div class="hidden md:block">桌面端显示</div>
<div class="block md:hidden">移动端显示</div>
```

### 移动端优化

```html
<!-- 触摸友好的按钮尺寸 -->
<button class="btn btn-lg min-h-[44px]">
    移动端按钮
</button>

<!-- 响应式间距 -->
<section class="py-12 md:py-20">
    <!-- 移动端小间距，桌面端大间距 -->
</section>
```

---

## 💻 代码规范

### HTML 结构

```html
<!-- 使用语义化标签 -->
<header>...</header>
<nav>...</nav>
<main>
    <section>...</section>
    <article>...</article>
</main>
<footer>...</footer>
```

### CSS 类名顺序

```html
<!-- 推荐顺序 -->
<div class="布局 flex flex-col 响应式 md:grid 尺寸 w-full
           间距 gap-4 颜色 bg-white 文字 text-black
           过渡 transition-all 悬停 hover:scale-105">
```

### Tailwind 最佳实践

```html
<!-- ✅ 推荐：使用 Tailwind 工具类 -->
<div class="bg-white text-black p-6 rounded-lg shadow-xl">
    自定义样式
</div>

<!-- ❌ 避免：过度使用内联样式 -->
<div style="background-color: white; padding: 24px;">
    自定义样式
</div>
```

### 组件封装

```html
<!-- 可复用的 Hero Section -->
<section class="relative min-h-screen flex items-center justify-center overflow-hidden">
    <div class="absolute inset-0 z-0">
        <div class="hero-gradient absolute inset-0"></div>
        <video class="absolute inset-0 w-full h-full" autoplay muted loop playsinline
               style="opacity: 0.3; object-fit: cover; object-position: center;">
            <source src="assets/videos/hero_bg.mp4" type="video/mp4">
        </video>
    </div>
    <div class="container mx-auto px-4 py-16 max-w-7xl relative z-10">
        <!-- 内容 -->
    </div>
</section>
```

---

## 🎯 常用设计模式

### Hero Section

```html
<section class="relative min-h-screen flex items-center justify-center">
    <div class="text-center">
        <div class="badge badge-primary badge-lg mb-6">标签</div>
        <h1 class="text-5xl md:text-7xl font-bold mb-6">标题</h1>
        <p class="text-xl mb-8 max-w-2xl mx-auto">描述</p>
        <div class="flex gap-4 justify-center">
            <a href="#" class="btn btn-lg" style="background-color: #002FA7;">主要按钮</a>
            <a href="#" class="btn btn-outline btn-lg">次要按钮</a>
        </div>
    </div>
</section>
```

### Feature Grid

```html
<div class="grid grid-cols-1 md:grid-cols-3 gap-8">
    <div class="card bg-base-100 shadow-xl card-hover transition-all duration-300">
        <div class="card-body items-center text-center">
            <div class="text-5xl text-kline-600 mb-4">
                <i class="ri-compass-line"></i>
            </div>
            <h4 class="card-title">特性标题</h4>
            <p>特性描述</p>
        </div>
    </div>
</div>
```

### CTA Section

```html
<section class="py-20" style="background: linear-gradient(135deg, #002FA7 0%, #2560FF 100%);">
    <div class="container mx-auto px-4 max-w-4xl text-center">
        <h2 class="text-3xl md:text-5xl font-bold text-white mb-8">
            行动号召标题
        </h2>
        <div class="flex gap-4 justify-center">
            <a href="#" class="btn btn-lg bg-white text-kline-600 hover:bg-gray-100 border-0">
                立即开始
            </a>
        </div>
    </div>
</section>
```

---

## 📦 依赖版本

```json
{
  "dependencies": {
    "tailwindcss": "^3.4.0",
    "daisyui": "^4.6.0",
    "remixicon": "^3.5.0"
  }
}
```

### CDN 引用

```html
<!-- Tailwind CSS + DaisyUI -->
<link href="https://cdn.jsdelivr.net/npm/daisyui@4.6.0/dist/full.min.css"
      rel="stylesheet" type="text/css" />
<script src="https://cdn.tailwindcss.com"></script>

<!-- Remix Icon -->
<link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css"
      rel="stylesheet" />

<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
      rel="stylesheet" />
```

---

## 🚀 快速开始

### 1. 新建页面模板

```html
<!DOCTYPE html>
<html lang="zh-CN" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>页面标题 | 盼趣AI</title>

    <!-- 依赖 -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/daisyui@4.6.0/dist/full.min.css" rel="stylesheet" type="text/css" />
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- Tailwind Config -->
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                    },
                    colors: {
                        kline: {
                            DEFAULT: '#002FA7',
                            50: '#E8EEFF',
                            100: '#C4D4FF',
                            200: '#9DB6FF',
                            300: '#7599FF',
                            400: '#4D7CFF',
                            500: '#2560FF',
                            600: '#002FA7',
                            700: '#002687',
                            800: '#001D67',
                            900: '#001447',
                        }
                    }
                }
            }
        }
    </script>

    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in { animation: fadeIn 0.8s ease-out; }

        .gradient-text {
            background: linear-gradient(135deg, #002FA7 0%, #2560FF 50%, #4D7CFF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
    </style>
</head>
<body class="min-h-screen bg-base-100">
    <!-- 内容 -->
</body>
</html>
```

### 2. 复制常用组件

直接从本文档复制所需组件代码，根据项目需求调整。

---

## 📝 注意事项

### 深浅主题适配

- 使用 DaisyUI 语义化颜色（`text-base-content`, `bg-base-100`）
- 避免硬编码颜色值
- 测试深浅两种模式下的显示效果

### 性能优化

- 图片使用 `loading="lazy"`
- 视频使用 `playsinline` 属性
- 避免过度使用动画
- 使用 CDN 加速资源加载

### 可访问性

- 图片添加 `alt` 属性
- 使用语义化 HTML
- 确保颜色对比度足够
- 按钮尺寸不小于 44px × 44px

---

## 🎓 参考资源

- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [DaisyUI 文档](https://daisyui.com/docs/)
- [Remix Icon](https://remixicon.com/)
- [克莱因蓝](https://en.wikipedia.org/wiki/International_Klein_Blue)

---

**维护者**: 盼趣AI 前端团队
**最后更新**: 2025-01-08
