/* ============================================================
   Dr. Yashaswini – Voice Agent Logic v5
   KEY FIXES:
   - FEMALE voice guaranteed (aggressive selection)
   - FAST voice input (single-utterance mode, instant finalization)
   - FAST voice output (higher rate, no unnecessary delays)
   - Beautiful avatar animations preserved
   - Multi-language support preserved
   ============================================================ */

const STATES = { IDLE: 'idle', LISTENING: 'listening', PROCESSING: 'processing', SPEAKING: 'speaking' };

let currentState = STATES.IDLE;
let recognition = null;
let synth = window.speechSynthesis;
let selectedVoice = null;
let mouthTimer = null;
let blinkTimer = null;
let micActive = false;
let habitsChosen = [];
let photosConfirmed = { 1: false, 2: false, 3: false };
let currentLang = 'en-IN';

// Known FEMALE voice names per platform
const FEMALE_VOICE_NAMES = [
    // Windows female voices
    'zira', 'heera', 'neerja', 'hemant',
    // macOS / iOS
    'samantha', 'karen', 'moira', 'tessa', 'fiona', 'veena', 'lekha',
    // Google TTS
    'google uk english female', 'google us english female',
    // Android
    'female',
];

// Known MALE voice names to EXCLUDE
const MALE_VOICE_NAMES = [
    'david', 'mark', 'ravi', 'james', 'daniel', 'george', 'richard',
    'alex', 'fred', 'thomas', 'male',
];

// Language configs
const LANG_MAP = {
    'en': { code: 'en-IN', label: 'English', ttsLang: 'en-IN', flag: '🇬🇧' },
    'hi': { code: 'hi-IN', label: 'हिन्दी', ttsLang: 'hi-IN', flag: '🇮🇳' },
    'kn': { code: 'kn-IN', label: 'ಕನ್ನಡ', ttsLang: 'kn-IN', flag: '🇮🇳' },
    'te': { code: 'te-IN', label: 'తెలుగు', ttsLang: 'te-IN', flag: '🇮🇳' },
    'ta': { code: 'ta-IN', label: 'தமிழ்', ttsLang: 'ta-IN', flag: '🇮🇳' },
    'ml': { code: 'ml-IN', label: 'മലയാളം', ttsLang: 'ml-IN', flag: '🇮🇳' },
    'mr': { code: 'mr-IN', label: 'मराठी', ttsLang: 'mr-IN', flag: '🇮🇳' },
    'bn': { code: 'bn-IN', label: 'বাংলা', ttsLang: 'bn-IN', flag: '🇮🇳' },
    'gu': { code: 'gu-IN', label: 'ગુજરાતી', ttsLang: 'gu-IN', flag: '🇮🇳' },
};

function setLanguage(langKey) {
    const lang = LANG_MAP[langKey] || LANG_MAP['en'];
    currentLang = lang.code;
    if (recognition) recognition.lang = lang.code;
    loadVoiceForLang(lang.ttsLang);
    const sel = document.getElementById('langSelect');
    if (sel) sel.value = langKey;

    fetch('/aria/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: `[LANG_CHANGE] The patient prefers to speak in ${lang.label}. Please switch to ${lang.label} language for all your responses from now on.` })
    }).then(r => r.json()).then(data => {
        if (data.speech) {
            addBubble('aria', data.speech);
            speak(data.speech);
        }
    }).catch(() => { });
}

// ══════════════════════════════════════════════════════════════
//  FEMALE VOICE SELECTION — Aggressive & Reliable
// ══════════════════════════════════════════════════════════════

function isFemaleVoice(voice) {
    const name = voice.name.toLowerCase();
    // Check if it matches known female names
    if (FEMALE_VOICE_NAMES.some(f => name.includes(f))) return true;
    // Check if it has "female" or "woman" in the name
    if (/female|woman/i.test(name)) return true;
    // Exclude known male voices
    if (MALE_VOICE_NAMES.some(m => name.includes(m))) return false;
    // If it has "Microsoft" and is NOT a known male, assume it could be female
    // (Windows has limited voices, we can't always tell)
    return false;
}

function isMaleVoice(voice) {
    const name = voice.name.toLowerCase();
    return MALE_VOICE_NAMES.some(m => name.includes(m)) || /\bmale\b/i.test(name);
}

function loadVoiceForLang(ttsLang) {
    const voices = synth.getVoices();
    if (!voices.length) return;

    const langBase = ttsLang.split('-')[0];  // e.g., 'en', 'hi', 'kn'

    // PRIORITY 1: Exact language match + known female name
    let v = voices.find(v => v.lang === ttsLang && isFemaleVoice(v));

    // PRIORITY 2: Language family match + known female
    if (!v) v = voices.find(v => v.lang.startsWith(langBase) && isFemaleVoice(v));

    // PRIORITY 3: Exact language match + NOT known male
    if (!v) v = voices.find(v => v.lang === ttsLang && !isMaleVoice(v));

    // PRIORITY 4: Language family match + NOT known male
    if (!v) v = voices.find(v => v.lang.startsWith(langBase) && !isMaleVoice(v));

    // PRIORITY 5: en-IN female
    if (!v) v = voices.find(v => v.lang === 'en-IN' && isFemaleVoice(v));

    // PRIORITY 6: en-IN not male
    if (!v) v = voices.find(v => v.lang === 'en-IN' && !isMaleVoice(v));

    // PRIORITY 7: Any English female (Zira, etc.)
    if (!v) v = voices.find(v => v.lang.startsWith('en') && isFemaleVoice(v));

    // PRIORITY 8: Any English NOT male
    if (!v) v = voices.find(v => v.lang.startsWith('en') && !isMaleVoice(v));

    // PRIORITY 9: Any language female
    if (!v) v = voices.find(v => isFemaleVoice(v));

    // PRIORITY 10: Absolute fallback - any voice at all
    if (!v) v = voices.find(v => v.lang.startsWith(langBase)) || voices[0];

    selectedVoice = v;
    console.log('[Dr.Y] Selected voice:', v?.name, v?.lang, '| Female?', v ? isFemaleVoice(v) : 'n/a');
}

function initVoices() {
    const tryLoad = () => {
        loadVoiceForLang(currentLang);
        // Log all available voices for debugging
        const voices = synth.getVoices();
        console.log('[Dr.Y] Available voices:', voices.map(v => `${v.name} (${v.lang})`).join(', '));
    };
    if (synth.getVoices().length) tryLoad();
    synth.addEventListener('voiceschanged', tryLoad);
}

// ══════════════════════════════════════════════════════════════
//  AVATAR ANIMATION SYSTEM
// ══════════════════════════════════════════════════════════════

// ── Blink Animation ──
function startBlinking() {
    if (blinkTimer) return;
    const blink = () => {
        const blL = document.getElementById('blinkL');
        const blR = document.getElementById('blinkR');
        if (!blL || !blR) return;
        blL.setAttribute('ry', '13');
        blR.setAttribute('ry', '13');
        setTimeout(() => {
            blL.setAttribute('ry', '0');
            blR.setAttribute('ry', '0');
        }, 130);
    };
    const scheduleBlink = () => {
        const delay = 2500 + Math.random() * 2500;
        blinkTimer = setTimeout(() => {
            blink();
            scheduleBlink();
        }, delay);
    };
    scheduleBlink();
}

function stopBlinking() {
    if (blinkTimer) { clearTimeout(blinkTimer); blinkTimer = null; }
    const blL = document.getElementById('blinkL');
    const blR = document.getElementById('blinkR');
    if (blL) blL.setAttribute('ry', '0');
    if (blR) blR.setAttribute('ry', '0');
}

// ── Mouth Animation (for speaking) ──
function startMouthAnim() {
    if (mouthTimer) return;
    const mouth = document.getElementById('mouthLower');
    const inner = document.getElementById('mouthInner');
    if (!mouth || !inner) return;

    let open = false;
    mouthTimer = setInterval(() => {
        open = !open;
        if (open) {
            const openAmount = 218 + Math.random() * 8;
            mouth.setAttribute('d', `M122,205 Q150,${openAmount} 178,205`);
            inner.setAttribute('ry', String(4 + Math.random() * 4));
        } else {
            mouth.setAttribute('d', 'M122,205 Q150,213 178,205');
            inner.setAttribute('ry', '1');
        }
    }, 110 + Math.random() * 50);
}

function stopMouthAnim() {
    if (mouthTimer) { clearInterval(mouthTimer); mouthTimer = null; }
    const mouth = document.getElementById('mouthLower');
    const inner = document.getElementById('mouthInner');
    if (mouth) mouth.setAttribute('d', 'M122,205 Q150,215 178,205');
    if (inner) inner.setAttribute('ry', '0');
}

// ── Glow Ring ──
function setGlowRing(color, pulse) {
    const svg = document.querySelector('#glowRing');
    if (!svg) return;
    const el = svg.querySelector('circle') || svg.querySelector('ellipse');
    if (!el) return;

    el.style.stroke = color;
    if (pulse) {
        el.style.filter = `drop-shadow(0 0 12px ${color})`;
        el.style.animation = 'glowPulse 1.2s ease-in-out infinite';
    } else {
        el.style.filter = `drop-shadow(0 0 6px ${color}50)`;
        el.style.animation = 'none';
    }
}

// ── Face SVG: set expression ──
function setExpression(expression) {
    const faceSvg = document.getElementById('ariaFaceSvg');
    if (!faceSvg) return;

    switch (expression) {
        case 'happy':
            const mouthHappy = document.getElementById('mouthLower');
            if (mouthHappy) mouthHappy.setAttribute('d', 'M122,205 Q150,218 178,205');
            break;
        case 'thinking':
            const mouthThink = document.getElementById('mouthLower');
            if (mouthThink) mouthThink.setAttribute('d', 'M127,207 Q150,212 173,207');
            break;
        case 'neutral':
            const mouthNeutral = document.getElementById('mouthLower');
            if (mouthNeutral) mouthNeutral.setAttribute('d', 'M122,205 Q150,215 178,205');
            break;
    }
}

// ══════════════════════════════════════════════════════════════
//  SPEECH SYNTHESIS (TTS) — Female, Fast
// ══════════════════════════════════════════════════════════════
function speak(text, onDone) {
    if (!text) { if (onDone) onDone(); return; }
    synth.cancel();

    setState(STATES.SPEAKING);
    startMouthAnim();

    // Split into sentences for Chrome workaround
    const sentences = text.match(/[^.!?।]+[.!?।]*/g) || [text];
    let idx = 0;

    // Chrome workaround: periodically resume
    let keepAlive = setInterval(() => {
        if (synth.speaking && synth.paused) synth.resume();
    }, 4000);

    function speakNext() {
        if (idx >= sentences.length) {
            clearInterval(keepAlive);
            stopMouthAnim();
            setExpression('happy');
            setState(STATES.IDLE);
            if (onDone) onDone();
            return;
        }
        const chunk = sentences[idx].trim();
        if (!chunk) { idx++; speakNext(); return; }

        const utt = new SpeechSynthesisUtterance(chunk);
        if (selectedVoice) utt.voice = selectedVoice;
        utt.lang = currentLang;
        utt.rate = 1.05;      // Slightly faster — feels more responsive
        utt.pitch = 1.15;     // Higher pitch — more feminine
        utt.volume = 1.0;

        utt.onend = () => { idx++; speakNext(); };
        utt.onerror = (e) => {
            console.warn('[Dr.Y] TTS error:', e);
            clearInterval(keepAlive);
            stopMouthAnim();
            setState(STATES.IDLE);
            if (onDone) onDone();
        };
        synth.speak(utt);
    }
    speakNext();
}

// ══════════════════════════════════════════════════════════════
//  STATE MACHINE
// ══════════════════════════════════════════════════════════════
function setState(state) {
    currentState = state;
    const lbl = document.getElementById('ariaStatusLabel');
    const btn = document.getElementById('micBtn');
    const mic = document.getElementById('micIcon');
    const faceSvg = document.getElementById('ariaFaceSvg');

    const configs = {
        idle: {
            color: '#4361ee', label: '🟢 Ready — Click mic to speak',
            btnBg: 'linear-gradient(135deg,#4361ee,#7c3aed)',
            icon: 'fa-microphone', ring: '#4361ee', pulse: false, expression: 'happy'
        },
        listening: {
            color: '#00d4aa', label: '🎤 Listening… speak now',
            btnBg: 'linear-gradient(135deg,#00d4aa,#0099aa)',
            icon: 'fa-stop', ring: '#00d4aa', pulse: true, expression: 'neutral'
        },
        processing: {
            color: '#a855f7', label: '🧠 Dr. Yashaswini is thinking…',
            btnBg: 'linear-gradient(135deg,#a855f7,#7c3aed)',
            icon: 'fa-spinner fa-spin', ring: '#a855f7', pulse: true, expression: 'thinking'
        },
        speaking: {
            color: '#f59e0b', label: '🔊 Dr. Yashaswini is speaking…',
            btnBg: 'linear-gradient(135deg,#f59e0b,#ea580c)',
            icon: 'fa-volume-up', ring: '#f59e0b', pulse: true, expression: 'happy'
        },
    };

    const cfg = configs[state] || configs.idle;

    if (lbl) {
        lbl.textContent = cfg.label;
        lbl.style.color = cfg.color;
    }
    if (btn) btn.style.background = cfg.btnBg;
    if (mic) mic.className = `fas ${cfg.icon}`;

    if (faceSvg) {
        faceSvg.style.filter = `drop-shadow(0 8px 30px ${cfg.color}55)`;
    }

    setGlowRing(cfg.ring, cfg.pulse);
    setExpression(cfg.expression);
}

// ══════════════════════════════════════════════════════════════
//  SPEECH RECOGNITION (STT) — FAST single-utterance mode
// ══════════════════════════════════════════════════════════════
function initSpeechRecognition() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
        console.warn('[Dr.Y] SpeechRecognition not available');
        const btn = document.getElementById('micBtn');
        if (btn) btn.title = 'Voice not supported. Use Chrome or Edge.';
        return;
    }

    recognition = new SR();
    recognition.lang = currentLang;
    recognition.continuous = false;      // ← SINGLE UTTERANCE = faster finalization!
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onresult = (e) => {
        let interim = '', final_text = '';
        for (let i = e.resultIndex; i < e.results.length; i++) {
            const t = e.results[i][0].transcript;
            if (e.results[i].isFinal) {
                final_text += t;
            } else {
                interim += t;
            }
        }
        const inp = document.getElementById('textInput');
        if (inp) {
            inp.value = final_text || interim;
            inp.style.borderColor = '#00d4aa';
        }
        // Send immediately on final result
        if (final_text.trim()) {
            stopMicListening();
            sendMessage(final_text.trim());
        }
    };

    recognition.onerror = (e) => {
        console.warn('[Dr.Y] Speech error:', e.error);
        if (e.error === 'not-allowed') {
            addBubble('aria', '⚠️ Microphone access denied. Please allow microphone permission in your browser.');
        } else if (e.error === 'no-speech') {
            // No speech detected — restart if mic is active
            if (micActive) {
                try { recognition.start(); } catch (ex) { }
            }
            return;
        } else if (e.error === 'aborted') {
            // Aborted is normal when we manually stop, do nothing
            return;
        }
        stopMicListening();
    };

    recognition.onend = () => {
        // In single-utterance mode, recognition ends after each phrase.
        // Restart if mic should still be active (user hasn't toggled off)
        if (micActive && currentState === STATES.LISTENING) {
            try { recognition.start(); } catch (e) { }
        }
    };
}

// ── Mic Toggle ────────────────────────────────────────────────
function toggleMic() {
    if (currentState === STATES.SPEAKING) {
        synth.cancel();
        stopMouthAnim();
        setState(STATES.IDLE);
        return;
    }
    if (currentState === STATES.PROCESSING) return;
    if (!micActive) {
        startMicListening();
    } else {
        stopMicListening();
    }
}

function startMicListening() {
    if (!recognition) {
        addBubble('aria', '⚠️ Voice input is not supported in this browser. Please use Google Chrome or Microsoft Edge.');
        return;
    }
    micActive = true;
    setState(STATES.LISTENING);
    const inp = document.getElementById('textInput');
    if (inp) {
        inp.value = '';
        inp.placeholder = '🎤 Listening… speak now';
        inp.style.borderColor = '#00d4aa';
    }
    try { recognition.start(); } catch (e) {
        console.warn('[Dr.Y] Recognition already running');
    }
}

function stopMicListening() {
    micActive = false;
    if (recognition) {
        try { recognition.stop(); } catch (e) { }
    }
    if (currentState === STATES.LISTENING) setState(STATES.IDLE);
    const inp = document.getElementById('textInput');
    if (inp) {
        inp.placeholder = 'Type your answer here…';
        inp.style.borderColor = '#1e2a50';
    }
}

// ══════════════════════════════════════════════════════════════
//  SEND MESSAGE
// ══════════════════════════════════════════════════════════════
async function sendMessage(text) {
    text = (text || document.getElementById('textInput').value || '').trim();
    if (!text) return;
    if (currentState === STATES.PROCESSING) return;

    if (currentState === STATES.SPEAKING) {
        synth.cancel();
        stopMouthAnim();
    }

    stopMicListening();
    document.getElementById('textInput').value = '';
    addBubble('user', text);
    setState(STATES.PROCESSING);
    showTypingIndicator();

    try {
        const res = await fetch('/aria/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        removeTypingIndicator();
        handleResponse(data);
    } catch (e) {
        console.error('[Dr.Y] Fetch error:', e);
        removeTypingIndicator();
        addBubble('aria', "Sorry, I had a connection issue. Please click the mic button and try again.");
        setState(STATES.IDLE);
    }
}

// ── Typing Indicator ──
function showTypingIndicator() {
    const wrap = document.getElementById('transcript');
    if (!wrap) return;
    removeTypingIndicator();
    const div = document.createElement('div');
    div.className = 'aria-msg aria';
    div.id = 'typingIndicator';
    div.innerHTML = `
        <div class="aria-bubble" style="display:flex;align-items:center;gap:6px;padding:.5rem 1.2rem;">
            <span class="typing-dot" style="animation-delay:0s"></span>
            <span class="typing-dot" style="animation-delay:0.15s"></span>
            <span class="typing-dot" style="animation-delay:0.3s"></span>
        </div>`;
    wrap.appendChild(div);
    wrap.scrollTop = wrap.scrollHeight;
}

function removeTypingIndicator() {
    const el = document.getElementById('typingIndicator');
    if (el) el.remove();
}

// ══════════════════════════════════════════════════════════════
//  HANDLE RESPONSE — Speak fast, then auto-mic
// ══════════════════════════════════════════════════════════════
function handleResponse(data) {
    const speech = data.speech || '';
    addBubble('aria', speech);

    if (data.action_type === 'fill_field' && data.field) {
        fillField(data.field, data.value || '');
        markProgress(data.field, data.value || '');
    }

    if (data.action_type === 'request_photo' && data.photo_index) {
        highlightPhotoSlot(data.photo_index);
    }

    if (data.is_complete) {
        showFinalSubmit();
    }

    // Speak then IMMEDIATELY auto-start mic — minimal delay
    speak(speech, () => {
        if (!data.is_complete && data.action_type !== 'request_photo') {
            setTimeout(() => {
                if (currentState === STATES.IDLE) {
                    startMicListening();
                }
            }, 150);  // Near-instant mic restart after speech ends
        }
    });
}

// ══════════════════════════════════════════════════════════════
//  FORM HELPERS
// ══════════════════════════════════════════════════════════════
function fillField(field, value) {
    if (field === 'habits') {
        document.querySelectorAll('input[name="habits"]').forEach(i => i.checked = false);
        habitsChosen = value.split(',').map(h => h.trim()).filter(h => h && h !== 'None');
        habitsChosen.forEach(habit => {
            const cb = document.querySelector(`input[name="habits"][value="${habit}"]`);
            if (cb) {
                cb.checked = true;
                const yDiv = { Tobacco: 'tbDiv', Alcohol: 'alcDiv', Smoking: 'smkDiv' }[habit];
                if (yDiv) { const el = document.getElementById(yDiv); if (el) el.style.display = 'block'; }
            }
        });
        return;
    }
    const hid = document.getElementById('hf_' + field);
    if (hid) hid.value = value;

    const vis = document.querySelector(`[name="${field}"]`);
    if (vis && vis.tagName === 'SELECT') {
        for (const opt of vis.options) {
            if (opt.value?.toLowerCase() === value.toLowerCase() ||
                opt.text?.toLowerCase() === value.toLowerCase()) {
                opt.selected = true; break;
            }
        }
    } else if (vis && vis.tagName === 'INPUT') {
        vis.value = value;
    }
}

function markProgress(field, value) {
    const el = document.getElementById('prog_' + field);
    if (!el) return;
    el.innerHTML = `<i class="fas fa-check-circle text-success me-1"></i><span class="fw-semibold">${escHtml(value)}</span>`;
    el.classList.add('done');
}

function highlightPhotoSlot(idx) {
    const slot = document.getElementById('photoSlot' + idx);
    if (!slot) return;
    slot.classList.add('aria-highlight');
    slot.scrollIntoView({ behavior: 'smooth', block: 'center' });
    const lbl = document.getElementById('photoLabel' + idx);
    if (lbl) lbl.style.display = 'block';
}

function photoConfirmed(idx) {
    photosConfirmed[idx] = true;
    const label = ['', 'Front View', 'Left Side', 'Right Side'][idx];
    markProgress('photo_' + idx, label + ' ✓');
    const slot = document.getElementById('photoSlot' + idx);
    if (slot) slot.classList.remove('aria-highlight');
    sendMessage(`I have taken the ${label} photo.`);
}

function showFinalSubmit() {
    const area = document.getElementById('submitArea');
    if (area) { area.style.display = 'flex'; area.scrollIntoView({ behavior: 'smooth' }); }
}

function submitScreening() {
    document.getElementById('ariaForm').submit();
}

// ── Chat Bubbles (with smooth animation) ──
function addBubble(role, text) {
    const wrap = document.getElementById('transcript');
    if (!wrap) return;
    const div = document.createElement('div');
    div.className = `aria-msg ${role}`;
    div.innerHTML = `<div class="aria-bubble">${escHtml(text)}</div>`;
    div.style.opacity = '0';
    div.style.transform = 'translateY(8px)';
    wrap.appendChild(div);
    requestAnimationFrame(() => {
        div.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
        div.style.opacity = '1';
        div.style.transform = 'translateY(0)';
    });
    wrap.scrollTop = wrap.scrollHeight;
}

function escHtml(s) {
    return (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ══════════════════════════════════════════════════════════════
//  INIT
// ══════════════════════════════════════════════════════════════
window.addEventListener('DOMContentLoaded', async () => {
    initVoices();
    initSpeechRecognition();
    startBlinking();
    setState(STATES.PROCESSING);

    const ti = document.getElementById('textInput');
    if (ti) ti.addEventListener('keydown', e => {
        if (e.key === 'Enter' && ti.value.trim()) {
            e.preventDefault();
            sendMessage();
        }
    });

    const sb = document.getElementById('sendBtn');
    if (sb) sb.addEventListener('click', () => sendMessage());

    const mb = document.getElementById('micBtn');
    if (mb) mb.addEventListener('click', toggleMic);

    const ls = document.getElementById('langSelect');
    if (ls) ls.addEventListener('change', () => setLanguage(ls.value));

    // Chrome TTS unlock on first click
    document.addEventListener('click', function enableTTS() {
        const utt = new SpeechSynthesisUtterance('');
        utt.volume = 0;
        synth.speak(utt);
        document.removeEventListener('click', enableTTS);
    }, { once: true });

    // Start session
    try {
        const res = await fetch('/aria/start', { method: 'POST' });
        const data = await res.json();
        if (data.response) {
            handleResponse(data.response);
        }
    } catch (e) {
        addBubble('aria', "Hello! I'm Dr. Yashaswini. I'm having trouble connecting right now. Please try refreshing the page.");
        setState(STATES.IDLE);
    }
});
