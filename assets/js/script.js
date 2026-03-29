/*!
 * Bangladeshi-AI: Main JavaScript
 * Bengali Language AI Educational Platform
 */

'use strict';

// ============================================================
// Navigation
// ============================================================
(function initNavigation() {
  const navbar = document.querySelector('.navbar');
  const navToggle = document.querySelector('.nav-toggle');
  const navMenu = document.querySelector('.nav-menu');
  const dropdowns = document.querySelectorAll('.dropdown');

  // Scroll effect
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    }, { passive: true });
  }

  // Mobile menu toggle
  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      const isOpen = navMenu.classList.toggle('open');
      navToggle.classList.toggle('open', isOpen);
      navToggle.setAttribute('aria-expanded', isOpen);
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!navbar.contains(e.target)) {
        navMenu.classList.remove('open');
        navToggle.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      }
    });
  }

  // Dropdown toggles (mobile)
  dropdowns.forEach((dropdown) => {
    const trigger = dropdown.querySelector('.nav-link');
    if (trigger) {
      trigger.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
          e.preventDefault();
          dropdown.classList.toggle('open');
        }
      });
    }
  });

  // Highlight active nav link
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach((link) => {
    const href = link.getAttribute('href');
    if (href && currentPath.endsWith(href)) {
      link.classList.add('active');
    }
  });
})();

// ============================================================
// Dark Mode Toggle
// ============================================================
(function initDarkMode() {
  const savedMode = localStorage.getItem('darkMode');
  if (savedMode === 'true') {
    document.body.classList.add('dark-mode');
  }

  const toggle = document.getElementById('darkModeToggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const isDark = document.body.classList.toggle('dark-mode');
      localStorage.setItem('darkMode', isDark);
      toggle.innerHTML = isDark
        ? '<i class="fas fa-sun"></i>'
        : '<i class="fas fa-moon"></i>';
    });
    // Sync icon on load
    if (document.body.classList.contains('dark-mode')) {
      toggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
  }
})();

// ============================================================
// Smooth Scroll for Anchor Links
// ============================================================
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener('click', function (e) {
    const targetId = this.getAttribute('href');
    if (targetId === '#') return;
    const target = document.querySelector(targetId);
    if (target) {
      e.preventDefault();
      const navHeight = parseInt(
        getComputedStyle(document.documentElement).getPropertyValue('--nav-height'),
        10
      ) || 68;
      const top = target.getBoundingClientRect().top + window.scrollY - navHeight - 16;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});

// ============================================================
// Scroll Reveal Animation
// ============================================================
(function initScrollReveal() {
  const elements = document.querySelectorAll(
    '.feature-card, .tool-card, .resource-card, .dataset-item, .tutorial-item, .team-card, .contribute-card'
  );

  if (!('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
  );

  elements.forEach((el) => {
    el.style.opacity = '0';
    observer.observe(el);
  });
})();

// ============================================================
// Text Analyzer Tool
// ============================================================
(function initTextAnalyzer() {
  const form = document.getElementById('textAnalyzerForm');
  if (!form) return;

  const input = document.getElementById('bengaliTextInput');
  const resultBox = document.getElementById('analyzerResult');
  const charCount = document.getElementById('charCount');
  const wordCount = document.getElementById('wordCount');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const clearBtn = document.getElementById('clearBtn');
  const sampleBtns = document.querySelectorAll('.sample-text-btn');

  const SAMPLES = [
    'আমি বাংলাদেশকে ভালোবাসি। এটি একটি সুন্দর দেশ।',
    'কৃত্রিম বুদ্ধিমত্তা বর্তমান বিশ্বে বিপ্লব এনেছে।',
    'বাংলা ভাষার জন্য এনএলপি প্রযুক্তি উন্নত করা দরকার।',
  ];

  // Character & word counter
  if (input) {
    input.addEventListener('input', () => {
      const text = input.value;
      if (charCount) charCount.textContent = text.length;
      if (wordCount) {
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        wordCount.textContent = words;
      }
    });
  }

  // Sample text buttons
  sampleBtns.forEach((btn, i) => {
    btn.addEventListener('click', () => {
      if (input && SAMPLES[i]) {
        input.value = SAMPLES[i];
        input.dispatchEvent(new Event('input'));
      }
    });
  });

  // Clear
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      if (input) { input.value = ''; input.dispatchEvent(new Event('input')); }
      if (resultBox) showResultPlaceholder(resultBox);
    });
  }

  // Analyze
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = input ? input.value.trim() : '';
    if (!text) {
      showError(resultBox, 'অনুগ্রহ করে বিশ্লেষণের জন্য কিছু বাংলা টেক্সট লিখুন।');
      return;
    }
    runAnalysis(text, resultBox, analyzeBtn);
  });

  function runAnalysis(text, box, btn) {
    if (!box) return;
    btn && (btn.disabled = true);
    box.innerHTML = '<div class="flex-center" style="padding:2rem"><div class="spinner"></div><span style="margin-left:.75rem;color:var(--text-muted)">বিশ্লেষণ চলছে...</span></div>';

    setTimeout(() => {
      const analysis = analyzeText(text);
      renderAnalysis(box, analysis);
      btn && (btn.disabled = false);
    }, 800);
  }

  function analyzeText(text) {
    const words = text.trim().split(/\s+/).filter(Boolean);
    const sentences = text.split(/[।!?]+/).filter((s) => s.trim().length > 0);
    const chars = text.length;
    const charsNoSpace = text.replace(/\s/g, '').length;

    // Simple sentiment heuristic using positive/negative Bengali word lists
    const positiveWords = ['ভালো', 'সুন্দর', 'ভালোবাসি', 'চমৎকার', 'অসাধারণ', 'উন্নত', 'সফল', 'আনন্দ', 'খুশি', 'প্রিয়'];
    const negativeWords = ['খারাপ', 'দুঃখ', 'সমস্যা', 'বিপদ', 'ভয়', 'ক্ষতি', 'দুর্ভোগ', 'ব্যর্থ', 'বিপদ'];

    let posScore = 0, negScore = 0;
    words.forEach((w) => {
      if (positiveWords.some((p) => w.includes(p))) posScore++;
      if (negativeWords.some((n) => w.includes(n))) negScore++;
    });

    let sentiment, sentimentClass;
    if (posScore > negScore) { sentiment = 'ইতিবাচক (Positive)'; sentimentClass = 'positive'; }
    else if (negScore > posScore) { sentiment = 'নেতিবাচক (Negative)'; sentimentClass = 'negative'; }
    else { sentiment = 'নিরপেক্ষ (Neutral)'; sentimentClass = 'neutral'; }

    // Avg word length
    const avgWordLen = words.length
      ? (words.reduce((s, w) => s + w.length, 0) / words.length).toFixed(1)
      : 0;

    return { words: words.length, sentences: sentences.length, chars, charsNoSpace, sentiment, sentimentClass, avgWordLen };
  }

  function renderAnalysis(box, a) {
    const sentColor = { positive: '#00a854', negative: '#f42a41', neutral: '#3b82f6' };
    box.innerHTML = `
      <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:.75rem;margin-bottom:1rem">
        <div class="result-stat"><span class="result-stat-num">${a.words}</span><span class="result-stat-label">শব্দ (Words)</span></div>
        <div class="result-stat"><span class="result-stat-num">${a.sentences}</span><span class="result-stat-label">বাক্য (Sentences)</span></div>
        <div class="result-stat"><span class="result-stat-num">${a.chars}</span><span class="result-stat-label">অক্ষর (Chars)</span></div>
        <div class="result-stat"><span class="result-stat-num">${a.avgWordLen}</span><span class="result-stat-label">গড় শব্দ দৈর্ঘ্য</span></div>
      </div>
      <div style="padding:.75rem 1rem;background:rgba(0,0,0,.04);border-radius:8px;display:flex;align-items:center;gap:.75rem">
        <span style="font-weight:600;font-size:.85rem;color:var(--text-secondary)">অনুভূতি বিশ্লেষণ:</span>
        <span class="demo-tag ${a.sentimentClass}" style="border:1px solid ${sentColor[a.sentimentClass]}20">
          ${a.sentiment}
        </span>
      </div>
      <p style="font-size:.8rem;color:var(--text-muted);margin-top:.75rem">
        ⚠️ এই বিশ্লেষণটি বাস্তব AI মডেলের মতো নয়—এটি একটি প্রদর্শনমূলক উদাহরণ।
      </p>`;

    // Inject minimal CSS for result stats if not present
    if (!document.getElementById('resultStatStyle')) {
      const style = document.createElement('style');
      style.id = 'resultStatStyle';
      style.textContent = `.result-stat{background:var(--bg-light);border:1px solid var(--border-color);border-radius:8px;padding:.75rem;text-align:center}.result-stat-num{display:block;font-size:1.6rem;font-weight:800;color:var(--color-primary)}.result-stat-label{font-size:.75rem;color:var(--text-muted)}`;
      document.head.appendChild(style);
    }
  }

  function showResultPlaceholder(box) {
    if (box) box.innerHTML = '<p class="result-placeholder">বিশ্লেষণের ফলাফল এখানে দেখানো হবে...</p>';
  }

  function showError(box, msg) {
    if (box) box.innerHTML = `<p style="color:var(--color-secondary)">${msg}</p>`;
  }
})();

// ============================================================
// Translator Tool
// ============================================================
(function initTranslator() {
  const form = document.getElementById('translatorForm');
  if (!form) return;

  const srcInput = document.getElementById('sourceText');
  const resultBox = document.getElementById('translationResult');
  const swapBtn = document.getElementById('swapBtn');
  const srcLang = document.getElementById('sourceLang');
  const tgtLang = document.getElementById('targetLang');
  const copyBtn = document.getElementById('copyTranslation');

  const DEMO_TRANSLATIONS = {
    'আমি বাংলাদেশ ভালোবাসি': 'I love Bangladesh',
    'বাংলা ভাষা সুন্দর': 'The Bengali language is beautiful',
    'কৃত্রিম বুদ্ধিমত্তা': 'Artificial Intelligence',
    'ধন্যবাদ': 'Thank you',
    'আপনার নাম কি?': 'What is your name?',
  };

  if (swapBtn && srcLang && tgtLang) {
    swapBtn.addEventListener('click', () => {
      const tmp = srcLang.value;
      srcLang.value = tgtLang.value;
      tgtLang.value = tmp;
      if (srcInput) { srcInput.value = ''; }
      if (resultBox) showTranslationPlaceholder(resultBox);
    });
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = srcInput ? srcInput.value.trim() : '';
    if (!text) return;
    translateText(text, resultBox, copyBtn);
  });

  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const text = resultBox ? resultBox.querySelector('.translation-output')?.textContent : '';
      if (text) {
        navigator.clipboard.writeText(text).then(() => {
          copyBtn.textContent = 'Copied!';
          setTimeout(() => { copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy'; }, 2000);
        });
      }
    });
  }

  function translateText(text, box, btn) {
    if (!box) return;
    box.innerHTML = '<div class="flex-center" style="padding:2rem"><div class="spinner"></div><span style="margin-left:.75rem;color:var(--text-muted)">অনুবাদ হচ্ছে...</span></div>';

    setTimeout(() => {
      // Demo: check if we have a hardcoded translation
      const translation = DEMO_TRANSLATIONS[text] || `[Demo] Translated: "${text.substring(0, 60)}${text.length > 60 ? '…' : ''}"`;
      box.innerHTML = `
        <div class="translation-output" style="font-family:var(--font-bengali);font-size:1.1rem;line-height:1.7;color:var(--text-primary);margin-bottom:.75rem">${translation}</div>
        <p style="font-size:.8rem;color:var(--text-muted)">⚠️ এটি একটি ডেমো অনুবাদ। বাস্তব অনুবাদের জন্য Google Translate API সংযোগ প্রয়োজন।</p>`;
    }, 700);
  }

  function showTranslationPlaceholder(box) {
    if (box) box.innerHTML = '<p class="result-placeholder">অনুবাদ এখানে দেখানো হবে...</p>';
  }
})();

// ============================================================
// Speech-to-Text Tool
// ============================================================
(function initSpeechToText() {
  const startBtn = document.getElementById('startRecording');
  const stopBtn = document.getElementById('stopRecording');
  const resultBox = document.getElementById('speechResult');
  const statusEl = document.getElementById('recordingStatus');

  if (!startBtn) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    if (startBtn) {
      startBtn.disabled = true;
      startBtn.title = 'আপনার ব্রাউজার Speech Recognition সাপোর্ট করে না।';
    }
    if (statusEl) {
      statusEl.textContent = '⚠️ আপনার ব্রাউজার ভয়েস রিকগনিশন সাপোর্ট করে না। অনুগ্রহ করে Chrome ব্যবহার করুন।';
    }
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = 'bn-BD';
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;
  let isRecording = false;

  startBtn.addEventListener('click', () => {
    if (isRecording) return;
    recognition.start();
  });

  if (stopBtn) {
    stopBtn.addEventListener('click', () => {
      if (!isRecording) return;
      recognition.stop();
    });
  }

  recognition.addEventListener('start', () => {
    isRecording = true;
    if (startBtn) startBtn.disabled = true;
    if (stopBtn) stopBtn.disabled = false;
    if (statusEl) statusEl.innerHTML = '<span style="color:var(--color-secondary)">🔴 রেকর্ডিং চলছে...</span>';
  });

  recognition.addEventListener('result', (e) => {
    const transcript = Array.from(e.results)
      .map((r) => r[0].transcript)
      .join('');
    if (resultBox) {
      resultBox.innerHTML = `<p style="font-family:var(--font-bengali);font-size:1.1rem;line-height:1.7">${transcript}</p>`;
    }
  });

  recognition.addEventListener('end', () => {
    isRecording = false;
    if (startBtn) startBtn.disabled = false;
    if (stopBtn) stopBtn.disabled = true;
    if (statusEl) statusEl.textContent = 'রেকর্ডিং শেষ হয়েছে।';
  });

  recognition.addEventListener('error', (e) => {
    isRecording = false;
    if (startBtn) startBtn.disabled = false;
    if (stopBtn) stopBtn && (stopBtn.disabled = true);
    if (statusEl) statusEl.textContent = `ত্রুটি: ${e.error}`;
    console.error('Speech recognition error:', e.error);
  });
})();

// ============================================================
// Copy Code Blocks
// ============================================================
document.querySelectorAll('.code-block').forEach((block) => {
  const wrapper = document.createElement('div');
  wrapper.style.cssText = 'position:relative';
  block.parentNode.insertBefore(wrapper, block);
  wrapper.appendChild(block);

  const btn = document.createElement('button');
  btn.textContent = 'Copy';
  btn.style.cssText = 'position:absolute;top:.5rem;right:.5rem;padding:.25rem .6rem;font-size:.75rem;background:rgba(255,255,255,.1);color:#e2e8f0;border:1px solid rgba(255,255,255,.15);border-radius:4px;cursor:pointer;transition:all .2s';
  btn.addEventListener('click', () => {
    navigator.clipboard.writeText(block.textContent).then(() => {
      btn.textContent = 'Copied!';
      setTimeout(() => { btn.textContent = 'Copy'; }, 2000);
    });
  });
  wrapper.appendChild(btn);
});

// ============================================================
// Current Year in Footer
// ============================================================
const yearEls = document.querySelectorAll('.current-year');
yearEls.forEach((el) => { el.textContent = new Date().getFullYear(); });
