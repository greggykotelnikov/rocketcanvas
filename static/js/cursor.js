(function() {
  // Alpha Boost Cursor Particle System
  const canvas = document.createElement('canvas');
  canvas.style.position = 'fixed';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.width = '100vw';
  canvas.style.height = '100vh';
  canvas.style.pointerEvents = 'none';
  canvas.style.zIndex = '9998'; // Just below tutorial
  document.body.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  let width, height;

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  const particles = [];
  let mouse = { x: -100, y: -100, vx: 0, vy: 0 };
  let lastMouse = { x: -100, y: -100 };
  let lastTime = performance.now();

  // Audio Engine
  const boostAudio = new Audio('/static/sounds/alphaboost.mp3');
  boostAudio.loop = true;
  boostAudio.volume = 0;
  
  let audioUnlocked = false;
  let targetVolume = 0;

  function unlockAudio() {
    if (audioUnlocked) return;
    boostAudio.play().then(() => {
      audioUnlocked = true;
    }).catch(e => {
      // Autoplay blocked, wait for user to click
      console.log("Audio unlock failed, waiting for user click", e);
    });
  }

  // Need user interaction to play audio initially
  document.addEventListener('click', unlockAudio, { once: true });
  document.addEventListener('keydown', unlockAudio, { once: true });

  window.addEventListener('mousemove', (e) => {
    lastMouse.x = mouse.x;
    lastMouse.y = mouse.y;
    mouse.x = e.clientX;
    mouse.y = e.clientY;

    const now = performance.now();
    const dt = Math.max(1, now - lastTime);
    lastTime = now;

    // Calculate velocity
    const dx = mouse.x - lastMouse.x;
    const dy = mouse.y - lastMouse.y;
    const speed = Math.sqrt(dx*dx + dy*dy) / dt; 

    if (audioUnlocked) {
      targetVolume = Math.min(1, speed * 0.1);
      boostAudio.playbackRate = 0.8 + Math.min(1, speed * 0.2);
    }

    // Spawn particles based on speed
    const numParticles = Math.min(5, Math.floor(speed * 2));
    for (let i = 0; i < numParticles; i++) {
      particles.push({
        x: mouse.x + (Math.random() - 0.5) * 10,
        y: mouse.y + (Math.random() - 0.5) * 10,
        vx: (Math.random() - 0.5) * 2 - dx * 0.05,
        vy: (Math.random() - 0.5) * 2 - dy * 0.05,
        life: 1,
        size: Math.random() * 4 + 2,
        color: Math.random() > 0.5 ? '#f59e0b' : '#fbbf24' // Alpha boost golden colors
      });
    }
  });

  function render() {
    ctx.clearRect(0, 0, width, height);

    // Audio smooth volume transition
    if (audioUnlocked) {
      targetVolume = Math.max(0.05, targetVolume - 0.005); // Fade out much slower, keep a baseline hum
      boostAudio.volume += (targetVolume - boostAudio.volume) * 0.1;
    }

    // Update and draw particles
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.life -= 0.02;

      if (p.life <= 0) {
        particles.splice(i, 1);
        continue;
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.life;
      
      // Glow effect
      ctx.shadowBlur = 10;
      ctx.shadowColor = p.color;
      ctx.fill();
      ctx.globalAlpha = 1;
      ctx.shadowBlur = 0;
    }
    requestAnimationFrame(render);
  }
  
  // Start loop
  requestAnimationFrame(render);

})();
