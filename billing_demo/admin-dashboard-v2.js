// ===================================
// Admin Dashboard V2 - Tailwind + DaisyUI
// ===================================

// Mock Data
const mockAdminData = {
    trendData: {
        '7days': {
            labels: ['01-03', '01-04', '01-05', '01-06', '01-07', '01-08', '01-09'],
            revenue: [1650000, 1680000, 1720000, 1750000, 1780000, 1820000, 1850000],
            cost: [490000, 500000, 510000, 520000, 530000, 540000, 550000],
            profit: [1160000, 1180000, 1210000, 1230000, 1250000, 1280000, 1300000]
        },
        '30days': {
            labels: ['12-11', '12-15', '12-19', '12-23', '12-27', '12-31', '01-04', '01-08'],
            revenue: [1150000, 1180000, 1200000, 1220000, 1250000, 1650000, 1780000, 1850000],
            cost: [340000, 345000, 350000, 360000, 375000, 490000, 530000, 550000],
            profit: [810000, 835000, 850000, 860000, 875000, 1160000, 1250000, 1300000]
        },
        '90days': {
            labels: ['10-15', '10-29', '11-12', '11-26', '12-10', '12-24', '01-07'],
            revenue: [750000, 920000, 1050000, 1150000, 1200000, 1550000, 1780000],
            cost: [220000, 270000, 300000, 340000, 355000, 480000, 530000],
            profit: [530000, 650000, 750000, 810000, 845000, 1070000, 1250000]
        },
        '6months': {
            labels: ['8月', '9月', '10月', '11月', '12月', '1月'],
            revenue: [520000, 680000, 850000, 1150000, 1480000, 1780000],
            cost: [150000, 195000, 245000, 340000, 445000, 530000],
            profit: [370000, 485000, 605000, 810000, 1035000, 1250000]
        },
        '1year': {
            labels: ['2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月', '1月'],
            revenue: [280000, 320000, 350000, 410000, 450000, 480000, 520000, 680000, 850000, 1150000, 1480000, 1780000],
            cost: [80000, 92000, 100000, 118000, 130000, 140000, 150000, 195000, 245000, 340000, 445000, 530000],
            profit: [200000, 228000, 250000, 292000, 320000, 340000, 370000, 485000, 605000, 810000, 1035000, 1250000]
        }
    },
    modelDistributionData: {
        '7days': [
            { name: 'Seedream 4.5', value: 4200000, percentage: 49.4, color: '#6366f1' },
            { name: 'Seedance 1.5', value: 2500000, percentage: 29.4, color: '#8b5cf6' },
            { name: '豆包 TTS', value: 1200000, percentage: 14.1, color: '#a855f7' },
            { name: 'Sora2', value: 600000, percentage: 7.1, color: '#4f46e5' }
        ],
        '30days': [
            { name: 'Seedream 4.5', value: 18500000, percentage: 52.1, color: '#6366f1' },
            { name: 'Seedance 1.5', value: 9800000, percentage: 27.6, color: '#8b5cf6' },
            { name: '豆包 TTS', value: 4800000, percentage: 13.5, color: '#a855f7' },
            { name: 'Sora2', value: 2400000, percentage: 6.8, color: '#4f46e5' }
        ],
        '90days': [
            { name: 'Seedream 4.5', value: 58000000, percentage: 51.5, color: '#6366f1' },
            { name: 'Seedance 1.5', value: 32000000, percentage: 28.4, color: '#8b5cf6' },
            { name: '豆包 TTS', value: 15500000, percentage: 13.8, color: '#a855f7' },
            { name: 'Sora2', value: 7000000, percentage: 6.3, color: '#4f46e5' }
        ],
        '6months': [
            { name: 'Seedream 4.5', value: 125000000, percentage: 50.8, color: '#6366f1' },
            { name: 'Seedance 1.5', value: 72000000, percentage: 29.3, color: '#8b5cf6' },
            { name: '豆包 TTS', value: 35000000, percentage: 14.2, color: '#a855f7' },
            { name: 'Sora2', value: 14000000, percentage: 5.7, color: '#4f46e5' }
        ],
        '1year': [
            { name: 'Seedream 4.5', value: 285000000, percentage: 50.2, color: '#6366f1' },
            { name: 'Seedance 1.5', value: 168000000, percentage: 29.6, color: '#8b5cf6' },
            { name: '豆包 TTS', value: 78000000, percentage: 13.7, color: '#a855f7' },
            { name: 'Sora2', value: 36000000, percentage: 6.5, color: '#4f46e5' }
        ]
    },
    organizationData: {
        'today': Array.from({ length: 25 }, (_, i) => ({
            rank: i + 1,
            name: `企业${String.fromCharCode(65 + i)}`,
            projects: Math.floor(Math.random() * 50) + 5,
            userCount: Math.floor(Math.random() * 200) + 10,
            points: Math.floor(Math.random() * 500000) + 100000,
            amount: Math.floor(Math.random() * 50000) + 10000,
            recharge: Math.floor(Math.random() * 1000000) + 500000,
            balance: Math.floor(Math.random() * 2000000) + 500000,
            avatarColor: ['bg-brand-500', 'bg-purple-500', 'bg-green-500', 'bg-orange-500', 'bg-pink-500'][i % 5],
            avatarText: ['企', '科', '教', '媒', '游'][i % 5]
        })),
        'week': Array.from({ length: 35 }, (_, i) => ({
            rank: i + 1,
            name: `企业${String.fromCharCode(65 + i)}`,
            projects: Math.floor(Math.random() * 50) + 5,
            userCount: Math.floor(Math.random() * 200) + 10,
            points: Math.floor(Math.random() * 3000000) + 500000,
            amount: Math.floor(Math.random() * 300000) + 50000,
            recharge: Math.floor(Math.random() * 2000000) + 1000000,
            balance: Math.floor(Math.random() * 5000000) + 1000000,
            avatarColor: ['bg-brand-500', 'bg-purple-500', 'bg-green-500', 'bg-orange-500', 'bg-pink-500'][i % 5],
            avatarText: ['企', '科', '教', '媒', '游'][i % 5]
        })),
        'month': Array.from({ length: 50 }, (_, i) => ({
            rank: i + 1,
            name: `企业${String.fromCharCode(65 + i)}`,
            projects: Math.floor(Math.random() * 50) + 5,
            userCount: Math.floor(Math.random() * 200) + 10,
            points: Math.floor(Math.random() * 10000000) + 1000000,
            amount: Math.floor(Math.random() * 1000000) + 100000,
            recharge: Math.floor(Math.random() * 5000000) + 2000000,
            balance: Math.floor(Math.random() * 10000000) + 2000000,
            avatarColor: ['bg-brand-500', 'bg-purple-500', 'bg-green-500', 'bg-orange-500', 'bg-pink-500'][i % 5],
            avatarText: ['企', '科', '教', '媒', '游'][i % 5]
        })),
        'quarter': Array.from({ length: 50 }, (_, i) => ({
            rank: i + 1,
            name: `企业${String.fromCharCode(65 + i)}`,
            projects: Math.floor(Math.random() * 50) + 5,
            userCount: Math.floor(Math.random() * 200) + 10,
            points: Math.floor(Math.random() * 30000000) + 3000000,
            amount: Math.floor(Math.random() * 3000000) + 300000,
            recharge: Math.floor(Math.random() * 10000000) + 5000000,
            balance: Math.floor(Math.random() * 20000000) + 5000000,
            avatarColor: ['bg-brand-500', 'bg-purple-500', 'bg-green-500', 'bg-orange-500', 'bg-pink-500'][i % 5],
            avatarText: ['企', '科', '教', '媒', '游'][i % 5]
        })),
        'year': Array.from({ length: 50 }, (_, i) => ({
            rank: i + 1,
            name: `企业${String.fromCharCode(65 + i)}`,
            projects: Math.floor(Math.random() * 50) + 5,
            userCount: Math.floor(Math.random() * 200) + 10,
            points: Math.floor(Math.random() * 100000000) + 10000000,
            amount: Math.floor(Math.random() * 10000000) + 1000000,
            recharge: Math.floor(Math.random() * 30000000) + 10000000,
            balance: Math.floor(Math.random() * 50000000) + 10000000,
            avatarColor: ['bg-brand-500', 'bg-purple-500', 'bg-green-500', 'bg-orange-500', 'bg-pink-500'][i % 5],
            avatarText: ['企', '科', '教', '媒', '游'][i % 5]
        }))
    }
};

// Global chart instance
let trendChartInstance = null;
let modelChartInstance = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTrendChart();
    initModelChart();
    initThemeToggle();
    initOrgTable();
});

// Initialize organization table with pagination
function initOrgTable() {
    updateOrgTable('month', '本月');
}

// Organization Pagination Class
class OrgPagination {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 10;
        this.totalItems = 0;
        this.currentData = [];
        this.currentRange = 'month';
    }

    setData(data) {
        this.currentData = data;
        this.totalItems = data.length;
        this.currentPage = 1;
        this.updateTable();
        this.updatePagination();
    }

    updateTable() {
        const start = (this.currentPage - 1) * this.pageSize;
        const end = start + this.pageSize;
        const pageData = this.currentData.slice(start, end);

        const tbody = document.getElementById('orgTableBody');
        if (!tbody) return;

        tbody.innerHTML = pageData.map(org => {
            const badgeClass = org.rank <= 3 ?
                (org.rank === 1 ? 'badge-primary' : org.rank === 2 ? 'badge-secondary' : 'badge-accent') :
                'badge-ghost';

            return `
                <tr class="hover:bg-base-200/50 transition-colors">
                    <td>
                        <div class="badge badge-lg ${badgeClass}">${org.rank}</div>
                    </td>
                    <td>
                        <div class="flex items-center gap-3">
                            <div class="avatar placeholder">
                                <div class="${org.avatarColor} text-white rounded-full w-10">
                                    <span class="text-xs font-bold">${org.avatarText}</span>
                                </div>
                            </div>
                            <div>
                                <div class="font-bold">${org.name}</div>
                            </div>
                        </div>
                    </td>
                    <td>${org.userCount}</td>
                    <td class="font-bold">${org.points.toLocaleString()}</td>
                    <td class="font-bold text-brand-600">¥${org.amount.toLocaleString()}</td>
                    <td class="font-bold text-success">${org.recharge.toLocaleString()}</td>
                    <td class="font-bold">${org.balance.toLocaleString()}</td>
                </tr>
            `;
        }).join('');
    }

    updatePagination() {
        const totalPages = Math.ceil(this.totalItems / this.pageSize);
        const start = (this.currentPage - 1) * this.pageSize + 1;
        const end = Math.min(this.currentPage * this.pageSize, this.totalItems);

        // Update info text
        document.getElementById('orgPaginationStart').textContent = start;
        document.getElementById('orgPaginationEnd').textContent = end;
        document.getElementById('orgPaginationTotal').textContent = this.totalItems;

        // Update page numbers
        const pageNumbersContainer = document.getElementById('orgPageNumbers');
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        let pageNumbersHTML = '';
        for (let i = startPage; i <= endPage; i++) {
            pageNumbersHTML += `<button class="join-item btn btn-sm ${i === this.currentPage ? 'btn-active' : ''}" onclick="orgPagination.goToPage(${i})">${i}</button>`;
        }
        pageNumbersContainer.innerHTML = pageNumbersHTML;

        // Update navigation buttons
        document.getElementById('orgFirstPageBtn').disabled = this.currentPage === 1;
        document.getElementById('orgPrevPageBtn').disabled = this.currentPage === 1;
        document.getElementById('orgNextPageBtn').disabled = this.currentPage === totalPages;
        document.getElementById('orgLastPageBtn').disabled = this.currentPage === totalPages;
    }

    goToPage(page) {
        this.currentPage = page;
        this.updateTable();
        this.updatePagination();
    }

    goToFirstPage() {
        this.goToPage(1);
    }

    goToPrevPage() {
        if (this.currentPage > 1) {
            this.goToPage(this.currentPage - 1);
        }
    }

    goToNextPage() {
        const totalPages = Math.ceil(this.totalItems / this.pageSize);
        if (this.currentPage < totalPages) {
            this.goToPage(this.currentPage + 1);
        }
    }

    goToLastPage() {
        const totalPages = Math.ceil(this.totalItems / this.pageSize);
        this.goToPage(totalPages);
    }

    changePageSize(size) {
        this.pageSize = parseInt(size);
        this.currentPage = 1;
        this.updateTable();
        this.updatePagination();
    }
}

// Create global pagination instance
const orgPagination = new OrgPagination();

// Revenue/Cost/Profit Trend Chart
function initTrendChart() {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;

    const revenueGradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    revenueGradient.addColorStop(0, 'rgba(34, 197, 94, 0.3)');
    revenueGradient.addColorStop(1, 'rgba(34, 197, 94, 0.0)');

    const costGradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    costGradient.addColorStop(0, 'rgba(251, 146, 60, 0.3)');
    costGradient.addColorStop(1, 'rgba(251, 146, 60, 0.0)');

    const profitGradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    profitGradient.addColorStop(0, 'rgba(99, 102, 241, 0.3)');
    profitGradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

    trendChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: mockAdminData.trendData['7days'].labels,
            datasets: [
                {
                    label: '收入',
                    data: mockAdminData.trendData['7days'].revenue,
                    borderColor: '#22c55e',
                    backgroundColor: revenueGradient,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '#22c55e',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                },
                {
                    label: '成本',
                    data: mockAdminData.trendData['7days'].cost,
                    borderColor: '#fb923c',
                    backgroundColor: costGradient,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '#fb923c',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                },
                {
                    label: '利润',
                    data: mockAdminData.trendData['7days'].profit,
                    borderColor: '#6366f1',
                    backgroundColor: profitGradient,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '#6366f1',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    align: 'end',
                    labels: {
                        color: '#64748b',
                        padding: 20,
                        font: { size: 13 },
                        usePointStyle: true,
                        pointStyle: 'circle'
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
                        label: function(context) {
                            return context.dataset.label + ': ¥' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#64748b',
                        font: {
                            size: 12
                        }
                    }
                },
                y: {
                    border: {
                        display: false
                    },
                    grid: {
                        color: 'rgba(100, 116, 139, 0.1)'
                    },
                    ticks: {
                        color: '#64748b',
                        font: {
                            size: 12
                        },
                        callback: function(value) {
                            return '¥' + (value / 10000).toFixed(0) + '万';
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Update trend chart based on selected time range
function updateTrendChart(range, text) {
    const trendTimeRangeText = document.getElementById('trendTimeRangeText');
    trendTimeRangeText.textContent = text;

    // Get the data for the selected range
    const data = mockAdminData.trendData[range];
    if (!data) {
        console.error(`No data found for range: ${range}`);
        return;
    }

    // Update the chart data
    if (trendChartInstance) {
        trendChartInstance.data.labels = data.labels;
        trendChartInstance.data.datasets[0].data = data.revenue;
        trendChartInstance.data.datasets[1].data = data.cost;
        trendChartInstance.data.datasets[2].data = data.profit;
        trendChartInstance.update();
    }

    console.log(`Updated trend chart to: ${text}`);

    // Close the dropdown
    document.activeElement.blur();
}

// Model Distribution Chart
function initModelChart() {
    const ctx = document.getElementById('modelChart');
    if (!ctx) return;

    const defaultData = mockAdminData.modelDistributionData['7days'];

    modelChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: defaultData.map(m => m.name),
            datasets: [{
                data: defaultData.map(m => m.value),
                backgroundColor: defaultData.map(m => m.color),
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
                    padding: 12
                }
            }
        }
    });
}

// Update model chart based on selected time range
function updateModelChart(range, text) {
    const modelTimeRangeText = document.getElementById('modelTimeRangeText');
    modelTimeRangeText.textContent = text;

    // Get the model distribution data for the selected range
    const data = mockAdminData.modelDistributionData[range];
    if (!data) {
        console.error(`No data found for range: ${range}`);
        return;
    }

    // Update the chart data
    if (modelChartInstance) {
        modelChartInstance.data.datasets[0].data = data.map(m => m.value);
        modelChartInstance.update();
    }

    console.log(`Updated model chart to: ${text}`);

    // Close the dropdown
    document.activeElement.blur();
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

// Date Range Functions
function setDateRange(range, text) {
    const dateRangeText = document.getElementById('dateRangeText');
    dateRangeText.textContent = text;

    // 根据选择的时间范围更新数据
    // 这里可以添加实际的API调用来获取不同时间范围的数据
    console.log(`Selected date range: ${range}`);

    // 关闭下拉菜单
    document.activeElement.blur();
}

// Update organization table based on selected time range
function updateOrgTable(range, text) {
    const orgTimeRangeText = document.getElementById('orgTimeRangeText');
    orgTimeRangeText.textContent = text;

    // Get the organization data for the selected range
    const data = mockAdminData.organizationData[range];
    if (!data) {
        console.error(`No data found for range: ${range}`);
        return;
    }

    // Update pagination with new data
    orgPagination.setData(data);
    orgPagination.currentRange = range;

    console.log(`Updated organization table to: ${text}`);

    // Close the dropdown
    document.activeElement.blur();
}

