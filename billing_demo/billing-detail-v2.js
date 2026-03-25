// ===================================
// Project Billing Detail V2 - Tailwind + DaisyUI
// ===================================

// Pagination state
let currentPage = 1;
let pageSize = 10;
let filteredRecords = [];

// Mock Data
const mockProjectData = {
    memberBreakdown: [
        { name: 'Alice', points: 45000, percentage: 52.9, color: '#4f46e5' },
        { name: 'Bob', points: 25000, percentage: 29.4, color: '#10b981' },
        { name: 'Charlie', points: 10000, percentage: 11.8, color: '#f59e0b' },
        { name: '其他', points: 5000, percentage: 5.9, color: '#64748b' }
    ],
    modelBreakdown: [
        { name: 'Seedream 4.5', points: 40000, percentage: 47.1, color: '#4f46e5' },
        { name: 'Seedance 1.5', points: 25000, percentage: 29.4, color: '#10b981' },
        { name: '豆包 TTS', points: 15000, percentage: 17.6, color: '#f59e0b' },
        { name: 'Sora2', points: 5000, percentage: 5.9, color: '#64748b' }
    ],
    detailRecords: [
        { time: '12-31 09:42', member: 'Alice', model: 'Seedream 4.5 - 音频', points: 250 },
        { time: '12-31 09:15', member: 'Alice', model: '豆包 TTS', points: 135 },
        { time: '12-31 08:50', member: 'Bob', model: 'Sora2 视频', points: 500 },
        { time: '12-30 16:30', member: 'Charlie', model: 'Seedance 1.5 - 4K', points: 120 },
        { time: '12-30 14:20', member: 'Alice', model: 'Seedream 4.5 - 无声', points: 150 },
        { time: '12-30 11:45', member: 'Bob', model: 'Seedream 4.5 - 音频', points: 280 },
        { time: '12-30 10:20', member: 'Charlie', model: '豆包 TTS', points: 95 },
        { time: '12-29 15:30', member: 'Alice', model: 'Sora2 视频', points: 500 },
        { time: '12-29 14:15', member: 'Bob', model: 'Seedance 1.5 - 4K', points: 120 },
        { time: '12-29 13:00', member: 'Charlie', model: 'Seedream 4.5 - 无声', points: 150 },
        { time: '12-29 11:30', member: 'Alice', model: 'Seedream 4.5 - 音频', points: 250 },
        { time: '12-29 10:15', member: 'Bob', model: '豆包 TTS', points: 135 },
        { time: '12-28 16:45', member: 'Charlie', model: 'Sora2 视频', points: 500 },
        { time: '12-28 15:20', member: 'Alice', model: 'Seedance 1.5 - 4K', points: 120 },
        { time: '12-28 14:00', member: 'Bob', model: 'Seedream 4.5 - 无声', points: 150 }
    ]
};

// Wait for Chart.js to be loaded
function waitForChart() {
    return new Promise((resolve) => {
        if (typeof Chart !== 'undefined') {
            resolve();
        } else {
            const checkInterval = setInterval(() => {
                if (typeof Chart !== 'undefined') {
                    clearInterval(checkInterval);
                    resolve();
                }
            }, 100);
            // Timeout after 5 seconds
            setTimeout(() => {
                clearInterval(checkInterval);
                console.warn('Chart.js failed to load after 5 seconds');
                resolve();
            }, 5000);
        }
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM Content Loaded');

    // Initialize member list immediately
    initMemberList();

    // Wait for Chart.js before initializing model chart
    await waitForChart();

    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded. Model chart will not be displayed.');
        showModelChartFallback();
    } else {
        console.log('Chart.js loaded successfully');
        initModelChart();
    }

    // Initialize filters and pagination
    initFilters();
    initPagination();

    // Initial data load
    filterRecords();

    initThemeToggle();
});

// Show fallback when Chart.js fails to load
function showModelChartFallback() {
    const ctx = document.getElementById('modelChart');
    if (ctx) {
        ctx.parentElement.innerHTML = `
            <div class="alert alert-warning">
                <i class="ri-error-warning-line text-xl"></i>
                <div>
                    <h4 class="font-bold">图表加载失败</h4>
                    <p class="text-xs">Chart.js 未能加载，请检查网络连接或刷新页面重试</p>
                </div>
            </div>
        `;
    }
}

// Member Distribution List
function initMemberList() {
    const container = document.getElementById('memberList');
    if (!container) return;

    container.innerHTML = mockProjectData.memberBreakdown.map((member, index) => `
        <div class="flex items-center justify-between p-2 rounded-lg hover:bg-base-200 transition-colors">
            <div class="flex items-center gap-2">
                <div class="badge ${index < 3 ? 'badge-primary' : 'badge-ghost'} text-xs">${index + 1}</div>
                <div class="avatar placeholder">
                    <div class="bg-gradient-to-br from-brand-500 to-purple-600 text-white rounded-full w-6">
                        <span class="text-xs">${member.name.charAt(0)}</span>
                    </div>
                </div>
                <span class="font-medium text-sm">${member.name}</span>
            </div>
            <div class="text-right">
                <div class="font-bold text-brand-600 text-sm">${member.points.toLocaleString()} 积分</div>
                <div class="text-xs text-base-content/60">${member.percentage.toFixed(1)}%</div>
            </div>
        </div>
    `).join('');
}

// Model Distribution Chart (Pie Chart)
function initModelChart() {
    const ctx = document.getElementById('modelChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: mockProjectData.modelBreakdown.map(m => m.name),
            datasets: [{
                data: mockProjectData.modelBreakdown.map(m => m.points),
                backgroundColor: mockProjectData.modelBreakdown.map(m => m.color),
                borderWidth: 2,
                borderColor: '#fff',
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#64748b',
                        padding: 15,
                        font: { size: 13 }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 30, 40, 0.95)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(99, 102, 241, 0.5)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                    callbacks: {
                        label: (context) => {
                            const label = context.label || '';
                            const value = context.parsed;
                            const percentage = mockProjectData.modelBreakdown[context.dataIndex].percentage;
                            return `${label}: ${value.toLocaleString()} 积分 (${percentage.toFixed(1)}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Filters
function initFilters() {
    const memberFilter = document.getElementById('memberFilter');
    const modelFilter = document.getElementById('modelFilter');

    if (memberFilter) {
        memberFilter.addEventListener('change', () => {
            currentPage = 1; // Reset to first page when filtering
            filterRecords();
        });
    }
    if (modelFilter) {
        modelFilter.addEventListener('change', () => {
            currentPage = 1; // Reset to first page when filtering
            filterRecords();
        });
    }
}

function filterRecords() {
    const memberFilter = document.getElementById('memberFilter').value;
    const modelFilter = document.getElementById('modelFilter').value;

    filteredRecords = [...mockProjectData.detailRecords];

    if (memberFilter !== 'all') {
        filteredRecords = filteredRecords.filter(r => r.member === memberFilter);
    }

    if (modelFilter !== 'all') {
        filteredRecords = filteredRecords.filter(r => {
            if (modelFilter === 'seedream') return r.model.includes('Seedream');
            if (modelFilter === 'seedance') return r.model.includes('Seedance');
            if (modelFilter === 'doubao') return r.model.includes('豆包');
            return true;
        });
    }

    updateTable();
    updatePagination();
}

// Update table with paginated data
function updateTable() {
    const tbody = document.getElementById('detailTableBody');
    if (!tbody) return;

    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const paginatedData = filteredRecords.slice(start, end);

    tbody.innerHTML = paginatedData.map(record => `
        <tr class="hover:bg-base-200/50 transition-colors">
            <td class="text-sm">${record.time}</td>
            <td>${record.member}</td>
            <td>${record.model}</td>
            <td class="font-bold text-brand-600">${record.points.toLocaleString()} 积分</td>
        </tr>
    `).join('');
}

// Pagination
function initPagination() {
    const pageSizeSelect = document.getElementById('pageSizeSelect');
    const firstPageBtn = document.getElementById('firstPageBtn');
    const prevPageBtn = document.getElementById('prevPageBtn');
    const nextPageBtn = document.getElementById('nextPageBtn');
    const lastPageBtn = document.getElementById('lastPageBtn');

    // Page size change handler
    if (pageSizeSelect) {
        pageSizeSelect.addEventListener('change', function() {
            pageSize = parseInt(this.value);
            currentPage = 1; // Reset to first page when changing page size
            updateTable();
            updatePagination();
        });
    }

    // Navigation button handlers
    if (firstPageBtn) {
        firstPageBtn.addEventListener('click', () => goToPage(1));
    }
    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', () => goToPage(currentPage - 1));
    }
    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', () => goToPage(currentPage + 1));
    }
    if (lastPageBtn) {
        lastPageBtn.addEventListener('click', () => goToPage(getTotalPages()));
    }

    // Page number buttons
    for (let i = 1; i <= 3; i++) {
        const pageBtn = document.getElementById(`page${i}Btn`);
        if (pageBtn) {
            pageBtn.addEventListener('click', () => goToPage(i));
        }
    }
}

function goToPage(page) {
    const totalPages = getTotalPages();
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    updateTable();
    updatePagination();
}

function getTotalPages() {
    return Math.ceil(filteredRecords.length / pageSize);
}

function updatePagination() {
    const totalPages = getTotalPages();
    const start = (currentPage - 1) * pageSize + 1;
    const end = Math.min(currentPage * pageSize, filteredRecords.length);

    // Update record count display
    document.getElementById('paginationStart').textContent = filteredRecords.length > 0 ? start : 0;
    document.getElementById('paginationEnd').textContent = end;
    document.getElementById('paginationTotal').textContent = filteredRecords.length;

    // Update navigation buttons
    const firstPageBtn = document.getElementById('firstPageBtn');
    const prevPageBtn = document.getElementById('prevPageBtn');
    const nextPageBtn = document.getElementById('nextPageBtn');
    const lastPageBtn = document.getElementById('lastPageBtn');

    if (firstPageBtn) firstPageBtn.disabled = currentPage === 1;
    if (prevPageBtn) prevPageBtn.disabled = currentPage === 1;
    if (nextPageBtn) nextPageBtn.disabled = currentPage === totalPages;
    if (lastPageBtn) lastPageBtn.disabled = currentPage === totalPages;

    // Update page number buttons
    for (let i = 1; i <= 3; i++) {
        const pageBtn = document.getElementById(`page${i}Btn`);
        if (pageBtn) {
            if (i <= totalPages) {
                pageBtn.style.display = 'block';
                pageBtn.textContent = i;
                if (i === currentPage) {
                    pageBtn.classList.add('btn-active');
                } else {
                    pageBtn.classList.remove('btn-active');
                }
            } else {
                pageBtn.style.display = 'none';
            }
        }
    }
}

// Theme Toggle
function initThemeToggle() {
    const toggle = document.getElementById('theme-toggle');
    const html = document.documentElement;

    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', savedTheme);
    toggle.checked = savedTheme === 'dark';

    toggle.addEventListener('change', function() {
        const theme = this.checked ? 'dark' : 'light';
        html.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    });
}
