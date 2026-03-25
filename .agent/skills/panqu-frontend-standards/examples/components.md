# 组件规范与示例 (Component Specs & Examples)

## 导航栏 (Navbar)

### ⚠️ 必须使用 DaisyUI navbar-start 和 navbar-end 结构

```html
<div class="navbar navbar-with-sidebar sticky top-0 z-50 px-6 bg-base-100 shadow">
  <div class="navbar-start">
    <div class="flex items-center gap-8">
      <a href="index.html" class="flex items-center gap-3">
        <img src="https://panqu.com/assets/img/logo.webp" alt="盼趣AI" class="h-8">
        <span class="gradient-text font-bold text-xl">盼趣 AI</span>
      </a>
      <ul class="menu menu-horizontal px-1 gap-2">
        <li><a href="index.html"><i class="ri-dashboard-line"></i><span>总览</span></a></li>
        <li><a href="Projects.html" class="active"><i class="ri-folder-3-line"></i><span>项目</span></a></li>
      </ul>
    </div>
  </div>
  <div class="navbar-end gap-2">
    <!-- 主题/通知/用户 -->
  </div>
</div>
```

---

## 按钮 (Buttons)

### 主按钮
```html
<button class="btn gap-2 hover:scale-105 transition-transform text-white border-0" style="background-color: #002FA7;">
  <i class="ri-movie-line"></i> 立即制作
</button>
```

---

## 卡片 (Cards)

### 图片卡片
```html
<div class="card bg-base-100 shadow-xl card-hover transition-all duration-300 fade-in">
  <figure><img src="..." class="w-full h-48 object-cover" /></figure>
  <div class="card-body">
    <h3 class="card-title">卡片标题</h3>
  </div>
</div>
```

### 统计卡片 (Stats)
```html
<div class="stats shadow bg-base-100">
  <div class="stat">
    <div class="stat-figure text-primary"><i class="ri-folder-line text-3xl"></i></div>
    <div class="stat-title">总项目数</div>
    <div class="stat-value text-primary">24</div>
  </div>
</div>
```

---

## 弹窗 (Modal)

### HTML Dialog Modal
```html
<dialog id="my_modal_1" class="modal">
  <div class="modal-box">
    <form method="dialog"><button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button></form>
    <h3 class="font-bold text-lg">标题</h3>
    <div class="modal-action">
      <form method="dialog"><button class="btn">取消</button></form>
      <button class="btn btn-primary">确认</button>
    </div>
  </div>
</dialog>
```

---

## 其他常用组件

### Join (搜索/分页)
```html
<div class="join">
  <input class="input input-bordered join-item" placeholder="搜索..." />
  <button class="btn join-item"><i class="ri-search-line"></i></button>
</div>
```

### Indicator (通知徽章)
```html
<div class="indicator">
  <i class="ri-notification-line text-xl"></i>
  <span class="badge badge-sm badge-error indicator-item">3</span>
</div>
```

### Avatar
```html
<div class="avatar placeholder">
  <div class="bg-primary text-primary-content rounded-full w-10">
    <span class="text-sm font-bold">C</span>
  </div>
</div>
```
