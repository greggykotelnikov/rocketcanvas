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

  // Real SFX from Fantasy UI SFX pack
  const sfxHover = new Audio("/static/sounds/fantasy-sfx/Fantasy UI SFX/Fantasy/Fantasy_UI (1).wav");
  const sfxConfirm = new Audio("/static/sounds/fantasy-sfx/Fantasy UI SFX/Fantasy/Fantasy_UI (11).wav");
  const sfxCancel = new Audio("/static/sounds/fantasy-sfx/Fantasy UI SFX/Fantasy/Fantasy_UI (12).wav");

  // Track list
  const playlist = [
  {
    "title": "A Long Winter",
    "url": "/static/sounds/bgm/a long winter.ogg",
    "source": "local"
  },
  {
    "title": "Android Nightmares",
    "url": "/static/sounds/bgm/android nightmares.ogg",
    "source": "local"
  },
  {
    "title": "Astral House",
    "url": "/static/sounds/bgm/astral house.ogg",
    "source": "local"
  },
  {
    "title": "Back To Reality",
    "url": "/static/sounds/bgm/back to reality.ogg",
    "source": "local"
  },
  {
    "title": "Birth",
    "url": "/static/sounds/bgm/birth.ogg",
    "source": "local"
  },
  {
    "title": "Bleepinblooper",
    "url": "/static/sounds/bgm/bleepinblooper.ogg",
    "source": "local"
  },
  {
    "title": "Break Time",
    "url": "/static/sounds/bgm/break time.ogg",
    "source": "local"
  },
  {
    "title": "Breakdown",
    "url": "/static/sounds/bgm/breakdown.ogg",
    "source": "local"
  },
  {
    "title": "Broken Traces",
    "url": "/static/sounds/bgm/broken traces.ogg",
    "source": "local"
  },
  {
    "title": "Call To War",
    "url": "/static/sounds/bgm/call to war.ogg",
    "source": "local"
  },
  {
    "title": "Cascading Collapse",
    "url": "/static/sounds/bgm/cascading collapse.ogg",
    "source": "local"
  },
  {
    "title": "Circuit Breaker",
    "url": "/static/sounds/bgm/circuit breaker.ogg",
    "source": "local"
  },
  {
    "title": "Contest",
    "url": "/static/sounds/bgm/contest.ogg",
    "source": "local"
  },
  {
    "title": "Crystallize",
    "url": "/static/sounds/bgm/crystallize.ogg",
    "source": "local"
  },
  {
    "title": "Cubical Void",
    "url": "/static/sounds/bgm/cubical void.ogg",
    "source": "local"
  },
  {
    "title": "Cut Chords",
    "url": "/static/sounds/bgm/cut chords.ogg",
    "source": "local"
  },
  {
    "title": "Deserters",
    "url": "/static/sounds/bgm/deserters.ogg",
    "source": "local"
  },
  {
    "title": "Distorted Future",
    "url": "/static/sounds/bgm/distorted future.ogg",
    "source": "local"
  },
  {
    "title": "Djinnboxing",
    "url": "/static/sounds/bgm/djinnboxing.ogg",
    "source": "local"
  },
  {
    "title": "Factorial",
    "url": "/static/sounds/bgm/factorial.ogg",
    "source": "local"
  },
  {
    "title": "Fiber Optics",
    "url": "/static/sounds/bgm/fiber optics.ogg",
    "source": "local"
  },
  {
    "title": "Floaty",
    "url": "/static/sounds/bgm/floaty.ogg",
    "source": "local"
  },
  {
    "title": "Getting There",
    "url": "/static/sounds/bgm/getting there.ogg",
    "source": "local"
  },
  {
    "title": "High Impedance",
    "url": "/static/sounds/bgm/high impedance.ogg",
    "source": "local"
  },
  {
    "title": "Hypnotic",
    "url": "/static/sounds/bgm/hypnotic.ogg",
    "source": "local"
  },
  {
    "title": "I Dont Know This Song",
    "url": "/static/sounds/bgm/i dont know this song.ogg",
    "source": "local"
  },
  {
    "title": "Im The Piano Man",
    "url": "/static/sounds/bgm/im the piano man.ogg",
    "source": "local"
  },
  {
    "title": "In Search Of Something More",
    "url": "/static/sounds/bgm/in search of something more.ogg",
    "source": "local"
  },
  {
    "title": "Industrial",
    "url": "/static/sounds/bgm/industrial.ogg",
    "source": "local"
  },
  {
    "title": "Intermission",
    "url": "/static/sounds/bgm/intermission.ogg",
    "source": "local"
  },
  {
    "title": "Kve\u00f0ja",
    "url": "/static/sounds/bgm/kve\u00f0ja.ogg",
    "source": "local"
  },
  {
    "title": "Land Of The Rising Moon",
    "url": "/static/sounds/bgm/land of the rising moon.ogg",
    "source": "local"
  },
  {
    "title": "Lights Out",
    "url": "/static/sounds/bgm/lights out.ogg",
    "source": "local"
  },
  {
    "title": "Liquid Horizon",
    "url": "/static/sounds/bgm/liquid horizon.ogg",
    "source": "local"
  },
  {
    "title": "Lo Fidelity",
    "url": "/static/sounds/bgm/lo fidelity.ogg",
    "source": "local"
  },
  {
    "title": "Lobby Time",
    "url": "/static/sounds/bgm/lobby time.ogg",
    "source": "local"
  },
  {
    "title": "Loss",
    "url": "/static/sounds/bgm/loss.ogg",
    "source": "local"
  },
  {
    "title": "Madness",
    "url": "/static/sounds/bgm/madness.ogg",
    "source": "local"
  },
  {
    "title": "Melodies",
    "url": "/static/sounds/bgm/melodies.ogg",
    "source": "local"
  },
  {
    "title": "Messy Violin",
    "url": "/static/sounds/bgm/messy violin.ogg",
    "source": "local"
  },
  {
    "title": "Mirror",
    "url": "/static/sounds/bgm/mirror.ogg",
    "source": "local"
  },
  {
    "title": "New Age",
    "url": "/static/sounds/bgm/new age.ogg",
    "source": "local"
  },
  {
    "title": "Ocean Staring Music",
    "url": "/static/sounds/bgm/ocean staring music.ogg",
    "source": "local"
  },
  {
    "title": "Ominous March",
    "url": "/static/sounds/bgm/ominous march.ogg",
    "source": "local"
  },
  {
    "title": "On My Own",
    "url": "/static/sounds/bgm/on my own.ogg",
    "source": "local"
  },
  {
    "title": "Organic",
    "url": "/static/sounds/bgm/organic.ogg",
    "source": "local"
  },
  {
    "title": "Phase Shift",
    "url": "/static/sounds/bgm/phase shift.ogg",
    "source": "local"
  },
  {
    "title": "Power Supply",
    "url": "/static/sounds/bgm/power supply.ogg",
    "source": "local"
  },
  {
    "title": "Protoboard",
    "url": "/static/sounds/bgm/protoboard.ogg",
    "source": "local"
  },
  {
    "title": "Real Trees",
    "url": "/static/sounds/bgm/real trees.ogg",
    "source": "local"
  },
  {
    "title": "Reawakening",
    "url": "/static/sounds/bgm/reawakening.ogg",
    "source": "local"
  },
  {
    "title": "Religious Respite",
    "url": "/static/sounds/bgm/religious respite.ogg",
    "source": "local"
  },
  {
    "title": "Requinox",
    "url": "/static/sounds/bgm/requinox.ogg",
    "source": "local"
  },
  {
    "title": "Research Materials",
    "url": "/static/sounds/bgm/research materials.ogg",
    "source": "local"
  },
  {
    "title": "Respiratory System",
    "url": "/static/sounds/bgm/respiratory system.ogg",
    "source": "local"
  },
  {
    "title": "Rising Up Again",
    "url": "/static/sounds/bgm/rising up again.ogg",
    "source": "local"
  },
  {
    "title": "Rocks Fall",
    "url": "/static/sounds/bgm/rocks fall.ogg",
    "source": "local"
  },
  {
    "title": "Sad Intro Extended",
    "url": "/static/sounds/bgm/sad intro extended.ogg",
    "source": "local"
  },
  {
    "title": "Sad Intro",
    "url": "/static/sounds/bgm/sad intro.ogg",
    "source": "local"
  },
  {
    "title": "Scrap Surfin",
    "url": "/static/sounds/bgm/scrap surfin.ogg",
    "source": "local"
  },
  {
    "title": "Seize The Means",
    "url": "/static/sounds/bgm/seize the means.ogg",
    "source": "local"
  },
  {
    "title": "Sewage Waterfalls",
    "url": "/static/sounds/bgm/sewage waterfalls.ogg",
    "source": "local"
  },
  {
    "title": "Shopping Spree",
    "url": "/static/sounds/bgm/shopping spree.ogg",
    "source": "local"
  },
  {
    "title": "Shouts",
    "url": "/static/sounds/bgm/shouts.ogg",
    "source": "local"
  },
  {
    "title": "Slow Down",
    "url": "/static/sounds/bgm/slow down.ogg",
    "source": "local"
  },
  {
    "title": "Sneaky Piano",
    "url": "/static/sounds/bgm/sneaky piano.ogg",
    "source": "local"
  },
  {
    "title": "Space Mission",
    "url": "/static/sounds/bgm/space mission.ogg",
    "source": "local"
  },
  {
    "title": "Staccato Time",
    "url": "/static/sounds/bgm/staccato time.ogg",
    "source": "local"
  },
  {
    "title": "The Bell Tolls",
    "url": "/static/sounds/bgm/the bell tolls.ogg",
    "source": "local"
  },
  {
    "title": "The Climb",
    "url": "/static/sounds/bgm/the climb.ogg",
    "source": "local"
  },
  {
    "title": "The Future Is Now",
    "url": "/static/sounds/bgm/the future is now.ogg",
    "source": "local"
  },
  {
    "title": "The Venture Below",
    "url": "/static/sounds/bgm/the venture below.ogg",
    "source": "local"
  },
  {
    "title": "Three Hours",
    "url": "/static/sounds/bgm/three hours.ogg",
    "source": "local"
  },
  {
    "title": "Threes",
    "url": "/static/sounds/bgm/threes.ogg",
    "source": "local"
  },
  {
    "title": "To The Top",
    "url": "/static/sounds/bgm/to the top.ogg",
    "source": "local"
  },
  {
    "title": "Tremolo Time",
    "url": "/static/sounds/bgm/tremolo time.ogg",
    "source": "local"
  },
  {
    "title": "Untitled2x",
    "url": "/static/sounds/bgm/untitled2x.ogg",
    "source": "local"
  },
  {
    "title": "Weight Of The World",
    "url": "/static/sounds/bgm/weight of the world.ogg",
    "source": "local"
  },
  {
    "title": "When They Fall",
    "url": "/static/sounds/bgm/when they fall.ogg",
    "source": "local"
  },
  {
    "title": "Whispers",
    "url": "/static/sounds/bgm/whispers.ogg",
    "source": "local"
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

  function playHoverProcedural() {
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

  function playConfirmProcedural() {
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

  function playCancelProcedural() {
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

  // Snappy hover sound
  function playHover() {
    const now = Date.now();
    if (now - lastHoverTime < HOVER_LIMIT_MS) return;
    lastHoverTime = now;

    try {
      sfxHover.currentTime = 0;
      sfxHover.volume = currentVolume * 0.4;
      sfxHover.play().catch(() => playHoverProcedural());
    } catch (e) {
      playHoverProcedural();
    }
  }

  // Confirm SFX
  function playConfirm() {
    try {
      sfxConfirm.currentTime = 0;
      sfxConfirm.volume = currentVolume * 0.8;
      sfxConfirm.play().catch(() => playConfirmProcedural());
    } catch (e) {
      playConfirmProcedural();
    }
  }

  // Cancel/Back SFX
  function playCancel() {
    try {
      sfxCancel.currentTime = 0;
      sfxCancel.volume = currentVolume * 0.8;
      sfxCancel.play().catch(() => playCancelProcedural());
    } catch (e) {
      playCancelProcedural();
    }
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
      if (playBtn) playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>';
      if (trackTicker) trackTicker.classList.remove('scrolling');
    } else {
      bgmAudio.play()
        .then(() => {
          isPlaying = true;
          if (playBtn) playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>';
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
          if (playBtn) playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>';
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
