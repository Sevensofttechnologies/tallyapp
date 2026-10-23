/**
 * Chart Data Storage
 * Centralized data for all charts in the application
 */

const chartData = {
    chartjs: {
        realtimeLine: {
            labels: ['10s ago', '9s', '8s', '7s', '6s', '5s', '4s', '3s', '2s', '1s', 'Now'],
            datasets: [{
                label: 'Requests/sec',
                data: [45, 52, 48, 61, 55, 58, 63, 59, 67, 62, 70],
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        realtimeBar: {
            labels: ['Electronics', 'Clothing', 'Food', 'Books', 'Sports'],
            datasets: [{
                label: 'Sales',
                data: [65, 59, 80, 81, 56],
                backgroundColor: [
                    'rgba(37, 99, 235, 0.8)',
                    'rgba(22, 163, 74, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(236, 72, 153, 0.8)',
                    'rgba(99, 102, 241, 0.8)'
                ],
                borderRadius: 8
            }]
        },
        pie: {
            labels: ['Direct', 'Social', 'Referral', 'Email', 'Search'],
            datasets: [{
                data: [300, 150, 100, 80, 120],
                backgroundColor: ['#2563eb', '#16a34a', '#f59e0b', '#ec4899', '#6366f1'],
                borderWidth: 3,
                borderColor: '#fff'
            }]
        },
        doughnut: {
            labels: ['18-24', '25-34', '35-44', '45-54', '55+'],
            datasets: [{
                data: [220, 340, 180, 120, 90],
                backgroundColor: [
                    'rgba(37, 99, 235, 0.8)',
                    'rgba(22, 163, 74, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(236, 72, 153, 0.8)',
                    'rgba(99, 102, 241, 0.8)'
                ],
                borderWidth: 3,
                borderColor: '#fff'
            }]
        },
        radar: {
            labels: ['Speed', 'Reliability', 'Comfort', 'Safety', 'Efficiency', 'Design'],
            datasets: [{
                label: 'Product A',
                data: [85, 90, 75, 80, 70, 95],
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.2)',
                borderWidth: 2
            }, {
                label: 'Product B',
                data: [70, 85, 90, 75, 85, 80],
                borderColor: '#16a34a',
                backgroundColor: 'rgba(22, 163, 74, 0.2)',
                borderWidth: 2
            }]
        },
        polarArea: {
            labels: ['Chrome', 'Safari', 'Firefox', 'Edge', 'Opera'],
            datasets: [{
                data: [45, 25, 15, 10, 5],
                backgroundColor: [
                    'rgba(37, 99, 235, 0.7)',
                    'rgba(22, 163, 74, 0.7)',
                    'rgba(245, 158, 11, 0.7)',
                    'rgba(236, 72, 153, 0.7)',
                    'rgba(99, 102, 241, 0.7)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        }
    },
    apexcharts: {
        area: {
            series: [{ name: 'Revenue', data: [31000, 40000, 35000, 51000, 49000, 60000, 70000] }],
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
        },
        mixed: {
            series: [{
                name: 'Orders', type: 'column', data: [23, 42, 35, 27, 43, 22, 17, 31]
            }, {
                name: 'Shipped', type: 'column', data: [20, 38, 32, 24, 40, 20, 15, 28]
            }, {
                name: 'Revenue', type: 'line', data: [30, 55, 45, 35, 60, 30, 25, 40]
            }],
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
        },
        radial: {
            series: [76, 67, 61, 90],
            labels: ['Sales', 'Marketing', 'Support', 'Development']
        }
    }
};

window.chartData = chartData;
