/**
 * Ensures Chart.js is loaded and the DOM is ready before page chart scripts run.
 */
window.rcChartsReady = function rcChartsReady(callback) {
  function run() {
    if (typeof Chart === 'undefined') {
      console.error('[RocketCanvas] Chart.js is not loaded. Charts will not render.');
      document.querySelectorAll('.chart-wrap, .chart-card').forEach((el) => {
        if (el.querySelector('.chart-load-err')) return;
        const note = document.createElement('p');
        note.className = 'chart-load-err';
        note.style.cssText = 'color:var(--loss);font-size:0.8rem;padding:1rem;font-family:var(--mono);';
        note.textContent = 'Charts failed to load. Hard-refresh the page (Ctrl+Shift+R).';
        el.appendChild(note);
      });
      return;
    }
    try {
      callback(Chart);
    } catch (err) {
      console.error('[RocketCanvas] Chart init error:', err);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
};
