// ===================================
// Client Billing V2 - Tailwind + DaisyUI
// 企业客户视角的账单页面
// ===================================

// Mock Data
const mockClientData = {
    orgTrend: {
        labels: ['12-01', '12-05', '12-10', '12-15', '12-20', '12-25', '12-31'],
        values: [120000, 180000, 250000, 420000, 580000, 720000, 850000]
    },
    departmentBreakdown: [
        { name: 'Alice', value: 350000, percentage: 41.2, color: '#6366f1' },
        { name: 'Bob', value: 280000, percentage: 32.9, color: '#8b5cf6' },
        { name: 'Charlie', value: 150000, percentage: 17.6, color: '#a855f7' },
        { name: 'David', value: 70000, percentage: 8.3, color: '#4f46e5' }
    ],
    modelUsage: [
        { name: '剧本', value: 280000, percentage: 32.9, color: '#6366f1' },
        { name: '图片', value: 250000, percentage: 29.4, color: '#8b5cf6' },
        { name: '视频', value: 200000, percentage: 23.5, color: '#a855f7' },
        { name: '配音', value: 120000, percentage: 14.2, color: '#4f46e5' }
    ],
    detailRecords: [
        { time: '12-31 09:42', project: 'marketing', projectName: '营销视频制作', member: 'Alice', model: 'Seedream 4.5 - 音频', mode: 'count', usage: '15秒', points: 250 },
        { time: '12-31 09:38', project: 'avatar', projectName: '虚拟人生成', member: 'Bob', model: 'Seedance 1.5 - 4K', mode: 'count', usage: '1 张', points: 120 },
        { time: '12-31 09:15', project: 'marketing', projectName: '营销视频制作', member: 'Alice', model: '豆包 TTS', mode: 'token', usage: '450 字符', points: 135 },
        { time: '12-31 08:50', project: 'tts', projectName: '语音合成测试', member: 'Charlie', model: 'Sora2 视频', mode: 'count', usage: '1 个任务', points: 500 },
        { time: '12-30 16:30', project: 'tts', projectName: '语音合成测试', member: 'Charlie', model: '豆包 TTS', mode: 'token', usage: '1,200 字符', points: 360 },
        { time: '12-30 14:20', project: 'content', projectName: '内容创作辅助', member: 'David', model: 'Seedream 4.5', mode: 'token', usage: '800 字符', points: 240 },
        { time: '12-30 11:05', project: 'marketing', projectName: '营销视频制作', member: 'Alice', model: 'Seedance 1.5', mode: 'count', usage: '3 张', points: 360 },
        { time: '12-30 09:30', project: 'avatar', projectName: '虚拟人生成', member: 'Bob', model: 'Seedance 1.5 - 4K', mode: 'count', usage: '2 张', points: 240 },
        { time: '12-29 17:45', project: 'tts', projectName: '语音合成测试', member: 'Charlie', model: '豆包 TTS', mode: 'token', usage: '950 字符', points: 285 },
        { time: '12-29 15:20', project: 'content', projectName: '内容创作辅助', member: 'David', model: 'Seedream 4.5', mode: 'token', usage: '1,200 字符', points: 360 },
        { time: '12-29 13:10', project: 'marketing', projectName: '营销视频制作', member: 'Alice', model: 'Sora2 视频', mode: 'count', usage: '1 个任务', points: 500 },
        { time: '12-29 10:30', project: 'avatar', projectName: '虚拟人生成', member: 'Bob', model: 'Seedance 1.5', mode: 'count', usage: '1 张', points: 120 },
        { time: '12-28 16:50', project: 'tts', projectName: '语音合成测试', member: 'Charlie', model: '豆包 TTS', mode: 'token', usage: '680 字符', points: 204 },
        { time: '12-28 14:15', project: 'content', projectName: '内容创作辅助', member: 'David', model: 'Seedream 4.5', mode: 'token', usage: '1,500 字符', points: 450 },
        { time: '12-28 11:40', project: 'marketing', projectName: '营销视频制作', member: 'Alice', model: 'Seedream 4.5 - 音频', mode: 'count', usage: '20秒', points: 333 },
        { time: '12-28 09:20', project: 'avatar', projectName: '虚拟人生成', member: 'Bob', model: 'Seedance 1.5 - 4K', mode: 'count', usage: '1 张', points: 120 },
        { time: '12-27 17:30', project: 'tts', projectName: '语音合成测试', member: 'Charlie', model: 'Sora2 视频', mode: 'count', usage: '1 个任务', points: 500 },
        { time: '12-27 15:10', project: 'content', projectName: '内容创作辅助', member: 'David', model: 'Seedream 4.5', mode: 'token', usage: '750 字符', points: 225 },
        { time: '12-27 12:45', project: 'marketing', projectName: '营销视频制作', member: 'Alice', model: '豆包 TTS', mode: 'token', usage: '520 字符', points: 156 },
        { time: '12-27 10:00', project: 'avatar', projectName: '虚拟人生成', member: 'Bob', model: 'Seedance 1.5', mode: 'count', usage: '2 张', points: 240 },
        { time: '12-26 16:25', project: 'tts', projectName: '语音合成测试', member: 'Charlie', model: '豆包 TTS', mode: 'token', usage: '1,100 字符', points: 330 },
        { time: '12-26 14:00', project: 'content', projectName: '内容创作辅助', member: 'David', model: 'Seedream 4.5', mode: 'token', usage: '980 字符', points: 294 },
        { time: '12-26 11:30', project: 'marketing', projectName: '营销视频制作', member: 'Alice', model: 'Sora2 视频', mode: 'count', usage: '1 个任务', points: 500 },
        { time: '12-26 09:15', project: 'avatar', projectName: '虚拟人生成', member: 'Bob', model: 'Seedance 1.5 - 4K', mode: 'count', usage: '1 张', points: 120 }
    ]
};

// Pagination state
let currentPage = 1;
let pageSize = 10;
let filteredRecords = [...mockClientData.detailRecords];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initOrgTrendChart();
    initModelUsageChart();
    initFilters();
    initThemeToggle();
    initDateFilters();
    initPagination();
    updateTopPersonnelList(mockClientData.departmentBreakdown);
    updateTable();
});

// Organization Trend Chart
function initOrgTrendChart() {
    const ctx = document.getElementById('orgTrendChart');
    if (!ctx) return;

    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.3)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: mockClientData.orgTrend.labels,
            datasets: [{
                label: '累计消费',
                data: mockClientData.orgTrend.values,
                borderColor: '#6366f1',
                backgroundColor: gradient,
                fill: true,
                tension: 0.4,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointShadowColor: 'rgba(99, 102, 241, 0.3)',
                pointShadowBlur: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 30, 40, 0.95)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(99, 102, 241, 0.5)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return '累计: ' + context.parsed.y.toLocaleString() + ' 积分';
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
                            return (value / 10000).toFixed(0) + '万';
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

// Model Usage Chart
function initModelUsageChart() {
    const ctx = document.getElementById('modelUsageChart');
    if (!ctx) {
        console.error('Canvas element modelUsageChart not found!');
        return;
    }

    // Check if Chart is loaded
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded! Using HTML fallback...');
        showModelUsageFallback();
        return;
    }

    console.log('Initializing model usage chart...', {
        labels: mockClientData.modelUsage.map(m => m.name),
        data: mockClientData.modelUsage.map(m => m.value)
    });

    try {
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: mockClientData.modelUsage.map(m => m.name),
                datasets: [{
                    data: mockClientData.modelUsage.map(m => m.value),
                    backgroundColor: mockClientData.modelUsage.map(m => m.color),
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
        console.log('Model usage chart initialized successfully!');
    } catch (error) {
        console.error('Error initializing model usage chart:', error);
        showModelUsageFallback();
    }
}

// Fallback: Show model usage as HTML when Chart.js fails
function showModelUsageFallback() {
    const canvas = document.getElementById('modelUsageChart');
    const fallback = document.getElementById('modelUsageChartFallback');

    if (canvas && fallback) {
        // Hide canvas, show fallback
        canvas.style.display = 'none';
        fallback.classList.remove('hidden');

        // Build HTML fallback
        const total = mockClientData.modelUsage.reduce((sum, item) => sum + item.value, 0);

        const gridContainer = fallback.querySelector('.grid');
        gridContainer.innerHTML = mockClientData.modelUsage.map(item => `
            <div class="flex items-center justify-between p-4 rounded-lg bg-base-200 hover:bg-base-300 transition-colors">
                <div class="flex items-center gap-3">
                    <div class="w-4 h-4 rounded-full" style="background-color: ${item.color}"></div>
                    <span class="font-semibold text-base-content">${item.name}</span>
                </div>
                <div class="flex items-center gap-4">
                    <div class="text-right">
                        <div class="font-bold text-brand-600">${item.value.toLocaleString()} 积分</div>
                        <div class="text-xs text-base-content/60">${item.percentage.toFixed(1)}%</div>
                    </div>
                    <div class="radial-progress text-brand-600" style="--value:${item.percentage}; --size:3rem;">${item.percentage.toFixed(0)}%</div>
                </div>
            </div>
        `).join('');

        // Add total at the bottom
        gridContainer.innerHTML += `
            <div class="mt-4 pt-4 border-t border-base-300">
                <div class="flex justify-between items-center">
                    <span class="font-bold text-base-content">总计</span>
                    <span class="font-bold text-xl text-brand-600">${total.toLocaleString()} 积分</span>
                </div>
            </div>
        `;

        console.log('Model usage fallback displayed successfully!');
    }
}

// Filters
function initFilters() {
    const projectFilter = document.getElementById('projectFilter');
    const memberFilter = document.getElementById('memberFilter');
    const dateFilter = document.getElementById('dateFilter');

    if (projectFilter) {
        projectFilter.addEventListener('change', filterRecords);
    }
    if (memberFilter) {
        memberFilter.addEventListener('change', filterRecords);
    }
    if (dateFilter) {
        dateFilter.addEventListener('change', filterRecords);
    }
}

function filterRecords() {
    const projectFilter = document.getElementById('projectFilter').value;
    const memberFilter = document.getElementById('memberFilter').value;

    let filtered = mockClientData.detailRecords;

    if (projectFilter !== 'all') {
        filtered = filtered.filter(r => r.project === projectFilter);
    }

    if (memberFilter !== 'all') {
        filtered = filtered.filter(r => r.member.toLowerCase() === memberFilter);
    }

    filteredRecords = filtered;
    currentPage = 1; // Reset to first page when filtering
    updateTable();
    updatePagination();
}

function updateTable() {
    const tbody = document.getElementById('detailTableBody');
    if (!tbody) return;

    // Calculate pagination
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const paginatedRecords = filteredRecords.slice(startIndex, endIndex);

    tbody.innerHTML = paginatedRecords.map(record => `
        <tr class="hover:bg-base-200/50 transition-colors">
            <td class="text-sm">${record.time}</td>
            <td><div class="badge badge-primary">${record.projectName}</div></td>
            <td>
                <div class="flex items-center gap-2">
                    <div class="avatar placeholder">
                        <div class="bg-brand-500 text-white rounded-full w-6">
                            <span class="text-xs">${record.member.charAt(0)}</span>
                        </div>
                    </div>
                    <span>${record.member}</span>
                </div>
            </td>
            <td>${record.model}</td>
            <td class="font-bold text-brand-600">${record.points.toLocaleString()} 积分</td>
        </tr>
    `).join('');
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

// Package selection animation
document.querySelectorAll('input[name="package"]').forEach(radio => {
    radio.addEventListener('change', function() {
        document.querySelectorAll('input[name="package"]').forEach(r => {
            r.closest('.card').classList.remove('ring-2', 'ring-brand-500');
        });
        this.closest('.card').classList.add('ring-2', 'ring-brand-500');
    });
});

// Date Filters
function initDateFilters() {
    // Trend chart date filter
    const trendDateFilter = document.getElementById('trendDateFilter');
    const trendStartDate = document.getElementById('trendStartDate');
    const trendEndDate = document.getElementById('trendEndDate');

    if (trendDateFilter) {
        trendDateFilter.addEventListener('change', function() {
            if (this.value === 'custom') {
                trendStartDate.classList.remove('hidden');
                trendEndDate.classList.remove('hidden');
            } else {
                trendStartDate.classList.add('hidden');
                trendEndDate.classList.add('hidden');
                updateTrendChart(this.value);
            }
        });
    }

    // Department chart date filter
    const departmentDateFilter = document.getElementById('departmentDateFilter');
    const departmentStartDate = document.getElementById('departmentStartDate');
    const departmentEndDate = document.getElementById('departmentEndDate');

    if (departmentDateFilter) {
        departmentDateFilter.addEventListener('change', function() {
            if (this.value === 'custom') {
                departmentStartDate.classList.remove('hidden');
                departmentEndDate.classList.remove('hidden');
            } else {
                departmentStartDate.classList.add('hidden');
                departmentEndDate.classList.add('hidden');
                updateDepartmentChart(this.value);
            }
        });
    }

    // Task type chart date filter
    const taskTypeDateFilter = document.getElementById('taskTypeDateFilter');
    const taskTypeStartDate = document.getElementById('taskTypeStartDate');
    const taskTypeEndDate = document.getElementById('taskTypeEndDate');

    if (taskTypeDateFilter) {
        taskTypeDateFilter.addEventListener('change', function() {
            if (this.value === 'custom') {
                taskTypeStartDate.classList.remove('hidden');
                taskTypeEndDate.classList.remove('hidden');
            } else {
                taskTypeStartDate.classList.add('hidden');
                taskTypeEndDate.classList.add('hidden');
                updateTaskTypeChart(this.value);
            }
        });
    }
}

// Update trend chart based on date filter
function updateTrendChart(period) {
    const chart = Chart.getChart('orgTrendChart');
    if (!chart) return;

    let newData = [];
    let newLabels = [];

    switch(period) {
        case 'today':
            newLabels = ['09:00', '12:00', '15:00', '18:00', '21:00'];
            newData = [5000, 15000, 28000, 35000, 42000];
            break;
        case '7days':
            newLabels = mockClientData.orgTrend.labels;
            newData = mockClientData.orgTrend.values;
            break;
        case '30days':
            newLabels = ['12-01', '12-05', '12-10', '12-15', '12-20', '12-25', '12-30'];
            newData = [300000, 450000, 580000, 720000, 850000, 950000, 1050000];
            break;
        case 'thisYear':
            newLabels = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
            newData = [200000, 350000, 480000, 620000, 750000, 900000, 1100000, 1250000, 1400000, 1600000, 1800000, 2000000];
            break;
    }

    chart.data.labels = newLabels;
    chart.data.datasets[0].data = newData;
    chart.update();
}

// Update department chart based on date filter
function updateDepartmentChart(period) {
    let newData;

    switch(period) {
        case 'today':
            newData = [
                { name: 'Alice', value: 25000, percentage: 45.5, color: '#6366f1' },
                { name: 'Bob', value: 18000, percentage: 32.7, color: '#8b5cf6' },
                { name: 'Charlie', value: 8000, percentage: 14.5, color: '#a855f7' },
                { name: 'David', value: 4000, percentage: 7.3, color: '#4f46e5' }
            ];
            break;
        case '7days':
        default:
            newData = [
                { name: 'Alice', value: 350000, percentage: 41.2, color: '#6366f1' },
                { name: 'Bob', value: 280000, percentage: 32.9, color: '#8b5cf6' },
                { name: 'Charlie', value: 150000, percentage: 17.6, color: '#a855f7' },
                { name: 'David', value: 70000, percentage: 8.3, color: '#4f46e5' }
            ];
            break;
        case '30days':
            newData = [
                { name: 'Alice', value: 450000, percentage: 38.5, color: '#6366f1' },
                { name: 'Bob', value: 380000, percentage: 32.5, color: '#8b5cf6' },
                { name: 'Charlie', value: 220000, percentage: 18.8, color: '#a855f7' },
                { name: 'David', value: 120000, percentage: 10.2, color: '#4f46e5' }
            ];
            break;
        case 'thisYear':
            newData = [
                { name: 'Alice', value: 2800000, percentage: 42.3, color: '#6366f1' },
                { name: 'Bob', value: 2100000, percentage: 31.7, color: '#8b5cf6' },
                { name: 'Charlie', value: 1200000, percentage: 18.1, color: '#a855f7' },
                { name: 'David', value: 530000, percentage: 7.9, color: '#4f46e5' }
            ];
            break;
    }

    // Update the top personnel list
    updateTopPersonnelList(newData);
}

// Update task type chart based on date filter
function updateTaskTypeChart(period) {
    const chart = Chart.getChart('modelUsageChart');
    if (!chart) return;

    let newData;

    switch(period) {
        case 'today':
            newData = [
                { name: '剧本', value: 12000, percentage: 35.3, color: '#6366f1' },
                { name: '图片', value: 10000, percentage: 29.4, color: '#8b5cf6' },
                { name: '视频', value: 8000, percentage: 23.5, color: '#a855f7' },
                { name: '配音', value: 4000, percentage: 11.8, color: '#4f46e5' }
            ];
            break;
        case '7days':
        default:
            newData = mockClientData.modelUsage;
            break;
        case '30days':
            newData = [
                { name: '剧本', value: 650000, percentage: 30.5, color: '#6366f1' },
                { name: '图片', value: 580000, percentage: 27.2, color: '#8b5cf6' },
                { name: '视频', value: 520000, percentage: 24.4, color: '#a855f7' },
                { name: '配音', value: 380000, percentage: 17.9, color: '#4f46e5' }
            ];
            break;
        case 'thisYear':
            newData = [
                { name: '剧本', value: 4500000, percentage: 33.8, color: '#6366f1' },
                { name: '图片', value: 3800000, percentage: 28.6, color: '#8b5cf6' },
                { name: '视频', value: 3200000, percentage: 24.1, color: '#a855f7' },
                { name: '配音', value: 1750000, percentage: 13.5, color: '#4f46e5' }
            ];
            break;
    }

    chart.data.labels = newData.map(d => d.name);
    chart.data.datasets[0].data = newData.map(d => d.value);
    chart.data.datasets[0].backgroundColor = newData.map(d => d.color);
    chart.options.plugins.legend.labels.generateLabels = (chart) => {
        const data = chart.data;
        return data.labels.map((label, i) => {
            const value = data.datasets[0].data[i];
            const percentage = newData[i].percentage;
            return `${label}: ${(value / 10000).toFixed(0)}万 (${percentage.toFixed(1)}%)`;
        });
    };
    chart.options.plugins.tooltip.callbacks.label = (context) => {
        const label = context.label || '';
        const value = context.parsed;
        const percentage = newData[context.dataIndex].percentage;
        return `${label}: ${value.toLocaleString()} 积分 (${percentage.toFixed(1)}%)`;
    };
    chart.update();
}

// Update top personnel list
function updateTopPersonnelList(data) {
    const container = document.getElementById('topPersonnelList');
    if (!container) return;

    // Generate top 10 personnel data
    const top10 = generateTop10Personnel(data);

    container.innerHTML = top10.map((person, index) => `
        <div class="flex items-center justify-between p-2 rounded-lg hover:bg-base-200 transition-colors">
            <div class="flex items-center gap-2">
                <div class="badge ${index < 3 ? 'badge-primary' : 'badge-ghost'} text-xs">${index + 1}</div>
                <div class="avatar placeholder">
                    <div class="bg-gradient-to-br from-brand-500 to-purple-600 text-white rounded-full w-6">
                        <span class="text-xs">${person.name.charAt(0)}</span>
                    </div>
                </div>
                <span class="font-medium text-sm">${person.name}</span>
            </div>
            <div class="text-right">
                <div class="font-bold text-brand-600 text-sm">${person.value.toLocaleString()}</div>
                <div class="text-xs text-base-content/60">${person.percentage.toFixed(1)}%</div>
            </div>
        </div>
    `).join('');
}

// Generate top 10 personnel data
function generateTop10Personnel(baseData) {
    const top10 = [
        { name: 'Alice', value: 350000, percentage: 41.2, color: '#6366f1' },
        { name: 'Bob', value: 280000, percentage: 32.9, color: '#8b5cf6' },
        { name: 'Charlie', value: 150000, percentage: 17.6, color: '#a855f7' },
        { name: 'David', value: 70000, percentage: 8.3, color: '#4f46e5' },
        { name: 'Emma', value: 55000, percentage: 6.5, color: '#6366f1' },
        { name: 'Frank', value: 42000, percentage: 4.9, color: '#8b5cf6' },
        { name: 'Grace', value: 35000, percentage: 4.1, color: '#a855f7' },
        { name: 'Henry', value: 28000, percentage: 3.3, color: '#4f46e5' },
        { name: 'Iris', value: 20000, percentage: 2.4, color: '#6366f1' },
        { name: 'Jack', value: 15000, percentage: 1.8, color: '#8b5cf6' }
    ];

    return top10;
}

// ===================================
// Pagination Functions
// ===================================

// Initialize pagination controls
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

    // Note: Page number buttons (page1Btn, page2Btn, page3Btn) are handled
    // dynamically in updatePageNumberButtons()

    updatePagination();
}

// Go to specific page
function goToPage(page) {
    const totalPages = getTotalPages();
    if (page < 1 || page > totalPages) return;

    currentPage = page;
    updateTable();
    updatePagination();
}

// Get total number of pages
function getTotalPages() {
    return Math.ceil(filteredRecords.length / pageSize);
}

// Update pagination controls and info
function updatePagination() {
    const totalPages = getTotalPages();
    const totalRecords = filteredRecords.length;
    const startIndex = (currentPage - 1) * pageSize + 1;
    const endIndex = Math.min(currentPage * pageSize, totalRecords);

    // Update pagination info text
    const paginationStart = document.getElementById('paginationStart');
    const paginationEnd = document.getElementById('paginationEnd');
    const paginationTotal = document.getElementById('paginationTotal');

    if (paginationStart) {
        paginationStart.textContent = totalRecords > 0 ? startIndex : 0;
    }
    if (paginationEnd) {
        paginationEnd.textContent = endIndex;
    }
    if (paginationTotal) {
        paginationTotal.textContent = totalRecords;
    }

    // Update navigation buttons
    const firstPageBtn = document.getElementById('firstPageBtn');
    const prevPageBtn = document.getElementById('prevPageBtn');
    const nextPageBtn = document.getElementById('nextPageBtn');
    const lastPageBtn = document.getElementById('lastPageBtn');

    if (firstPageBtn) {
        firstPageBtn.disabled = currentPage === 1;
    }
    if (prevPageBtn) {
        prevPageBtn.disabled = currentPage === 1;
    }
    if (nextPageBtn) {
        nextPageBtn.disabled = currentPage === totalPages || totalPages === 0;
    }
    if (lastPageBtn) {
        lastPageBtn.disabled = currentPage === totalPages || totalPages === 0;
    }

    // Update page number buttons
    updatePageNumberButtons(totalPages);
}

// Update page number buttons dynamically
function updatePageNumberButtons(totalPages) {
    const maxVisiblePages = 3;
    let startPage = Math.max(1, currentPage - 1);
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    // Adjust start if we're near the end
    if (endPage - startPage < maxVisiblePages - 1) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    // Update the three page buttons
    for (let i = 1; i <= 3; i++) {
        const pageBtn = document.getElementById(`page${i}Btn`);

        if (pageBtn) {
            // Remove old event listener by cloning
            const newBtn = pageBtn.cloneNode(true);
            pageBtn.parentNode.replaceChild(newBtn, pageBtn);

            const pageNum = startPage + i - 1;

            if (pageNum <= totalPages) {
                newBtn.textContent = pageNum;
                newBtn.classList.remove('hidden');
                newBtn.classList.toggle('btn-active', pageNum === currentPage);

                // Add new event listener
                newBtn.addEventListener('click', () => goToPage(pageNum));
            } else {
                newBtn.classList.add('hidden');
            }
        }
    }
}
