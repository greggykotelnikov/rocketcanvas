function getPageKey(pathname) {
  const path = pathname || window.location.pathname;
  if (path === '/login' || path === '/') return 'login';
  if (path === '/register') return 'register';
  if (path === '/profile') return 'profile';
  if (path === '/dashboard') return 'dashboard';
  if (path === '/gallery') return 'gallery';
  if (path === '/analytics') return 'analytics';
  if (path === '/hitbox' || path === '/hitbox_lookup') return 'hitbox';
  if (path === '/recommend') return 'recommend';
  return null;
}

document.addEventListener('DOMContentLoaded', () => {
  if (new URLSearchParams(window.location.search).get('reset_tutorial') === '1') {
    localStorage.removeItem('rc_tutorial_seen');
    const url = new URL(window.location);
    url.searchParams.delete('reset_tutorial');
    window.history.replaceState({}, '', url);
  }

  const pageKey = getPageKey();
  if (!pageKey) return;

  const force = new URLSearchParams(window.location.search).get('tour') === '1';
  const seenPages = JSON.parse(localStorage.getItem('rc_tutorial_seen') || '{}');
  if (seenPages[pageKey] && !force) {
    bindTourReplayButton(pageKey);
    return;
  }

  startRcTour(pageKey, { force });
});

function bindTourReplayButton(pageKey) {
  const btn = document.getElementById('navTourBtn');
  if (!btn || btn.dataset.bound) return;
  btn.dataset.bound = '1';
  btn.addEventListener('click', () => startRcTour(pageKey, { force: true }));
}

function startRcTour(pageKey, opts = {}) {
  if (!pageKey) pageKey = getPageKey();
  if (!pageKey) return;

  const existing = document.getElementById('p5-tutorial-container');
  if (existing) existing.remove();
  document.getElementById('p5-highlight-mask')?.remove();
  const seenPages = JSON.parse(localStorage.getItem('rc_tutorial_seen') || '{}');
  if (seenPages[pageKey] && !opts.force) return;

  runTour(pageKey, seenPages);
}

window.startRcTour = startRcTour;

function runTour(pageKey, seenPages) {

  // --- Character Config ---
  const characters = {
    octane: {
      name: 'OCTANE',
      img: '/static/images/octane_for_personalikedialogue.png',
      gender: 'male'
    },
    dominus: {
      name: 'DOMINUS',
      img: '/static/images/dominus_for_personalikedialogue.png',
      gender: 'female'
    }
  };

  // Which character speaks on which page
  const pageCharacter = {
    login: 'octane',
    register: 'octane',
    profile: 'octane',
    hitbox: 'octane',
    dashboard: 'dominus',
    gallery: 'dominus',
    analytics: 'dominus',
    recommend: 'dominus'
  };

  const charKey = pageCharacter[pageKey] || 'octane';
  const char = characters[charKey];

  // --- Create Tutorial UI ---
  const tutorialHTML = `
    <div id="p5-highlight-mask"></div>
    <div id="p5-tutorial-container">
      <div class="p5-portrait" id="p5-portrait">
        <img src="${char.img}" alt="${char.name}">
      </div>
      <div class="p5-dialogue-wrapper">
        <div class="p5-name">${char.name}</div>
        <div class="p5-box-bg">
          <div class="p5-text" id="p5-text"></div>
          <div class="p5-options" id="p5-options" style="display:none;"></div>
        </div>
      </div>
    </div>
  `;
  document.body.insertAdjacentHTML('beforeend', tutorialHTML);

  const container = document.getElementById('p5-tutorial-container');
  const textArea = document.getElementById('p5-text');
  const optionsArea = document.getElementById('p5-options');
  const portrait = document.getElementById('p5-portrait');
  const highlightMask = document.getElementById('p5-highlight-mask');
  // --- Voice Loading (prefer natural-sounding system voices) ---
  let femaleVoice = null;
  let maleVoice = null;

  function scoreVoice(v, gender) {
    const n = v.name.toLowerCase();
    const natural = /natural|neural|online/i.test(n) ? 4 : 0;
    const local = v.localService ? 2 : 0;
    if (gender === 'female') {
      if (/jenny|aria|samantha|zira|natasha|hazel|susan|female/i.test(n)) return 10 + natural + local;
      return natural + local;
    }
    if (/guy|ryan|david|mark|george|james|male|christopher/i.test(n)) return 10 + natural + local;
    return natural + local;
  }

  function loadVoices() {
    const voices = window.speechSynthesis.getVoices();
    if (!voices.length) return;
    const en = voices.filter(v => v.lang && v.lang.toLowerCase().startsWith('en'));
    const pool = en.length ? en : voices;
    femaleVoice = pool
      .slice()
      .sort((a, b) => scoreVoice(b, 'female') - scoreVoice(a, 'female'))[0] || null;
    maleVoice = pool
      .slice()
      .sort((a, b) => scoreVoice(b, 'male') - scoreVoice(a, 'male'))[0] || null;
  }

  window.speechSynthesis.onvoiceschanged = loadVoices;
  loadVoices(); // try immediately

  // --- Audio Blips ---
  const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
  let audioCtx = null;

  function ensureAudioCtx() {
    if (!audioCtx) audioCtx = new AudioCtxClass();
    if (audioCtx.state === 'suspended') audioCtx.resume();
  }

  function playBlip() {
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'square';
    // Higher pitch for female character, lower for male
    const baseFreq = char.gender === 'female' ? 600 : 400;
    osc.frequency.setValueAtTime(baseFreq + Math.random() * 50, audioCtx.currentTime);
    gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.05);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.05);
  }

  // --- TTS ---
  let activeUtterances = [];
  function speak(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Ensure voices are loaded if they loaded late
    if (!femaleVoice || !maleVoice) {
      loadVoices();
    }
    
    if (char.gender === 'female' && femaleVoice) {
      utterance.voice = femaleVoice;
      utterance.pitch = 1.02;
    } else if (char.gender === 'male' && maleVoice) {
      utterance.voice = maleVoice;
      utterance.pitch = 0.96;
    }
    utterance.rate = 1.05;
    utterance.volume = 1;
    
    // Prevent garbage collection
    activeUtterances.push(utterance);
    const cleanUp = () => {
      activeUtterances = activeUtterances.filter(u => u !== utterance);
    };
    utterance.onend = cleanUp;
    utterance.onerror = cleanUp;
    
    window.speechSynthesis.speak(utterance);
  }

  // --- Typewriter (ALWAYS speaks) ---
  let typeTimer;

  function typeText(text, callback) {
    textArea.innerHTML = '';
    optionsArea.style.display = 'none';
    portrait.classList.add('talking');
    speak(text); // <-- This is the fix: every line gets spoken

    let i = 0;
    clearInterval(typeTimer);
    typeTimer = setInterval(() => {
      textArea.innerHTML += text.charAt(i);
      playBlip();
      i++;
      if (i >= text.length) {
        clearInterval(typeTimer);
        portrait.classList.remove('talking');
        if (callback) callback();
      }
    }, 30);
  }

  // --- Options ---
  function showOptions(options) {
    optionsArea.innerHTML = '';
    optionsArea.style.display = 'flex';
    options.forEach(opt => {
      const btn = document.createElement('button');
      btn.className = 'p5-option-btn';
      btn.textContent = opt.text;
      btn.onclick = () => {
        ensureAudioCtx();
        opt.action();
      };
      optionsArea.appendChild(btn);
    });
  }

  // --- Finish ---
  function finishTutorial() {
    seenPages[pageKey] = true;
    localStorage.setItem('rc_tutorial_seen', JSON.stringify(seenPages));
    container.classList.remove('active');
    highlightMask.classList.remove('active');
    bindTourReplayButton(pageKey);
  }

  // Helper: chain multiple lines then show options
  function chainLines(lines, optionsToShow) {
    if (lines.length === 0) {
      if (optionsToShow) showOptions(optionsToShow);
      return;
    }
    const [first, ...rest] = lines;
    typeText(first, () => {
      setTimeout(() => chainLines(rest, optionsToShow), 800);
    });
  }

  // ============================================================
  //  DIALOGUE FLOWS
  // ============================================================

  const Flows = {

    // --- LOGIN (Octane, male) ---
    login: () => {
      chainLines([
        "Hey! I'm Octane — welcome to RocketCanvas.",
        "This is your Rocket League stats hub: search players, track replays on the Dashboard, and dig into charts on Analytics.",
        "We also have a community Gallery for car designs and a Hitbox page to look up any car's hitbox class.",
        "Sign in below and we'll get your profile set up."
      ], [
        { text: "Sounds awesome!", action: finishTutorial },
        { text: "What can I do here?", action: () => {
          chainLines([
            "After login you get Dashboard stats, deep Analytics, the design Gallery, and Hitbox lookup.",
            "Link your RL username on Profile so searches are faster. Let's go!"
          ], [
            { text: "Let's go!", action: finishTutorial }
          ]);
        }}
      ]);
    },

    // --- REGISTER (Octane, male) ---
    register: () => {
      chainLines([
        "Yo! Ready to join RocketCanvas?",
        "Track win rates, browse the community gallery, and look up hitbox types for any car — Octane included, obviously.",
        "Fill in your details below and we'll send you a quick verification code."
      ], [
        { text: "Let's do it!", action: finishTutorial },
        { text: "What data do you collect?", action: () => {
          chainLines([
            "We only store your Rocket League ID and your uploaded designs. Your privacy matters to us!",
            "No sketchy stuff, I promise."
          ], [
            { text: "Fair enough!", action: finishTutorial }
          ]);
        }}
      ]);
    },

    // --- DASHBOARD (Dominus, female) ---
    dashboard: () => {
      chainLines([
        "Welcome to the Dashboard! This is your command center."
      ], [
        { text: "What do I do here?", action: () => {
          chainLines([
            "You can track your recent matches, see your linked account stats, and monitor your performance over time.",
            "Think of it as your Rocket League war room."
          ], [
            { text: "Got it, thanks!", action: finishTutorial }
          ]);
        }},
        { text: "Got it, thanks!", action: finishTutorial }
      ]);
    },

    // --- GALLERY (Dominus, female) ---
    gallery: () => {
      chainLines([
        "Whoa, the Gallery! You looking to upload a preset or just browsing?"
      ], [
        { text: "Tell me how to upload.", action: () => {
          chainLines([
            "Just click the 'Upload Design' button at the top right.",
            "It mints your preset into a Legendary Trading Card. Pretty sick, right?"
          ], [
            { text: "That's amazing!", action: finishTutorial }
          ]);
        }},
        { text: "Just browsing.", action: finishTutorial }
      ]);
    },

    // --- ANALYTICS (Dominus, female) ---
    analytics: () => {
      chainLines([
        "Analytics page! Ready to face the hard truth about your win rates?"
      ], [
        { text: "Give it to me straight.", action: () => {
          chainLines([
            "This page pulls raw data from the ballchasing API.",
            "Use the charts to figure out which maps you're throwing on!"
          ], [
            { text: "Time to grind.", action: finishTutorial }
          ]);
        }},
        { text: "I already know I'm cracked.", action: finishTutorial }
      ]);
    },

    profile: () => {
      chainLines([
        "Welcome to your Profile! Link your RL username here so Dashboard and Analytics load your stats automatically.",
        "Quick Actions below jump you to Dashboard, Analytics, Hitbox, or a fresh player search."
      ], [
        { text: "Show me Quick Actions", action: () => {
          chainLines([
            "Those cards are shortcuts — tap one and we send you straight there with your name pre-filled.",
            "Upload an avatar too if you want the nav bar to look clean."
          ], [{ text: "Nice!", action: finishTutorial }]);
        }},
        { text: "Got it!", action: finishTutorial }
      ]);
    },

    recommend: () => {
      chainLines([
        "Recommendations! We crunch your ballchasing data and suggest playlists or focus areas.",
        "Search a player name if you want tips for someone else."
      ], [
        { text: "How's it calculated?", action: () => {
          chainLines([
            "Win rate, map performance, and streaks all feed into the suggestions.",
            "Use it between sessions to decide what to grind next."
          ], [{ text: "Let's grind.", action: finishTutorial }]);
        }},
        { text: "Sweet.", action: finishTutorial }
      ]);
    },

    hitbox: () => {
      chainLines([
        "Hitbox lookup — search any car name to see which hitbox class it uses.",
        "Octane, Dominus, Fennec, Breakout… they're all grouped so you can compare playstyles."
      ], [
        { text: "How do I search?", action: () => {
          chainLines([
            "Type a car in the search box — try Fennec or Dominus — and hit Search.",
            "Scroll down for the full list sorted by hitbox type."
          ], [
            { text: "Got it!", action: finishTutorial }
          ]);
        }},
        { text: "Dominus for life.", action: () => {
          typeText("Respect. Long hood, clean flicks. You get it.", () => {
            setTimeout(finishTutorial, 2200);
          });
        }}
      ]);
    }
  };

  // --- Activate ---
  bindTourReplayButton(pageKey);

  setTimeout(() => {
    container.classList.add('active');
    highlightMask.classList.add('active');

    const welcomeText = charKey === 'octane'
      ? "Hey — I'm Octane. Want a quick tour of this page? I can talk you through it."
      : "Hi. Dominus here. Want a short walkthrough of this screen?";
      
    textArea.innerHTML = welcomeText;
    
    const startText = charKey === 'octane' ? "Let's roll!" : "Proceed";
    
    showOptions([
      {
        text: startText,
        action: () => {
          // Play a silent click blip via custom oscillator and start flow
          ensureAudioCtx();
          if (Flows[pageKey]) Flows[pageKey]();
        }
      },
      {
        text: "Skip tour",
        action: finishTutorial
      }
    ]);
  }, 800);
}
