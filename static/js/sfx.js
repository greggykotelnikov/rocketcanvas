/**
 * RocketCanvas SFX & BGM Manager
 * Procedural Persona 5 style Web Audio API sound effects and Music Player widget logic.
 */

(function () {
  // Web Audio Context
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  let audioCtx = null;

  // Track the BGM element
  let bgmAudio = null;
  let isPlaying = false;
  let currentTrackIdx = 0;
  let currentVolume = parseFloat(localStorage.getItem('rc-bgm-volume') || '0.5');

  // Rate limiting for hover sounds to keep it clean and professional
  let lastHoverTime = 0;
  const HOVER_LIMIT_MS = 90;

  // Track list
  const playlist = [
    {
      title: "RLCS Overtime Theme",
      url: "/static/sounds/rlcs-overtime.mp3",
      source: "local"
    },
    {
      title: "Neon Tokyo Lofi Synth",
      url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
      source: "stream"
    },
    {
      title: "Midnight Arcade Groove",
      url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
      source: "stream"
    }
  ];

  // Initialize Audio Context on first click/interaction
  function initAudio() {
    if (!audioCtx) {
      audioCtx = new AudioContextClass();
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    
    // Also init BGM element if not done yet
    if (!bgmAudio) {
      bgmAudio = new Audio();
      bgmAudio.loop = true;
      bgmAudio.volume = currentVolume;
      bgmAudio.src = playlist[currentTrackIdx].url;

      // Handle track endings if loop is disabled, but we loop for ambient feel
      bgmAudio.addEventListener('error', (e) => {
        console.warn("BGM Stream failed to load or was interrupted:", e);
      });
    }
  }

  // --- PROCEDURAL SFX SYNTHESIZERS ---

  // Snappy double-tick hover sound (Persona 5 style)
  function playHover() {
    if (!audioCtx) return;
    const now = Date.now();
    if (now - lastHoverTime < HOVER_LIMIT_MS) return; // Prevent double-triggering clutter
    lastHoverTime = now;

    if (audioCtx.state === 'suspended') audioCtx.resume();

    // First tick
    const osc1 = audioCtx.createOscillator();
    const gain1 = audioCtx.createGain();
    osc1.type = 'sine';
    osc1.frequency.setValueAtTime(988, audioCtx.currentTime); // B5 note
    gain1.gain.setValueAtTime(0.015, audioCtx.currentTime);
    gain1.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.015);
    osc1.connect(gain1);
    gain1.connect(audioCtx.destination);
    osc1.start();
    osc1.stop(audioCtx.currentTime + 0.015);

    // Second tick (slight delay)
    setTimeout(() => {
      if (!audioCtx) return;
      const osc2 = audioCtx.createOscillator();
      const gain2 = audioCtx.createGain();
      osc2.type = 'sine';
      osc2.frequency.setValueAtTime(1047, audioCtx.currentTime); // C6 note
      gain2.gain.setValueAtTime(0.012, audioCtx.currentTime);
      gain2.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.012);
      osc2.connect(gain2);
      gain2.connect(audioCtx.destination);
      osc2.start();
      osc2.stop(audioCtx.currentTime + 0.012);
    }, 15);
  }

  // Dual-pitch ascending chime (Confirm SFX)
  function playConfirm() {
    if (!audioCtx) return;
    if (audioCtx.state === 'suspended') audioCtx.resume();

    const t = audioCtx.currentTime;
    
    // Note 1 (E5 -> C6)
    const osc1 = audioCtx.createOscillator();
    const gain1 = audioCtx.createGain();
    osc1.type = 'triangle';
    osc1.frequency.setValueAtTime(659.25, t); // E5
    osc1.frequency.exponentialRampToValueAtTime(1046.50, t + 0.12); // C6
    gain1.gain.setValueAtTime(0.06, t);
    gain1.gain.exponentialRampToValueAtTime(0.001, t + 0.18);
    osc1.connect(gain1);
    gain1.connect(audioCtx.destination);
    osc1.start();
    osc1.stop(t + 0.18);

    // Note 2 (G5 -> E6, slight delay)
    setTimeout(() => {
      if (!audioCtx) return;
      const t2 = audioCtx.currentTime;
      const osc2 = audioCtx.createOscillator();
      const gain2 = audioCtx.createGain();
      osc2.type = 'sine';
      osc2.frequency.setValueAtTime(783.99, t2); // G5
      osc2.frequency.exponentialRampToValueAtTime(1318.51, t2 + 0.12); // E6
      gain2.gain.setValueAtTime(0.04, t2);
      gain2.gain.exponentialRampToValueAtTime(0.001, t2 + 0.18);
      osc2.connect(gain2);
      gain2.connect(audioCtx.destination);
      osc2.start();
      osc2.stop(t2 + 0.18);
    }, 30);
  }

  // Descending slide (Cancel/Back SFX)
  function playCancel() {
    if (!audioCtx) return;
    if (audioCtx.state === 'suspended') audioCtx.resume();

    const t = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    
    osc.type = 'sine';
    osc.frequency.setValueAtTime(587.33, t); // D5
    osc.frequency.linearRampToValueAtTime(196.00, t + 0.15); // G3
    
    gain.gain.setValueAtTime(0.05, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.16);
    
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    
    osc.start();
    osc.stop(t + 0.16);
  }

  // Noise-like frequency sweep (Swoosh SFX for overlays)
  function playSwoosh() {
    if (!audioCtx) return;
    if (audioCtx.state === 'suspended') audioCtx.resume();

    const t = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const filter = audioCtx.createBiquadFilter();
    const gain = audioCtx.createGain();

    osc.type = 'triangle';
    osc.frequency.setValueAtTime(100, t);
    osc.frequency.exponentialRampToValueAtTime(320, t + 0.25);

    filter.type = 'bandpass';
    filter.Q.value = 1.8;
    filter.frequency.setValueAtTime(200, t);
    filter.frequency.exponentialRampToValueAtTime(1000, t + 0.25);

    gain.gain.setValueAtTime(0.04, t);
    gain.gain.linearRampToValueAtTime(0.001, t + 0.25);

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(audioCtx.destination);

    osc.start();
    osc.stop(t + 0.25);
  }

  // --- BACKGROUND MUSIC PLAYER ---

  function toggleBGM() {
    initAudio();
    if (!bgmAudio) return;

    const playBtn = document.getElementById('bgmPlayBtn');
    const trackTicker = document.getElementById('bgmTrackTicker');

    if (isPlaying) {
      bgmAudio.pause();
      isPlaying = false;
      if (playBtn) playBtn.innerHTML = '▶';
      if (trackTicker) trackTicker.classList.remove('scrolling');
    } else {
      bgmAudio.play()
        .then(() => {
          isPlaying = true;
          if (playBtn) playBtn.innerHTML = '⏸';
          if (trackTicker) trackTicker.classList.add('scrolling');
        })
        .catch(err => {
          console.warn("Autoplay blocked or stream fail:", err);
        });
    }
  }

  function changeVolume(volumeVal) {
    currentVolume = parseFloat(volumeVal);
    localStorage.setItem('rc-bgm-volume', currentVolume);
    if (bgmAudio) {
      bgmAudio.volume = currentVolume;
    }
  }

  function changeTrack(direction) {
    initAudio();
    if (!bgmAudio) return;

    currentTrackIdx = (currentTrackIdx + direction + playlist.length) % playlist.length;
    
    // Smooth transition
    const wasPlaying = isPlaying;
    
    bgmAudio.pause();
    bgmAudio.src = playlist[currentTrackIdx].url;
    bgmAudio.load();

    // Update UI Ticker
    const tickerText = document.getElementById('bgmTrackName');
    if (tickerText) {
      tickerText.textContent = playlist[currentTrackIdx].title;
    }

    if (wasPlaying) {
      bgmAudio.play()
        .then(() => {
          isPlaying = true;
        })
        .catch(err => {
          console.warn("Track failed to play:", err);
          isPlaying = false;
          const playBtn = document.getElementById('bgmPlayBtn');
          if (playBtn) playBtn.innerHTML = '▶';
        });
    }
  }

  // --- AUTO BINDING INTERACTIVE SFX ---
  function bindSFX() {
    // 1. Hover SFX
    const hoverElements = document.querySelectorAll(
      'a, button, input[type="submit"], input[type="button"], select, .p5-option-btn, .theme-toggle, .btn, .card, .card-glass, .nav-avatar'
    );
    hoverElements.forEach(el => {
      el.addEventListener('mouseenter', () => {
        if (audioCtx) playHover();
      });
    });

    // 2. Confirm SFX
    const confirmElements = document.querySelectorAll(
      'button, input[type="submit"], input[type="button"], .p5-option-btn, .btn-primary'
    );
    confirmElements.forEach(el => {
      // Exclude back/cancel styled buttons
      if (
        el.classList.contains('btn-cancel') || 
        el.innerText.toLowerCase().includes('cancel') ||
        el.innerText.toLowerCase().includes('skip') ||
        el.innerText.toLowerCase().includes('back')
      ) {
        return;
      }
      el.addEventListener('click', () => {
        initAudio();
        if (audioCtx) playConfirm();
      });
    });

    // 3. Cancel SFX
    const cancelElements = document.querySelectorAll(
      '.btn-cancel, [data-action="cancel"], [data-action="close"], .btn-ghost'
    );
    cancelElements.forEach(el => {
      el.addEventListener('click', () => {
        initAudio();
        if (audioCtx) playCancel();
      });
    });

    // Also scan for words like "Cancel" or "Back" or "Skip" in button text
    document.querySelectorAll('button, a.btn').forEach(el => {
      const text = el.innerText.toLowerCase();
      if (text.includes('cancel') || text.includes('back') || text.includes('skip')) {
        el.addEventListener('click', () => {
          initAudio();
          if (audioCtx) playCancel();
        });
      }
    });

    // 4. Input Focus SFX (Subtle tick)
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea');
    inputs.forEach(el => {
      el.addEventListener('focus', () => {
        initAudio();
        if (audioCtx) playHover();
      });
    });
  }

  // --- DOM Ready Hook ---
  document.addEventListener('DOMContentLoaded', () => {
    // Expose AudioManager globally so other scripts can play sound effects manually
    window.AudioManager = {
      init: initAudio,
      playHover,
      playConfirm,
      playCancel,
      playSwoosh,
      toggleBGM,
      changeTrack,
      changeVolume,
      getPlaylist: () => playlist,
      getCurrentTrack: () => playlist[currentTrackIdx]
    };

    // Initialize bindings
    bindSFX();

    // Trigger swoosh when elements with transition animations appear
    const p5Container = document.getElementById('p5-tutorial-container');
    if (p5Container) {
      // Watch for active class change to play swoosh
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.attributeName === 'class') {
            if (p5Container.classList.contains('active')) {
              setTimeout(() => {
                if (audioCtx) playSwoosh();
              }, 100);
            }
          }
        });
      });
      observer.observe(p5Container, { attributes: true });
    }

    // Set up navbar BGM control event listeners
    const playBtn = document.getElementById('bgmPlayBtn');
    const prevBtn = document.getElementById('bgmPrevBtn');
    const nextBtn = document.getElementById('bgmNextBtn');
    const volSlider = document.getElementById('bgmVolSlider');
    const tickerText = document.getElementById('bgmTrackName');

    if (playBtn) playBtn.addEventListener('click', toggleBGM);
    if (prevBtn) prevBtn.addEventListener('click', () => changeTrack(-1));
    if (nextBtn) nextBtn.addEventListener('click', () => changeTrack(1));
    if (volSlider) {
      volSlider.value = currentVolume;
      volSlider.addEventListener('input', (e) => changeVolume(e.target.value));
    }
    if (tickerText) {
      tickerText.textContent = playlist[currentTrackIdx].title;
    }

    // Bind document click once to unlock audio engine safely
    document.body.addEventListener('click', () => {
      initAudio();
    }, { once: true });
  });

})();
