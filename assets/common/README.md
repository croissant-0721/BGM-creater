# 公共资源文件说明

## 目录结构

```
assets/
├── css/
│   └── common/
│       └── billing-common.css    # 账单页面公共样式
└── js/
    └── common/
        ├── billing-common.js      # 账单页面公共 JavaScript
        └── tailwind-config.js     # Tailwind CSS 配置
```

## 文件说明

### 1. billing-common.css

公共样式文件，包含：
- 渐变文字效果 (`.gradient-text`)
- 淡入动画 (`.fade-in`)
- 自定义滚动条样式
- 主题色工具类
- 响应式工具
- 打印样式

**使用方式：**
```html
<link rel="stylesheet" href="../assets/css/common/billing-common.css">
```

### 2. billing-common.js

公共 JavaScript 文件，包含：

#### 主题管理 (`initTheme()`)
- 自动加载保存的主题
- 主题切换功能
- LocalStorage 持久化

#### Chart.js 管理 (`loadChartJS()`)
- 多 CDN 自动切换
- 失败重试机制
- Promise 支持

#### 分页类 (`Pagination`)
- 通用的表格分页功能
- 支持自定义渲染
- 页码导航

#### 日期工具
- `formatDate()` - 日期格式化
- `getDateRange()` - 获取日期范围

#### 图表工具
- `getChartColors()` - 获取主题颜色
- `createChartOptions()` - 创建图表配置

**使用方式：**
```html
<script src="../assets/js/common/billing-common.js"></script>
```

**示例代码：**
```javascript
// 初始化主题（自动执行）
// 主题已包含在 DOMContentLoaded 事件中

// 使用分页类
const pagination = new Pagination({
    data: dataArray,
    pageSize: 10,
    tableBodyId: 'detailTableBody',
    renderRow: (item) => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${item.name}</td><td>${item.value}</td>`;
        return row;
    }
});

// 格式化日期
const formatted = formatDate(new Date(), 'YYYY-MM-DD HH:mm');

// 获取日期范围
const range = getDateRange('7days');
console.log(range.start, range.end);
```

### 3. tailwind-config.js

Tailwind CSS 配置文件，包含：
- 主题色配置 (brand 颜色系列)
- 自定义动画
- 字体配置

**使用方式：**
```html
<script src="https://cdn.tailwindcss.com"></script>
<script src="../assets/js/common/tailwind-config.js"></script>
```

## 在新页面中使用

### HTML 模板

```html
<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>页面标题 | Panqu AI</title>

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    <!-- Icons -->
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">

    <!-- Common Styles -->
    <link rel="stylesheet" href="../assets/css/common/billing-common.css">

    <!-- Tailwind CSS + DaisyUI -->
    <link href="https://cdn.jsdelivr.net/npm/daisyui@4.6.0/dist/full.min.css" rel="stylesheet" type="text/css" />
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- Tailwind Config -->
    <script src="../assets/js/common/tailwind-config.js"></script>
</head>
<body>
    <!-- 页面内容 -->

    <!-- Common JavaScript -->
    <script src="../assets/js/common/billing-common.js"></script>

    <!-- Page-specific JavaScript -->
    <script src="your-page.js"></script>
</body>
</html>
```

## 已更新的页面

以下页面已更新为使用公共资源：

1. `billing_demo/admin-dashboard.html` - 管理后台
2. `billing_demo/billing.html` - 个人账单
3. `billing_demo/client_billing.html` - 企业账单
4. `billing_demo/billing-detail.html` - 项目费用详情

## 注意事项

1. **路径问题**：确保相对路径正确，根据页面所在位置调整 `../` 的数量
2. **依赖顺序**：先加载公共资源，再加载页面特定脚本
3. **Chart.js**：如需使用图表功能，请调用 `loadChartJS()` 或在页面中直接引入 Chart.js
4. **主题切换**：确保页面中有 `id="theme-toggle"` 的 checkbox 元素

## 扩展指南

### 添加新的公共样式

在 `billing-common.css` 中添加：

```css
.your-class {
    /* 样式定义 */
}
```

### 添加新的公共函数

在 `billing-common.js` 中添加：

```javascript
function yourFunction() {
    // 函数实现
}
```

### 自定义 Tailwind 配置

编辑 `tailwind-config.js` 中的 `window.tailwindConfig` 对象。
