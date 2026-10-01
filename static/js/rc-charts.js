/**
 * One consistent look and feel for every chart on the site. Pages can still
 * override any of these per chart.
 */
let sharedDefaultsApplied = false;
function applySharedDefaults(Chart) {
  if (sharedDefaultsApplied) return;
  sharedDefaultsApplied = true;

  const css = getComputedStyle(document.documentElement);
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.color = css.getPropertyValue('--muted').trim() || '#8a99b0';
  Chart.defaults.borderColor = 'rgba(148, 163, 184, 0.12)';

  // Smooth, consistent entrance and update animations.
  Chart.defaults.animation.duration = 700;
  Chart.defaults.animation.easing = 'easeOutQuart';

  // Matching tooltip styling across pages.
  Object.assign(Chart.defaults.plugins.tooltip, {
    backgroundColor: 'rgba(12, 9, 31, 0.95)',
    borderColor: 'rgba(176, 110, 255, 0.35)',
    borderWidth: 1,
    padding: 10,
    cornerRadius: 6,
    titleFont: { weight: '600' },
  });

  // Respect the OS "reduce motion" setting.
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    Chart.defaults.animation = false;
  }
}

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
    applySharedDefaults(Chart);
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

// chart.min.js is loaded just before this file, so apply the shared
// defaults immediately too, for pages that create charts directly.
if (typeof Chart !== 'undefined') applySharedDefaults(Chart);
