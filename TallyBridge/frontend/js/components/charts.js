/**
 * VanillaNext Charts Library
 * Wrapper for Chart.js and ApexCharts with Premium Styling
 */

const Charts = {
  // Storage for chart instances
  instances: {},

  /**
   * Show a custom themed toast for chart interactions
   */
  showToast: function (icon, title, message) {
    // Remove existing toast
    const existing = document.querySelector('.chart-toast');
    if (existing) existing.remove();

    // Create new toast
    const toast = document.createElement('div');
    toast.className = 'chart-toast';
    toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
        `;

    document.body.appendChild(toast);

    // Auto-hide after 3 seconds
    setTimeout(() => {
      toast.classList.add('hide');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  },

  /**
   * Real-time Stats Widget Logic
   */
  initStatsWidget: function (id, initialValue, interval = 3000) {
    let value = initialValue;
    const el = document.getElementById(`${id}-value`);
    const timeEl = document.getElementById(`${id}-time`);

    if (!el) return;

    const update = () => {
      value += Math.floor(Math.random() * 8) - 2;
      el.textContent = value.toLocaleString();

      // Animate scale
      el.style.transform = 'scale(1.1)';
      setTimeout(() => el.style.transform = 'scale(1)', 200);

      // Update timestamp
      if (timeEl) {
        const now = new Date().toLocaleTimeString();
        timeEl.textContent = now;
      }
    };

    setInterval(update, interval);
  },

  /**
   * Chart.js: Real-time Line Chart
   */
  createRealtimeLine: function (id) {
    const ctx = document.getElementById(id);
    if (!ctx) return;

    const data = window.chartData?.chartjs?.realtimeLine || {
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
    };

    const chart = new Chart(ctx, {
      type: 'line',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 750 },
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, max: 100, grid: { color: 'rgba(0,0,0,0.05)' } },
          x: { grid: { display: false } }
        }
      }
    });

    this.instances[id] = chart;

    // Start Update Loop
    setInterval(() => {
      data.datasets[0].data.shift();
      data.datasets[0].data.push(Math.floor(Math.random() * 40) + 50);
      chart.update('none');
    }, 2000);
  },

  /**
   * Chart.js: Real-time Bar Chart
   */
  createRealtimeBar: function (id) {
    const ctx = document.getElementById(id);
    if (!ctx) return;

    const data = window.chartData?.chartjs?.realtimeBar || {
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
    };

    const chart = new Chart(ctx, {
      type: 'bar',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 750 },
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, max: 100, grid: { color: 'rgba(0,0,0,0.05)' } },
          x: { grid: { display: false } }
        }
      }
    });

    this.instances[id] = chart;

    setInterval(() => {
      data.datasets[0].data = data.datasets[0].data.map(val =>
        Math.max(20, Math.min(95, val + Math.floor(Math.random() * 20) - 10))
      );
      chart.update('active');
    }, 3000);
  },

  /**
   * Chart.js: Interactive Pie Chart
   */
  createPie: function (id) {
    const ctx = document.getElementById(id);
    if (!ctx) return;

    const data = window.chartData?.chartjs?.pie || {
      labels: ['Direct', 'Social', 'Referral', 'Email', 'Search'],
      datasets: [{
        data: [300, 150, 100, 80, 120],
        backgroundColor: ['#2563eb', '#16a34a', '#f59e0b', '#ec4899', '#6366f1'],
        borderWidth: 3,
        borderColor: '#fff'
      }]
    };

    const chart = new Chart(ctx, {
      type: 'pie',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' }
        },
        onClick: (e, activeEls) => {
          if (activeEls.length > 0) {
            const index = activeEls[0].index;
            const label = chart.data.labels[index];
            const value = chart.data.datasets[0].data[index];
            const total = chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
            this.showToast('🍰', `${label} Traffic`, `${value} visitors • ${((value / total) * 100).toFixed(1)}% of total`);
          }
        }
      }
    });
    this.instances[id] = chart;
  },

  /**
   * Chart.js: Interactive Doughnut
   */
  createDoughnut: function (id) {
    const ctx = document.getElementById(id);
    if (!ctx) return;

    const data = window.chartData?.chartjs?.doughnut || {
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
    };

    const chart = new Chart(ctx, {
      type: 'doughnut',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } },
        onClick: (e, activeEls) => {
          if (activeEls.length > 0) {
            const index = activeEls[0].index;
            const label = chart.data.labels[index];
            const value = chart.data.datasets[0].data[index];
            const total = chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
            this.showToast('👥', `Age Group: ${label}`, `${value} users • ${((value / total) * 100).toFixed(1)}%`);
          }
        }
      }
    });
    this.instances[id] = chart;
  },

  /**
   * Chart.js: Radar Chart
   */
  createRadar: function (id) {
    const ctx = document.getElementById(id);
    if (!ctx) return;

    const data = window.chartData?.chartjs?.radar || {
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
    };

    new Chart(ctx, {
      type: 'radar',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: { beginAtZero: true, max: 100, ticks: { stepSize: 20 } }
        },
        plugins: { legend: { position: 'top' } }
      }
    });
  },

  /**
   * Chart.js: Polar Area
   */
  createPolarArea: function (id) {
    const ctx = document.getElementById(id);
    if (!ctx) return;

    const data = window.chartData?.chartjs?.polarArea || {
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
    };

    new Chart(ctx, {
      type: 'polarArea',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { padding: 15 } }
        }
      }
    });
  },

  /**
   * Apex: Heatmap
   */
  createHeatmap: function (id) {
    const series = window.chartData?.apexcharts?.heatmap?.series || (function () {
      const generateData = (name, count) => {
        const data = [];
        for (let i = 0; i < count; i++) {
          data.push({ x: `W${i + 1}`, y: Math.floor(Math.random() * 90) + 10 });
        }
        return { name, data };
      };
      return [
        generateData('Mon', 10), generateData('Tue', 10), generateData('Wed', 10),
        generateData('Thu', 10), generateData('Fri', 10), generateData('Sat', 10), generateData('Sun', 10)
      ];
    })();

    const options = {
      chart: { height: 300, type: 'heatmap', toolbar: { show: false } },
      dataLabels: { enabled: false },
      colors: ['#2563eb'],
      series: series,
      xaxis: { type: 'category' }
    };

    const chart = new ApexCharts(document.querySelector(`#${id}`), options);
    chart.render();
  },

  /**
   * Apex: Candlestick
   */
  createCandlestick: function (id) {
    const series = window.chartData?.apexcharts?.candlestick?.series || [{
      data: [
        { x: new Date(1538778600000), y: [6629.81, 6650.5, 6623.04, 6633.33] },
        { x: new Date(1538780400000), y: [6632.01, 6643.59, 6620, 6630.11] },
        { x: new Date(1538782200000), y: [6630.71, 6648.95, 6623.34, 6635.65] },
        { x: new Date(1538784000000), y: [6635.65, 6651, 6629.67, 6638.24] },
        { x: new Date(1538785800000), y: [6638.24, 6640, 6620, 6624.47] },
        { x: new Date(1538787600000), y: [6624.53, 6636.03, 6621.68, 6624.31] }
      ]
    }];

    const options = {
      chart: { height: 300, type: 'candlestick', toolbar: { show: false } },
      series: series,
      xaxis: { type: 'datetime' },
      plotOptions: {
        candlestick: { colors: { upward: '#16a34a', downward: '#dc2626' } }
      }
    };

    const chart = new ApexCharts(document.querySelector(`#${id}`), options);
    chart.render();
  },

  /**
   * Apex: Real-time Area
   */
  createRealtimeArea: function (id) {
    let areaData = window.chartData?.apexcharts?.area?.series[0]?.data || [31000, 40000, 35000, 51000, 49000, 60000, 70000];
    const categories = window.chartData?.apexcharts?.area?.categories || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'];

    const options = {
      chart: {
        height: 300, type: 'area', toolbar: { show: false },
        animations: { enabled: true, dynamicAnimation: { speed: 1000 } }
      },
      dataLabels: { enabled: false },
      stroke: { curve: 'smooth', width: 3 },
      colors: ['#14b8a6'],
      series: [{ name: 'Revenue', data: areaData }],
      xaxis: { categories: categories },
      fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.7, opacityTo: 0.2 } }
    };

    const chart = new ApexCharts(document.querySelector(`#${id}`), options);
    chart.render();

    setInterval(() => {
      areaData = areaData.map(val => Math.max(20000, val + Math.floor(Math.random() * 10000) - 5000));
      chart.updateSeries([{ data: areaData }]);
    }, 4000);
  },

  /**
   * Apex: Mixed (Line + Bar)
   */
  createMixed: function (id) {
    const series = window.chartData?.apexcharts?.mixed?.series || [{
      name: 'Orders', type: 'column', data: [23, 42, 35, 27, 43, 22, 17, 31]
    }, {
      name: 'Shipped', type: 'column', data: [20, 38, 32, 24, 40, 20, 15, 28]
    }, {
      name: 'Revenue', type: 'line', data: [30, 55, 45, 35, 60, 30, 25, 40]
    }];
    const categories = window.chartData?.apexcharts?.mixed?.categories || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'];

    const options = {
      chart: { height: 300, type: 'line', toolbar: { show: false } },
      stroke: { width: [0, 0, 3], curve: 'smooth' },
      plotOptions: { bar: { columnWidth: '50%', borderRadius: 6 } },
      colors: ['#2563eb', '#16a34a', '#f59e0b'],
      series: series,
      xaxis: { categories: categories },
      dataLabels: { enabled: false }
    };

    const chart = new ApexCharts(document.querySelector(`#${id}`), options);
    chart.render();
  },

  /**
   * Apex: Radial Bar with Click
   */
  createRadial: function (id) {
    let values = window.chartData?.apexcharts?.radial?.series || [76, 67, 61, 90];
    const labels = window.chartData?.apexcharts?.radial?.labels || ['Sales', 'Marketing', 'Support', 'Development'];

    const options = {
      chart: {
        height: 300, type: 'radialBar',
        events: {
          click: (event, chartContext, config) => {
            if (config.dataPointIndex >= 0) {
              const label = labels[config.dataPointIndex];
              const val = values[config.dataPointIndex];
              this.showToast('🎯', `${label} Goal`, `${val}% complete • Click again to refresh!`);
              values[config.dataPointIndex] = Math.floor(Math.random() * 40) + 60;
              chart.updateSeries(values);
            }
          }
        }
      },
      plotOptions: {
        radialBar: {
          startAngle: 0, endAngle: 270, hollow: { size: '35%' },
          dataLabels: {
            name: { fontSize: '14px' },
            value: { fontSize: '22px', fontWeight: 700 }
          }
        }
      },
      colors: ['#06b6d4', '#2563eb', '#6366f1', '#d1d5db'],
      series: values,
      labels: labels
    };

    const chart = new ApexCharts(document.querySelector(`#${id}`), options);
    chart.render();
  },

  /**
   * Apex: Bubble
   */
  createBubble: function (id) {
    const series = window.chartData?.apexcharts?.bubble?.series || (function () {
      const generateBubbleData = (count, yrange) => {
        const series = [];
        for (let i = 0; i < count; i++) {
          series.push([
            Math.floor(Math.random() * 750) + 1,
            Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min,
            Math.floor(Math.random() * 60) + 15
          ]);
        }
        return series;
      };
      return [
        { name: 'Product A', data: generateBubbleData(15, { min: 10, max: 60 }) },
        { name: 'Product B', data: generateBubbleData(15, { min: 10, max: 60 }) }
      ];
    })();

    const options = {
      chart: { height: 300, type: 'bubble', toolbar: { show: false } },
      dataLabels: { enabled: false },
      colors: ['#2563eb', '#14b8a6', '#f59e0b', '#ec4899'],
      series: series,
      fill: { opacity: 0.8 },
      xaxis: { type: 'category' }
    };

    const chart = new ApexCharts(document.querySelector(`#${id}`), options);
    chart.render();
  },

  /**
   * Chart.js: Simplified Line Chart Wrapper
   */
  line: function (id, config) {
    const ctx = document.getElementById(id);
    if (!ctx) return;
    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: config.labels,
        datasets: config.datasets.map(ds => ({
          ...ds,
          borderColor: ds.color || ds.borderColor,
          backgroundColor: ds.fill ? (ds.color || ds.backgroundColor) + '33' : 'transparent',
        }))
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  },

  /**
   * Chart.js: Simplified Bar Chart Wrapper
   */
  bar: function (id, config) {
    const ctx = document.getElementById(id);
    if (!ctx) return;
    return new Chart(ctx, {
      type: 'bar',
      data: {
        labels: config.labels,
        datasets: config.datasets.map(ds => ({
          ...ds,
          backgroundColor: ds.colors || ds.backgroundColor,
        }))
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  },

  /**
   * Chart.js: Simplified Doughnut Chart Wrapper
   */
  doughnut: function (id, config) {
    const ctx = document.getElementById(id);
    if (!ctx) return;
    return new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: config.labels,
        datasets: [{
          data: config.values,
          backgroundColor: config.colors,
        }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }
};

window.Charts = Charts;
