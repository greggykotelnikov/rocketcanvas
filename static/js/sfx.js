/**
 * RocketCanvas SFX & BGM Manager
 * Persistent music player that survives page navigation, auto-advancing playlist,
 * Fantasy UI SFX, and tutorial volume ducking.
 */

(function () {
  // Web Audio Context
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  let audioCtx = null;

  // Track the BGM element. State persisted in localStorage across page loads
  let bgmAudio = null;
  let isPlaying = false;
  let currentTrackIdx = parseInt(localStorage.getItem('rc-bgm-track') || '0', 10);
  let currentVolume = parseFloat(localStorage.getItem('rc-bgm-volume') || '0.5');
  let lastTimeSave = 0;
  let timeListenersBound = false;

  function getPageEndpoint() {
    return document.body?.dataset?.page || '';
  }

  function shouldAutoStartBGM() {
    const saved = localStorage.getItem('rc-bgm-playing');
    if (saved === '1') return true;
    if (saved === '0') return false;
    const page = getPageEndpoint();
    return page === 'login' || page === 'register' || page === 'garage';
  }

  function saveBGMTime() {
    if (!bgmAudio || !isPlaying) return;
    localStorage.setItem('rc-bgm-time', String(bgmAudio.currentTime));
    localStorage.setItem('rc-bgm-time-track', String(currentTrackIdx));
  }

  function clearBGMTime() {
    localStorage.removeItem('rc-bgm-time');
    localStorage.removeItem('rc-bgm-time-track');
  }

  function restoreBGMTime() {
    if (!bgmAudio) return;
    const savedTrack = parseInt(localStorage.getItem('rc-bgm-time-track') || '-1', 10);
    const savedTime = parseFloat(localStorage.getItem('rc-bgm-time') || '0');
    if (savedTrack !== currentTrackIdx || savedTime <= 0) return;

    const applyTime = () => {
      if (savedTime < bgmAudio.duration) {
        bgmAudio.currentTime = savedTime;
      }
    };

    if (bgmAudio.readyState >= 1) {
      applyTime();
    } else {
      bgmAudio.addEventListener('loadedmetadata', applyTime, { once: true });
    }
  }

  function bindBGMTimeListeners() {
    if (!bgmAudio || timeListenersBound) return;
    timeListenersBound = true;

    bgmAudio.addEventListener('timeupdate', () => {
      const now = Date.now();
      if (now - lastTimeSave < 2000) return;
      lastTimeSave = now;
      saveBGMTime();
    });

    const flushTime = () => saveBGMTime();
    window.addEventListener('pagehide', flushTime);
    window.addEventListener('beforeunload', flushTime);
  }

  // Rate limiting for hover sounds to keep it clean and professional
  let lastHoverTime = 0;
  const HOVER_LIMIT_MS = 90;

  // Fantasy UI SFX (primary sounds, with procedural fallbacks)
  const sfxHover   = new Audio('/static/sounds/fantasy-sfx/Fantasy/Fantasy_UI (1).wav');
  const sfxConfirm = new Audio('/static/sounds/fantasy-sfx/Fantasy/Fantasy_UI (11).wav');
  const sfxCancel  = new Audio('/static/sounds/fantasy-sfx/Fantasy/Fantasy_UI (12).wav');
  const sfxSwoosh  = new Audio('/static/sounds/fantasy-sfx/Fantasy/Fantasy_UI (10).wav');
  const sfxBlip    = new Audio('/static/sounds/fantasy-sfx/Fantasy/Fantasy_UI (60).wav');

  // Preload at low volume to avoid jarring first play
  [sfxHover, sfxConfirm, sfxCancel, sfxSwoosh, sfxBlip].forEach(s => {
    s.volume = 0;
    s.play().catch(() => {}); // Attempt to prime the audio pipeline
    s.pause();
    s.currentTime = 0;
    s.volume = 1;
  });

  // Track list
  const playlist = [
  {
    "title": "A Long Winter",
    "url": "/static/sounds/bgm/a long winter.ogg"
  },
  {
    "title": "Android Nightmares",
    "url": "/static/sounds/bgm/android nightmares.ogg"
  },
  {
    "title": "Astral House",
    "url": "/static/sounds/bgm/astral house.ogg"
  },
  {
    "title": "Back To Reality",
    "url": "/static/sounds/bgm/back to reality.ogg"
  },
  {
    "title": "Birth",
    "url": "/static/sounds/bgm/birth.ogg"
  },
  {
    "title": "Bleepinblooper",
    "url": "/static/sounds/bgm/bleepinblooper.ogg"
  },
  {
    "title": "Break Time",
    "url": "/static/sounds/bgm/break time.ogg"
  },
  {
    "title": "Breakdown",
    "url": "/static/sounds/bgm/breakdown.ogg"
  },
  {
    "title": "Broken Traces",
    "url": "/static/sounds/bgm/broken traces.ogg"
  },
  {
    "title": "Call To War",
    "url": "/static/sounds/bgm/call to war.ogg"
  },
  {
    "title": "Cascading Collapse",
    "url": "/static/sounds/bgm/cascading collapse.ogg"
  },
  {
    "title": "Circuit Breaker",
    "url": "/static/sounds/bgm/circuit breaker.ogg"
  },
  {
    "title": "Contest",
    "url": "/static/sounds/bgm/contest.ogg"
  },
  {
    "title": "Crystallize",
    "url": "/static/sounds/bgm/crystallize.ogg"
  },
  {
    "title": "Cubical Void",
    "url": "/static/sounds/bgm/cubical void.ogg"
  },
  {
    "title": "Cut Chords",
    "url": "/static/sounds/bgm/cut chords.ogg"
  },
  {
    "title": "Deserters",
    "url": "/static/sounds/bgm/deserters.ogg"
  },
  {
    "title": "Distorted Future",
    "url": "/static/sounds/bgm/distorted future.ogg"
  },
  {
    "title": "Djinnboxing",
    "url": "/static/sounds/bgm/djinnboxing.ogg"
  },
  {
    "title": "Factorial",
    "url": "/static/sounds/bgm/factorial.ogg"
  },
  {
    "title": "Fiber Optics",
    "url": "/static/sounds/bgm/fiber optics.ogg"
  },
  {
    "title": "Floaty",
    "url": "/static/sounds/bgm/floaty.ogg"
  },
  {
    "title": "Getting There",
    "url": "/static/sounds/bgm/getting there.ogg"
  },
  {
    "title": "High Impedance",
    "url": "/static/sounds/bgm/high impedance.ogg"
  },
  {
    "title": "Hypnotic",
    "url": "/static/sounds/bgm/hypnotic.ogg"
  },
  {
    "title": "I Dont Know This Song",
    "url": "/static/sounds/bgm/i dont know this song.ogg"
  },
  {
    "title": "Im The Piano Man",
    "url": "/static/sounds/bgm/im the piano man.ogg"
  },
  {
    "title": "In Search Of Something More",
    "url": "/static/sounds/bgm/in search of something more.ogg"
  },
  {
    "title": "Industrial",
    "url": "/static/sounds/bgm/industrial.ogg"
  },
  {
    "title": "Intermission",
    "url": "/static/sounds/bgm/intermission.ogg"
  },
  {
    "title": "Kveðja",
    "url": "/static/sounds/bgm/kveðja.ogg"
  },
  {
    "title": "Land Of The Rising Moon",
    "url": "/static/sounds/bgm/land of the rising moon.ogg"
  },
  {
    "title": "Lights Out",
    "url": "/static/sounds/bgm/lights out.ogg"
  },
  {
    "title": "Liquid Horizon",
    "url": "/static/sounds/bgm/liquid horizon.ogg"
  },
  {
    "title": "Lo Fidelity",
    "url": "/static/sounds/bgm/lo fidelity.ogg"
  },
  {
    "title": "Lobby Time",
    "url": "/static/sounds/bgm/lobby time.ogg"
  },
  {
    "title": "Loss",
    "url": "/static/sounds/bgm/loss.ogg"
  },
  {
    "title": "Madness",
    "url": "/static/sounds/bgm/madness.ogg"
  },
  {
    "title": "Melodies",
    "url": "/static/sounds/bgm/melodies.ogg"
  },
  {
    "title": "Messy Violin",
    "url": "/static/sounds/bgm/messy violin.ogg"
  },
  {
    "title": "Mirror",
    "url": "/static/sounds/bgm/mirror.ogg"
  },
  {
    "title": "New Age",
    "url": "/static/sounds/bgm/new age.ogg"
  },
  {
    "title": "Ocean Staring Music",
    "url": "/static/sounds/bgm/ocean staring music.ogg"
  },
  {
    "title": "Ominous March",
    "url": "/static/sounds/bgm/ominous march.ogg"
  },
  {
    "title": "On My Own",
    "url": "/static/sounds/bgm/on my own.ogg"
  },
  {
    "title": "Organic",
    "url": "/static/sounds/bgm/organic.ogg"
  },
  {
    "title": "Phase Shift",
    "url": "/static/sounds/bgm/phase shift.ogg"
  },
  {
    "title": "Power Supply",
    "url": "/static/sounds/bgm/power supply.ogg"
  },
  {
    "title": "Protoboard",
    "url": "/static/sounds/bgm/protoboard.ogg"
  },
  {
    "title": "Real Trees",
    "url": "/static/sounds/bgm/real trees.ogg"
  },
  {
    "title": "Reawakening",
    "url": "/static/sounds/bgm/reawakening.ogg"
  },
  {
    "title": "Religious Respite",
    "url": "/static/sounds/bgm/religious respite.ogg"
  },
  {
    "title": "Requinox",
    "url": "/static/sounds/bgm/requinox.ogg"
  },
  {
    "title": "Research Materials",
    "url": "/static/sounds/bgm/research materials.ogg"
  },
  {
    "title": "Respiratory System",
    "url": "/static/sounds/bgm/respiratory system.ogg"
  },
  {
    "title": "Rising Up Again",
    "url": "/static/sounds/bgm/rising up again.ogg"
  },
  {
    "title": "Rocks Fall",
    "url": "/static/sounds/bgm/rocks fall.ogg"
  },
  {
    "title": "Sad Intro Extended",
    "url": "/static/sounds/bgm/sad intro extended.ogg"
  },
  {
    "title": "Sad Intro",
    "url": "/static/sounds/bgm/sad intro.ogg"
  },
  {
    "title": "Scrap Surfin",
    "url": "/static/sounds/bgm/scrap surfin.ogg"
  },
  {
    "title": "Seize The Means",
    "url": "/static/sounds/bgm/seize the means.ogg"
  },
  {
    "title": "Sewage Waterfalls",
    "url": "/static/sounds/bgm/sewage waterfalls.ogg"
  },
  {
    "title": "Shopping Spree",
    "url": "/static/sounds/bgm/shopping spree.ogg"
  },
  {
    "title": "Shouts",
    "url": "/static/sounds/bgm/shouts.ogg"
  },
  {
    "title": "Slow Down",
    "url": "/static/sounds/bgm/slow down.ogg"
  },
  {
    "title": "Sneaky Piano",
    "url": "/static/sounds/bgm/sneaky piano.ogg"
  },
  {
    "title": "Space Mission",
    "url": "/static/sounds/bgm/space mission.ogg"
  },
  {
    "title": "Staccato Time",
    "url": "/static/sounds/bgm/staccato time.ogg"
  },
  {
    "title": "The Bell Tolls",
    "url": "/static/sounds/bgm/the bell tolls.ogg"
  },
  {
    "title": "The Climb",
    "url": "/static/sounds/bgm/the climb.ogg"
  },
  {
    "title": "The Future Is Now",
    "url": "/static/sounds/bgm/the future is now.ogg"
  },
  {
    "title": "The Venture Below",
    "url": "/static/sounds/bgm/the venture below.ogg"
  },
  {
    "title": "Three Hours",
    "url": "/static/sounds/bgm/three hours.ogg"
  },
  {
    "title": "Threes",
    "url": "/static/sounds/bgm/threes.ogg"
  },
  {
    "title": "To The Top",
    "url": "/static/sounds/bgm/to the top.ogg"
  },
  {
    "title": "Tremolo Time",
    "url": "/static/sounds/bgm/tremolo time.ogg"
  },
  {
    "title": "Untitled2x",
    "url": "/static/sounds/bgm/untitled2x.ogg"
  },
  {
    "title": "Weight Of The World",
    "url": "/static/sounds/bgm/weight of the world.ogg"
  },
  {
    "title": "When They Fall",
    "url": "/static/sounds/bgm/when they fall.ogg"
  },
  {
    "title": "Whispers",
    "url": "/static/sounds/bgm/whispers.ogg"
  }
];

  // ── VOLUME DUCKING ───────────────────────────────────────────────────
  // The tutorial can call duckBGM()/unduckBGM() to smoothly reduce volume
  const DUCK_VOLUME_RATIO = 0.25; // 25% of current volume during dialogue
  let isDucked = false;
  let duckTimer = null;

  function duckBGM() {
    if (!bgmAudio || isDucked) return;
    isDucked = true;
    const target = currentVolume * DUCK_VOLUME_RATIO;
    fadeBGMVolume(target, 600);
  }

  function unduckBGM() {
    if (!bgmAudio || !isDucked) return;
    isDucked = false;
    fadeBGMVolume(currentVolume, 800);
  }

  function fadeBGMVolume(targetVol, durationMs) {
    if (!bgmAudio) return;
    const start = bgmAudio.volume;
    const diff = targetVol - start;
    const steps = 30;
    const interval = durationMs / steps;
    let step = 0;
    clearInterval(duckTimer);
    duckTimer = setInterval(() => {
      step++;
      bgmAudio.volume = Math.max(0, Math.min(1, start + diff * (step / steps)));
      if (step >= steps) clearInterval(duckTimer);
    }, interval);
  }

  // ── AUDIO CONTEXT ────────────────────────────────────────────────────
  function initAudio() {
    if (!audioCtx) {
      audioCtx = new AudioContextClass();
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }

    // Initialise BGM element if not done yet
    if (!bgmAudio) {
      bgmAudio = new Audio();
      bgmAudio.loop = false; // We handle looping manually to enable auto-advance
      bgmAudio.volume = currentVolume;
      bgmAudio.src = playlist[currentTrackIdx].url;

      // ── AUTO-ADVANCE when a track ends ──────────────────────────────
      bgmAudio.addEventListener('ended', () => {
        isPlaying = true;
        clearBGMTime();
        advanceTrack(1);
      });

      bindBGMTimeListeners();

      bgmAudio.addEventListener('error', (e) => {
        console.warn('BGM Stream failed to load or was interrupted:', e);
        // Try to skip to next track on error
        setTimeout(() => advanceTrack(1), 500);
      });
    }
  }

  // Auto-advance to next track seamlessly
  function advanceTrack(direction) {
    if (!bgmAudio) return;
    currentTrackIdx = (currentTrackIdx + direction + playlist.length) % playlist.length;
    localStorage.setItem('rc-bgm-track', currentTrackIdx);
    clearBGMTime();

    bgmAudio.src = playlist[currentTrackIdx].url;
    bgmAudio.load();

    updateTickerUI();

    if (isPlaying) {
      bgmAudio.play()
        .then(() => {
          localStorage.setItem('rc-bgm-playing', '1');
        })
        .catch(err => console.warn('Track advance failed:', err));
    }
  }

  // ── PROCEDURAL SFX FALLBACKS ─────────────────────────────────────────

  function playHoverProcedural() {
    if (!audioCtx) return;
    const now = Date.now();
    if (now - lastHoverTime < HOVER_LIMIT_MS) return;
    lastHoverTime = now;

    if (audioCtx.state === 'suspended') audioCtx.resume();

    const osc1 = audioCtx.createOscillator();
    const gain1 = audioCtx.createGain();
    osc1.type = 'sine';
    osc1.frequency.setValueAtTime(988, audioCtx.currentTime);
    gain1.gain.setValueAtTime(0.015, audioCtx.currentTime);
    gain1.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.015);
    osc1.connect(gain1);
    gain1.connect(audioCtx.destination);
    osc1.start();
    osc1.stop(audioCtx.currentTime + 0.015);

    setTimeout(() => {
      if (!audioCtx) return;
      const osc2 = audioCtx.createOscillator();
      const gain2 = audioCtx.createGain();
      osc2.type = 'sine';
      osc2.frequency.setValueAtTime(1047, audioCtx.currentTime);
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

    const osc1 = audioCtx.createOscillator();
    const gain1 = audioCtx.createGain();
    osc1.type = 'triangle';
    osc1.frequency.setValueAtTime(659.25, t);
    osc1.frequency.exponentialRampToValueAtTime(1046.50, t + 0.12);
    gain1.gain.setValueAtTime(0.06, t);
    gain1.gain.exponentialRampToValueAtTime(0.001, t + 0.18);
    osc1.connect(gain1);
    gain1.connect(audioCtx.destination);
    osc1.start();
    osc1.stop(t + 0.18);

    setTimeout(() => {
      if (!audioCtx) return;
      const t2 = audioCtx.currentTime;
      const osc2 = audioCtx.createOscillator();
      const gain2 = audioCtx.createGain();
      osc2.type = 'sine';
      osc2.frequency.setValueAtTime(783.99, t2);
      osc2.frequency.exponentialRampToValueAtTime(1318.51, t2 + 0.12);
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
    osc.frequency.setValueAtTime(587.33, t);
    osc.frequency.linearRampToValueAtTime(196.00, t + 0.15);

    gain.gain.setValueAtTime(0.05, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.16);

    osc.connect(gain);
    gain.connect(audioCtx.destination);

    osc.start();
    osc.stop(t + 0.16);
  }

  // ── FANTASY SFX (PRIMARY) ────────────────────────────────────────────

  function playHover() {
    const now = Date.now();
    if (now - lastHoverTime < HOVER_LIMIT_MS) return;
    lastHoverTime = now;

    try {
      sfxHover.currentTime = 0;
      sfxHover.volume = Math.min(1, currentVolume * 0.55);
      sfxHover.play().catch(() => playHoverProcedural());
    } catch (e) {
      playHoverProcedural();
    }
  }

  function playConfirm() {
    try {
      sfxConfirm.currentTime = 0;
      sfxConfirm.volume = Math.min(1, currentVolume * 0.9);
      sfxConfirm.play().catch(() => playConfirmProcedural());
    } catch (e) {
      playConfirmProcedural();
    }
  }

  function playCancel() {
    try {
      sfxCancel.currentTime = 0;
      sfxCancel.volume = Math.min(1, currentVolume * 0.9);
      sfxCancel.play().catch(() => playCancelProcedural());
    } catch (e) {
      playCancelProcedural();
    }
  }

  function playSwoosh() {
    try {
      sfxSwoosh.currentTime = 0;
      sfxSwoosh.volume = Math.min(1, currentVolume * 0.7);
      sfxSwoosh.play().catch(() => {
        // Procedural fallback swoosh
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
      });
    } catch (e) {}
  }

  function playBlip() {
    try {
      sfxBlip.currentTime = 0;
      sfxBlip.volume = Math.min(1, currentVolume * 0.4);
      sfxBlip.play().catch(() => {});
    } catch (e) {}
  }

  // ── BGM PLAYER ────────────────────────────────────────────────────────

  function updateTickerUI() {
    const tickerText = document.getElementById('bgmTrackName');
    const trackTicker = document.getElementById('bgmTrackTicker');
    if (tickerText) tickerText.textContent = playlist[currentTrackIdx].title;
    if (trackTicker) {
      if (isPlaying) {
        trackTicker.classList.add('scrolling');
      } else {
        trackTicker.classList.remove('scrolling');
      }
    }
  }

  function updatePlayBtnUI() {
    const playBtn = document.getElementById('bgmPlayBtn');
    if (!playBtn) return;
    if (isPlaying) {
      playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>';
    } else {
      playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>';
    }
  }

  function toggleBGM() {
    initAudio();
    if (!bgmAudio) return;

    if (isPlaying) {
      bgmAudio.pause();
      isPlaying = false;
      localStorage.setItem('rc-bgm-playing', '0');
    } else {
      bgmAudio.play()
        .then(() => {
          isPlaying = true;
          localStorage.setItem('rc-bgm-playing', '1');
          updateTickerUI();
          updatePlayBtnUI();
        })
        .catch(err => {
          console.warn('Autoplay blocked or stream fail:', err);
        });
    }

    updateTickerUI();
    updatePlayBtnUI();
  }

  // Start music playback (respects autoplay policy; must be called from user gesture context)
  function startBGM() {
    initAudio();
    if (!bgmAudio || isPlaying) return;

    bgmAudio.play()
      .then(() => {
        isPlaying = true;
        localStorage.setItem('rc-bgm-playing', '1');
        updateTickerUI();
        updatePlayBtnUI();
      })
      .catch(err => {
        console.warn('BGM autoplay blocked:', err);
      });
  }

  function changeVolume(volumeVal) {
    currentVolume = parseFloat(volumeVal);
    localStorage.setItem('rc-bgm-volume', currentVolume);
    if (bgmAudio && !isDucked) {
      bgmAudio.volume = currentVolume;
    }
  }

  function changeTrack(direction) {
    initAudio();
    if (!bgmAudio) return;

    const wasPlaying = isPlaying;

    bgmAudio.pause();
    isPlaying = false;

    currentTrackIdx = (currentTrackIdx + direction + playlist.length) % playlist.length;
    localStorage.setItem('rc-bgm-track', currentTrackIdx);
    clearBGMTime();

    bgmAudio.src = playlist[currentTrackIdx].url;
    bgmAudio.load();

    updateTickerUI();

    if (wasPlaying) {
      bgmAudio.play()
        .then(() => {
          isPlaying = true;
          localStorage.setItem('rc-bgm-playing', '1');
          updateTickerUI();
          updatePlayBtnUI();
        })
        .catch(err => {
          console.warn('Track failed to play:', err);
          isPlaying = false;
          updatePlayBtnUI();
        });
    }
  }

  // ── SFX BINDINGS ─────────────────────────────────────────────────────
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

    document.querySelectorAll('button, a.btn').forEach(el => {
      const text = el.innerText.toLowerCase();
      if (text.includes('cancel') || text.includes('back') || text.includes('skip')) {
        el.addEventListener('click', () => {
          initAudio();
          if (audioCtx) playCancel();
        });
      }
    });

    // 4. Input Focus SFX (subtle tick)
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea');
    inputs.forEach(el => {
      el.addEventListener('focus', () => {
        initAudio();
        if (audioCtx) playHover();
      });
    });
  }

  // ── RESTORE PLAYBACK STATE AFTER PAGE NAVIGATION ─────────────────────
  // Because the BGM element is re-created on each page load (browsers don't
  // persist <audio> across navigation), we read localStorage to resume.
  function tryPlayBGM() {
    if (!bgmAudio) return;
    restoreBGMTime();
    bgmAudio.play()
      .then(() => {
        isPlaying = true;
        localStorage.setItem('rc-bgm-playing', '1');
        updateTickerUI();
        updatePlayBtnUI();
      })
      .catch(() => {
        const resume = () => {
          initAudio();
          restoreBGMTime();
          bgmAudio.play()
            .then(() => {
              isPlaying = true;
              localStorage.setItem('rc-bgm-playing', '1');
              updateTickerUI();
              updatePlayBtnUI();
            })
            .catch(() => {});
        };
        document.body.addEventListener('click', resume, { once: true });
        document.body.addEventListener('keydown', resume, { once: true });
      });
  }

  function restorePlaybackState() {
    const savedTrack = parseInt(localStorage.getItem('rc-bgm-track') || '0', 10);
    const wantPlay = shouldAutoStartBGM();

    currentTrackIdx = (savedTrack >= 0 && savedTrack < playlist.length) ? savedTrack : 0;

    initAudio();

    if (bgmAudio) {
      bgmAudio.src = playlist[currentTrackIdx].url;
      bgmAudio.load();
      updateTickerUI();
    }

    if (wantPlay) {
      tryPlayBGM();
    }
  }

  // ── DOM READY ─────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', () => {
    // Expose AudioManager globally so other scripts can play sound effects manually
    window.AudioManager = {
      init: initAudio,
      playHover,
      playConfirm,
      playCancel,
      playSwoosh,
      playBlip,
      toggleBGM,
      startBGM,
      changeTrack,
      changeVolume,
      duckBGM,
      unduckBGM,
      getPlaylist: () => playlist,
      getCurrentTrack: () => playlist[currentTrackIdx]
    };

    // Initialize SFX bindings
    bindSFX();

    // Restore music state from previous page
    restorePlaybackState();

    // Trigger swoosh when tutorial container appears
    const p5Container = document.getElementById('p5-tutorial-container');
    if (p5Container) {
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
    const playBtn    = document.getElementById('bgmPlayBtn');
    const prevBtn    = document.getElementById('bgmPrevBtn');
    const nextBtn    = document.getElementById('bgmNextBtn');
    const volSlider  = document.getElementById('bgmVolSlider');
    const tickerText = document.getElementById('bgmTrackName');

    if (playBtn) playBtn.addEventListener('click', toggleBGM);
    if (prevBtn) prevBtn.addEventListener('click', () => { initAudio(); changeTrack(-1); });
    if (nextBtn) nextBtn.addEventListener('click', () => { initAudio(); changeTrack(1); });
    if (volSlider) {
      volSlider.value = currentVolume;
      volSlider.addEventListener('input', (e) => changeVolume(e.target.value));
    }
    if (tickerText) {
      tickerText.textContent = playlist[currentTrackIdx].title;
    }

    // Sync play button visual to restored state
    updatePlayBtnUI();
  });

})();
