/**
 * Billing Pages Common JavaScript
 * 公共账单页面 JavaScript 文件
 * 包含主题切换、Chart.js 加载、分页等通用功能
 */

// ==================== Theme Management ====================

/**
 * Initialize theme system
 * 初始化主题系统
 */
function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;

    // Get saved theme or default to light
    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', savedTheme);

    if (themeToggle) {
        themeToggle.checked = savedTheme === 'dark';
        themeToggle.addEventListener('change', function() {
            const newTheme = this.checked ? 'dark' : 'light';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);

            // Update chart colors if charts exist
            if (window.updateChartsTheme) {
                window.updateChartsTheme(newTheme);
            }
        });
    }
}

// ==================== Chart.js Management ====================

/**
 * Load Chart.js from CDN with fallback
 * 从 CDN 加载 Chart.js，带失败重试
 */
function loadChartJS() {
    return new Promise((resolve, reject) => {
        if (typeof Chart !== 'undefined') {
            resolve();
            return;
        }

        const script = document.createElement('script');
        script.src = 'https://cdn.bootcdn.net/ajax/libs/Chart.js/4.4.1/chart.umd.min.js';

        script.onload = () => {
            if (typeof Chart !== 'undefined') {
                console.log('Chart.js loaded successfully from BootCDN');
                resolve();
            } else {
                loadFallbackChartJS().then(resolve).catch(reject);
            }
        };

        script.onerror = () => {
            console.warn('BootCDN failed, trying unpkg...');
            loadFallbackChartJS().then(resolve).catch(reject);
        };

        document.head.appendChild(script);
    });
}

/**
 * Load Chart.js from fallback CDN
 * 从备用 CDN 加载 Chart.js
 */
function loadFallbackChartJS() {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/chart.js@4.4.1/dist/chart.umd.min.js';

        script.onload = () => {
            if (typeof Chart !== 'undefined') {
                console.log('Chart.js loaded successfully from unpkg');
                resolve();
            } else {
                console.warn('unpkg failed, trying jsdelivr...');
                loadFinalFallbackChartJS().then(resolve).catch(reject);
            }
        };

        script.onerror = () => {
            loadFinalFallbackChartJS().then(resolve).catch(reject);
        };

        document.head.appendChild(script);
    });
}

/**
 * Load Chart.js from final fallback CDN
 * 从最后备用 CDN 加载 Chart.js
 */
function loadFinalFallbackChartJS() {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js';

        script.onload = () => {
            if (typeof Chart !== 'undefined') {
                console.log('Chart.js loaded successfully from jsDelivr');
                resolve();
            } else {
                console.error('All Chart.js CDNs failed');
                reject(new Error('Failed to load Chart.js from all CDNs'));
            }
        };

        script.onerror = () => {
            console.error('All Chart.js CDNs failed');
            reject(new Error('Failed to load Chart.js from all CDNs'));
        };

        document.head.appendChild(script);
    });
}

// ==================== Pagination Management ====================

/**
 * Pagination class for table data
 * 表格数据分页类
 */
class Pagination {
    constructor(options) {
        this.data = options.data || [];
        this.pageSize = options.pageSize || 10;
        this.currentPage = 1;
        this.tableBodyId = options.tableBodyId;
        this.paginationStartId = options.paginationStartId || 'paginationStart';
        this.paginationEndId = options.paginationEndId || 'paginationEnd';
        this.paginationTotalId = options.paginationTotalId || 'paginationTotal';
        this.pageNumbersId = options.pageNumbersId || 'pageNumbers';
        this.firstPageBtnId = options.firstPageBtnId || 'firstPageBtn';
        this.prevPageBtnId = options.prevPageBtnId || 'prevPageBtn';
        this.nextPageBtnId = options.nextPageBtnId || 'nextPageBtn';
        this.lastPageBtnId = options.lastPageBtnId || 'lastPageBtn';
        this.renderRow = options.renderRow || this.defaultRenderRow;

        this.init();
    }

    init() {
        this.bindEvents();
        this.render();
    }

    defaultRenderRow(item) {
        const row = document.createElement('tr');
        row.className = 'hover:bg-base-200/50 transition-colors';
        row.innerHTML = `<td colspan="5">${JSON.stringify(item)}</td>`;
        return row;
    }

    bindEvents() {
        const firstBtn = document.getElementById(this.firstPageBtnId);
        const prevBtn = document.getElementById(this.prevPageBtnId);
        const nextBtn = document.getElementById(this.nextPageBtnId);
        const lastBtn = document.getElementById(this.lastPageBtnId);

        if (firstBtn) firstBtn.addEventListener('click', () => this.goToFirstPage());
        if (prevBtn) prevBtn.addEventListener('click', () => this.goToPrevPage());
        if (nextBtn) nextBtn.addEventListener('click', () => this.goToNextPage());
        if (lastBtn) lastBtn.addEventListener('click', () => this.goToLastPage());
    }

    goToPage(page) {
        const totalPages = Math.ceil(this.data.length / this.pageSize);
        if (page < 1 || page > totalPages) return;

        this.currentPage = page;
        this.render();
    }

    goToFirstPage() {
        this.goToPage(1);
    }

    goToPrevPage() {
        this.goToPage(this.currentPage - 1);
    }

    goToNextPage() {
        this.goToPage(this.currentPage + 1);
    }

    goToLastPage() {
        const totalPages = Math.ceil(this.data.length / this.pageSize);
        this.goToPage(totalPages);
    }

    changePageSize(size) {
        this.pageSize = parseInt(size);
        this.currentPage = 1;
        this.render();
    }

    render() {
        const tableBody = document.getElementById(this.tableBodyId);
        if (!tableBody) return;

        const start = (this.currentPage - 1) * this.pageSize;
        const end = start + this.pageSize;
        const pageData = this.data.slice(start, end);

        tableBody.innerHTML = '';
        pageData.forEach(item => {
            tableBody.appendChild(this.renderRow(item));
        });

        this.updatePaginationInfo();
        this.updatePageNumbers();
    }

    updatePaginationInfo() {
        const start = (this.currentPage - 1) * this.pageSize + 1;
        const end = Math.min(this.currentPage * this.pageSize, this.data.length);

        document.getElementById(this.paginationStartId).textContent = start;
        document.getElementById(this.paginationEndId).textContent = end;
        document.getElementById(this.paginationTotalId).textContent = this.data.length;
    }

    updatePageNumbers() {
        const totalPages = Math.ceil(this.data.length / this.pageSize);
        const pageNumbers = document.getElementById(this.pageNumbersId);
        if (!pageNumbers) return;

        pageNumbers.innerHTML = '';

        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        for (let i = startPage; i <= endPage; i++) {
            const btn = document.createElement('button');
            btn.className = `join-item btn btn-sm ${i === this.currentPage ? 'btn-active' : ''}`;
            btn.textContent = i;
            btn.addEventListener('click', () => this.goToPage(i));
            pageNumbers.appendChild(btn);
        }

        // Update navigation buttons
        const firstBtn = document.getElementById(this.firstPageBtnId);
        const prevBtn = document.getElementById(this.prevPageBtnId);
        const nextBtn = document.getElementById(this.nextPageBtnId);
        const lastBtn = document.getElementById(this.lastPageBtnId);

        if (firstBtn) firstBtn.disabled = this.currentPage === 1;
        if (prevBtn) prevBtn.disabled = this.currentPage === 1;
        if (nextBtn) nextBtn.disabled = this.currentPage === totalPages;
        if (lastBtn) lastBtn.disabled = this.currentPage === totalPages;
    }

    setData(newData) {
        this.data = newData;
        this.currentPage = 1;
        this.render();
    }
}

// ==================== Date Utilities ====================

/**
 * Format date to string
 * 格式化日期
 */
function formatDate(date, format = 'MM-DD HH:mm') {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');

    return format
        .replace('YYYY', year)
        .replace('MM', month)
        .replace('DD', day)
        .replace('HH', hours)
        .replace('mm', minutes);
}

/**
 * Get date range by preset
 * 根据预设获取日期范围
 */
function getDateRange(preset) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    switch (preset) {
        case 'today':
            return {
                start: today,
                end: new Date(today.getTime() + 24 * 60 * 60 * 1000)
            };
        case 'week':
            const weekStart = new Date(today);
            weekStart.setDate(today.getDate() - today.getDay());
            return { start: weekStart, end: now };
        case 'month':
            const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
            return { start: monthStart, end: now };
        case 'year':
            const yearStart = new Date(now.getFullYear(), 0, 1);
            return { start: yearStart, end: now };
        case '7days':
            return {
                start: new Date(today.getTime() - 6 * 24 * 60 * 60 * 1000),
                end: now
            };
        case '30days':
            return {
                start: new Date(today.getTime() - 29 * 24 * 60 * 60 * 1000),
                end: now
            };
        case '90days':
            return {
                start: new Date(today.getTime() - 89 * 24 * 60 * 60 * 1000),
                end: now
            };
        case '6months':
            const sixMonthsAgo = new Date(now);
            sixMonthsAgo.setMonth(now.getMonth() - 6);
            return { start: sixMonthsAgo, end: now };
        case '1year':
            const oneYearAgo = new Date(now);
            oneYearAgo.setFullYear(now.getFullYear() - 1);
            return { start: oneYearAgo, end: now };
        default:
            return { start: today, end: now };
    }
}

// ==================== Chart Utilities ====================

/**
 * Get chart colors based on theme
 * 根据主题获取图表颜色
 */
function getChartColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

    return {
        text: isDark ? '#e2e8f0' : '#1e293b',
        grid: isDark ? '#334155' : '#e2e8f0',
        background: isDark ? '#1e293b' : '#ffffff'
    };
}

/**
 * Create common chart options
 * 创建通用图表选项
 */
function createChartOptions(options = {}) {
    const colors = getChartColors();

    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: colors.text,
                    font: {
                        family: "'Inter', sans-serif"
                    }
                }
            },
            tooltip: {
                backgroundColor: colors.background,
                titleColor: colors.text,
                bodyColor: colors.text,
                borderColor: colors.grid,
                borderWidth: 1,
                padding: 12,
                displayColors: true,
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += context.parsed.y.toLocaleString();
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: colors.text,
                    font: {
                        family: "'Inter', sans-serif"
                    }
                },
                grid: {
                    color: colors.grid
                }
            },
            y: {
                ticks: {
                    color: colors.text,
                    font: {
                        family: "'Inter', sans-serif"
                    }
                },
                grid: {
                    color: colors.grid
                }
            }
        },
        ...options
    };
}

// ==================== Sidebar Management ====================

/**
 * Initialize sidebar collapse functionality
 * 初始化侧边栏收起功能
 */
function initSidebar() {
    const collapseBtn = document.getElementById('sidebarCollapseBtn');
    const collapseIcon = document.getElementById('collapseIcon');
    const sidebar = document.querySelector('.sidebar');

    if (!collapseBtn || !sidebar) return;

    // Load saved state
    const savedState = localStorage.getItem('sidebarCollapsed');
    if (savedState === 'true') {
        sidebar.classList.add('collapsed');
        if (collapseIcon) {
            collapseIcon.classList.remove('ri-menu-fold-line');
            collapseIcon.classList.add('ri-menu-unfold-line');
        }
    }

    // Load saved width
    const savedWidth = localStorage.getItem('sidebarWidth');
    if (savedWidth && !sidebar.classList.contains('collapsed')) {
        sidebar.style.width = savedWidth + 'px';
    }

    // Toggle sidebar
    collapseBtn.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        const isCollapsed = sidebar.classList.contains('collapsed');

        // Update icon
        if (collapseIcon) {
            if (isCollapsed) {
                collapseIcon.classList.remove('ri-menu-fold-line');
                collapseIcon.classList.add('ri-menu-unfold-line');
            } else {
                collapseIcon.classList.remove('ri-menu-unfold-line');
                collapseIcon.classList.add('ri-menu-fold-line');
                // Restore width when expanding
                const savedWidth = localStorage.getItem('sidebarWidth');
                if (savedWidth) {
                    sidebar.style.width = savedWidth + 'px';
                }
            }
        }

        // Save state
        localStorage.setItem('sidebarCollapsed', isCollapsed);

        // Trigger custom event for other components to listen
        window.dispatchEvent(new CustomEvent('sidebarToggled', { detail: { isCollapsed } }));
    });

    // Initialize resize functionality
    initSidebarResize(sidebar);
}

/**
 * Initialize sidebar resize functionality
 * 初始化侧边栏拖动调节功能
 */
function initSidebarResize(sidebar) {
    const resizeHandle = document.getElementById('sidebarResizeHandle');
    if (!resizeHandle || !sidebar) return;

    let isResizing = false;
    let startX = 0;
    let startWidth = 0;

    resizeHandle.addEventListener('mousedown', function(e) {
        isResizing = true;
        startX = e.clientX;
        startWidth = sidebar.offsetWidth;

        sidebar.classList.add('resizing');
        resizeHandle.classList.add('active');

        // Prevent text selection during resize
        document.body.style.userSelect = 'none';
        document.body.style.cursor = 'col-resize';

        e.preventDefault();
    });

    document.addEventListener('mousemove', function(e) {
        if (!isResizing) return;

        const diff = e.clientX - startX;
        let newWidth = startWidth + diff;

        // Enforce min and max width
        const minWidth = 180;
        const maxWidth = 400;
        newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));

        sidebar.style.width = newWidth + 'px';

        // Trigger resize event for other components
        window.dispatchEvent(new CustomEvent('sidebarResize', {
            detail: { width: newWidth }
        }));
    });

    document.addEventListener('mouseup', function(e) {
        if (!isResizing) return;

        isResizing = false;
        sidebar.classList.remove('resizing');
        resizeHandle.classList.remove('active');

        // Restore cursor
        document.body.style.userSelect = '';
        document.body.style.cursor = '';

        // Save width to localStorage
        const finalWidth = sidebar.offsetWidth;
        localStorage.setItem('sidebarWidth', finalWidth);

        // Trigger resize complete event
        window.dispatchEvent(new CustomEvent('sidebarResizeComplete', {
            detail: { width: finalWidth }
        }));
    });

    // Touch support for mobile devices
    resizeHandle.addEventListener('touchstart', function(e) {
        const touch = e.touches[0];
        isResizing = true;
        startX = touch.clientX;
        startWidth = sidebar.offsetWidth;

        sidebar.classList.add('resizing');
        resizeHandle.classList.add('active');

        document.body.style.userSelect = 'none';

        e.preventDefault();
    });

    document.addEventListener('touchmove', function(e) {
        if (!isResizing) return;

        const touch = e.touches[0];
        const diff = touch.clientX - startX;
        let newWidth = startWidth + diff;

        const minWidth = 180;
        const maxWidth = 400;
        newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));

        sidebar.style.width = newWidth + 'px';

        window.dispatchEvent(new CustomEvent('sidebarResize', {
            detail: { width: newWidth }
        }));
    });

    document.addEventListener('touchend', function(e) {
        if (!isResizing) return;

        isResizing = false;
        sidebar.classList.remove('resizing');
        resizeHandle.classList.remove('active');

        document.body.style.userSelect = '';

        const finalWidth = sidebar.offsetWidth;
        localStorage.setItem('sidebarWidth', finalWidth);

        window.dispatchEvent(new CustomEvent('sidebarResizeComplete', {
            detail: { width: finalWidth }
        }));
    });
}

// ==================== Initialize ====================

/**
 * Initialize common functionality when DOM is ready
 * DOM 加载完成后初始化公共功能
 */
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    initSidebar();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        Pagination,
        formatDate,
        getDateRange,
        getChartColors,
        createChartOptions,
        loadChartJS
    };
}
