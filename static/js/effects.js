window.triggerGoalExplosion = function() {
  if (typeof confetti !== 'function') return;

  var duration = 3000;
  var end = Date.now() + duration;

  (function frame() {
    confetti({
      particleCount: 7,
      angle: 60,
      spread: 55,
      origin: { x: 0 },
      colors: ['#b06eff', '#7c3aed', '#ff00ff', '#10e88a']
    });
    confetti({
      particleCount: 7,
      angle: 120,
      spread: 55,
      origin: { x: 1 },
      colors: ['#b06eff', '#7c3aed', '#ff00ff', '#10e88a']
    });

    if (Date.now() < end) {
      requestAnimationFrame(frame);
    }
  }());
  
  // Center blast
  confetti({
    particleCount: 150,
    spread: 100,
    origin: { y: 0.6 },
    colors: ['#ffffff', '#b06eff', '#d09fff']
  });
  
  // Play sound if available
  const explosionSound = new Audio('/static/sounds/goal-explosion-rocket-league.mp3');
  explosionSound.volume = 0.5;
  explosionSound.play().catch(e => console.log('Audio autoplay blocked', e));
};
