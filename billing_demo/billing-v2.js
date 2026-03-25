// ===================================
// Billing Page V2 - Tailwind + DaisyUI
// ===================================

// Mock data
const mockData = {
    consumptionTrend: {
        labels: ['12-25', '12-26', '12-27', '12-28', '12-29', '12-30', '12-31'],
        values: [15000, 22000, 18000, 25000, 20000, 15000, 10000]
    }
};

// Initialize Chart
document.addEventListener('DOMContentLoaded', function() {
    initChart();
    initThemeToggle();
});

function initChart() {
    const ctx = document.getElementById('consumptionChart');
    if (!ctx) return;

    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.3)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: mockData.consumptionTrend.labels,
            datasets: [{
                label: '消耗积分',
                data: mockData.consumptionTrend.values,
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
                            return context.parsed.y.toLocaleString() + ' 积分';
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
                            return value.toLocaleString();
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

// Theme Toggle
function initThemeToggle() {
    const toggle = document.getElementById('theme-toggle');
    const html = document.documentElement;

    // Load saved theme
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
