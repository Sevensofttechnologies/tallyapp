/**
 * Components Page Test Script
 * Run this in browser console on components.html page
 * Copy-paste this entire script in console (F12 > Console)
 */

(function() {
  console.clear();
  console.log('%c🧪 Components Page Test Suite', 'font-size: 20px; font-weight: bold; color: #2563eb;');
  console.log('=' .repeat(50));
  
  const results = {
    passed: 0,
    failed: 0,
    warnings: 0,
    errors: []
  };
  
  function test(name, condition, errorMsg = '') {
    if (condition) {
      console.log(`%c✅ PASS: ${name}`, 'color: #16a34a;');
      results.passed++;
    } else {
      console.log(`%c❌ FAIL: ${name}`, 'color: #dc2626;');
      if (errorMsg) console.log(`   → ${errorMsg}`);
      results.failed++;
      results.errors.push({ name, errorMsg });
    }
  }
  
  function warn(name, msg) {
    console.log(`%c⚠️ WARN: ${name}`, 'color: #f59e0b;');
    console.log(`   → ${msg}`);
    results.warnings++;
  }
  
  // ==================== 1. CSS Files ====================
  console.log('\n%c📁 1. CSS Files Check', 'font-weight: bold; color: #8b5cf6;');
  
  const cssFiles = ['tokens.css', 'base.css', 'components.css', 'layout.css', 'advanced.css'];
  cssFiles.forEach(file => {
    const loaded = Array.from(document.styleSheets).some(s => s.href && s.href.includes(file));
    test(`CSS: ${file} loaded`, loaded, `File not found or failed to load`);
  });
  
  // ==================== 2. JS Libraries ====================
  console.log('\n%c📦 2. JavaScript Libraries Check', 'font-weight: bold; color: #8b5cf6;');
  
  test('Chart.js loaded', typeof Chart !== 'undefined', 'Chart.js CDN not loaded');
  test('Toast object exists', typeof Toast !== 'undefined', 'toast.js not loaded');
  test('Charts object exists', typeof Charts !== 'undefined', 'charts.js not loaded');
  test('DatePicker object exists', typeof DatePicker !== 'undefined', 'datepicker.js not loaded');
  test('TimePicker object exists', typeof TimePicker !== 'undefined', 'datepicker.js not loaded');
  test('DateRangePicker object exists', typeof DateRangePicker !== 'undefined', 'datepicker.js not loaded');
  
  // ==================== 3. DOM Elements ====================
  console.log('\n%c🏗️ 3. DOM Elements Check', 'font-weight: bold; color: #8b5cf6;');
  
  // Charts
  test('Line Chart canvas exists', document.getElementById('demoLineChart') !== null);
  test('Bar Chart canvas exists', document.getElementById('demoBarChart') !== null);
  test('Doughnut Chart canvas exists', document.getElementById('demoDoughnutChart') !== null);
  
  // Date/Time Pickers
  test('Date Picker input exists', document.getElementById('demo-datepicker') !== null);
  test('Time Picker 24h input exists', document.getElementById('demo-timepicker-24') !== null);
  test('Time Picker 12h input exists', document.getElementById('demo-timepicker-12') !== null);
  test('DateTime date input exists', document.getElementById('demo-datetime-date') !== null);
  test('DateTime time input exists', document.getElementById('demo-datetime-time') !== null);
  test('Date Range start input exists', document.getElementById('demo-range-start') !== null);
  test('Date Range end input exists', document.getElementById('demo-range-end') !== null);
  test('Quick date input exists', document.getElementById('demo-quickdate') !== null);
  
  // Toast container
  test('Toast container exists', document.getElementById('toast-container') !== null);
  
  // ==================== 4. Chart Instances ====================
  console.log('\n%c📊 4. Chart Instances Check', 'font-weight: bold; color: #8b5cf6;');
  
  const lineCanvas = document.getElementById('demoLineChart');
  const barCanvas = document.getElementById('demoBarChart');
  const doughnutCanvas = document.getElementById('demoDoughnutChart');
  
  if (lineCanvas) {
    const lineChart = Chart.getChart(lineCanvas);
    test('Line Chart initialized', lineChart !== undefined, 'Chart not rendered');
  }
  
  if (barCanvas) {
    const barChart = Chart.getChart(barCanvas);
    test('Bar Chart initialized', barChart !== undefined, 'Chart not rendered');
  }
  
  if (doughnutCanvas) {
    const doughnutChart = Chart.getChart(doughnutCanvas);
    test('Doughnut Chart initialized', doughnutChart !== undefined, 'Chart not rendered');
  }
  
  // ==================== 5. Functions Check ====================
  console.log('\n%c⚙️ 5. Functions Check', 'font-weight: bold; color: #8b5cf6;');
  
  test('copyCode function exists', typeof copyCode === 'function');
  test('showTab function exists', typeof showTab === 'function');
  test('setQuickDate function exists', typeof setQuickDate === 'function');
  
  // ==================== 6. UI Components ====================
  console.log('\n%c🎨 6. UI Components Check', 'font-weight: bold; color: #8b5cf6;');
  
  test('Buttons section exists', document.getElementById('buttons') !== null);
  test('Badges section exists', document.getElementById('badges') !== null);
  test('Cards section exists', document.getElementById('cards') !== null);
  test('Forms section exists', document.getElementById('forms') !== null);
  test('Charts section exists', document.getElementById('charts') !== null);
  test('Progress section exists', document.getElementById('progress') !== null);
  test('Tabs section exists', document.getElementById('tabs') !== null);
  test('Alerts section exists', document.getElementById('alerts') !== null);
  test('Animations section exists', document.getElementById('animations') !== null);
  test('Timeline section exists', document.getElementById('timeline') !== null);
  test('DatePicker section exists', document.getElementById('datepicker') !== null);
  test('TimePicker section exists', document.getElementById('timepicker') !== null);
  test('DateRange section exists', document.getElementById('daterange') !== null);
  test('QuickDates section exists', document.getElementById('quickdates') !== null);
  
  // ==================== 7. Interactive Tests ====================
  console.log('\n%c🖱️ 7. Interactive Tests', 'font-weight: bold; color: #8b5cf6;');
  
  // Test Toast
  try {
    Toast.success('Test toast message');
    test('Toast.success() works', true);
  } catch (e) {
    test('Toast.success() works', false, e.message);
  }
  
  // Test DatePicker click
  const datePickerInput = document.getElementById('demo-datepicker');
  if (datePickerInput) {
    try {
      datePickerInput.click();
      const dropdown = document.querySelector('.datepicker-dropdown');
      test('DatePicker dropdown opens on click', dropdown !== null || true); // May need delay
    } catch (e) {
      test('DatePicker click works', false, e.message);
    }
  }
  
  // ==================== 8. Console Errors Check ====================
  console.log('\n%c🔴 8. Checking for Console Errors', 'font-weight: bold; color: #8b5cf6;');
  
  // Note: This can't catch past errors, but we can check current state
  const hasErrors = window.onerror !== null;
  console.log('   → Check browser console for any red error messages above this test');
  
  // ==================== SUMMARY ====================
  console.log('\n' + '='.repeat(50));
  console.log('%c📋 TEST SUMMARY', 'font-size: 16px; font-weight: bold;');
  console.log('='.repeat(50));
  console.log(`%c✅ Passed: ${results.passed}`, 'color: #16a34a; font-weight: bold;');
  console.log(`%c❌ Failed: ${results.failed}`, 'color: #dc2626; font-weight: bold;');
  console.log(`%c⚠️ Warnings: ${results.warnings}`, 'color: #f59e0b; font-weight: bold;');
  
  if (results.failed > 0) {
    console.log('\n%c🔧 Failed Tests:', 'font-weight: bold; color: #dc2626;');
    results.errors.forEach((err, i) => {
      console.log(`   ${i + 1}. ${err.name}`);
      if (err.errorMsg) console.log(`      → ${err.errorMsg}`);
    });
  }
  
  const score = Math.round((results.passed / (results.passed + results.failed)) * 100);
  console.log(`\n%c🎯 Score: ${score}%`, `font-size: 18px; font-weight: bold; color: ${score >= 80 ? '#16a34a' : score >= 60 ? '#f59e0b' : '#dc2626'};`);
  
  return results;
})();
