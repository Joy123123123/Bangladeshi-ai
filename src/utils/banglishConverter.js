/**
 * Client-side Banglish detection and input hints.
 *
 * Banglish = Romanised Bengali (e.g., "ami math er question korte chai")
 * These utilities help the UI show helpful hints and pre-process input
 * before sending it to the backend parser.
 */

// ---------------------------------------------------------------------------
// Banglish → Bengali word mapping (client-side, lightweight)
// ---------------------------------------------------------------------------
/** @type {Record<string, string>} */
const COMMON_BANGLISH = {
  ami: "আমি",
  tumi: "তুমি",
  apni: "আপনি",
  ki: "কি",
  keno: "কেন",
  kivabe: "কিভাবে",
  math: "গণিত",
  physics: "পদার্থবিজ্ঞান",
  chemistry: "রসায়ন",
  biology: "জীববিজ্ঞান",
  english: "ইংরেজি",
  bangla: "বাংলা",
  exam: "পরীক্ষা",
  question: "প্রশ্ন",
  answer: "উত্তর",
  help: "সাহায্য",
  study: "পড়াশোনা",
  class: "শ্রেণী",
  shortcut: "শর্টকাট",
  formula: "সূত্র",
  problem: "সমস্যা",
  solve: "সমাধান করুন",
  explain: "ব্যাখ্যা করুন",
  important: "গুরুত্বপূর্ণ",
  easy: "সহজ",
  hard: "কঠিন",
  preparation: "প্রস্তুতি",
  admission: "ভর্তি",
};

// Patterns that strongly suggest Banglish input
const BANGLISH_PATTERNS = [
  /\b(ami|tumi|apni|amar|tomar)\b/i,
  /\b(koro|korte|korun|korbo|korechi)\b/i,
  /\b(ache|achhe|nai|nei|hobe|hoy)\b/i,
  /\b(ektu|ekটু|kintu|tahole|theke)\b/i,
  /\b(kivabe|kemon|kothay|kothai)\b/i,
];

const SUBJECT_BANGLISH_KEYWORDS = [
  "math", "maths", "physics", "fisics", "chemistry", "chem", "biology", "bio",
  "bangla", "english", "history", "geography", "economics", "ict", "science",
];

// ---------------------------------------------------------------------------
// Detection
// ---------------------------------------------------------------------------

/**
 * Returns true if the input string is likely Banglish.
 */
export function isBanglish(text) {
  if (!text || text.trim().length === 0) return false;

  const hasBanglaChars = /[\u0980-\u09FF]/.test(text);
  const hasLatinChars = /[a-zA-Z]/.test(text);

  // If there's Bengali script, it's not Banglish
  if (hasBanglaChars && !hasLatinChars) return false;

  // Check common patterns
  const lower = text.toLowerCase();
  for (const pattern of BANGLISH_PATTERNS) {
    if (pattern.test(lower)) return true;
  }

  // Check subject keywords
  for (const kw of SUBJECT_BANGLISH_KEYWORDS) {
    if (lower.includes(kw)) return true;
  }

  return false;
}

/**
 * Returns the detected subject code from the input text, or null.
 */
export function detectSubjectFromText(text) {
  if (!text) return null;
  const lower = text.toLowerCase();
  const subjectMap = {
    math: "math", maths: "math", gonit: "math", গণিত: "math",
    physics: "physics", pদার্থ: "physics", podartho: "physics",
    chemistry: "chemistry", chem: "chemistry", রসায়ন: "chemistry",
    biology: "biology", bio: "biology", জীব: "biology",
    english: "english", ইংরেজি: "english",
    bangla: "bangla", বাংলা: "bangla",
    history: "history", ইতিহাস: "history",
    geography: "geography", ভূগোল: "geography",
    economics: "economics", অর্থনীতি: "economics",
    ict: "ict", computer: "ict",
    science: "general_science", বিজ্ঞান: "general_science",
  };

  for (const [keyword, subject] of Object.entries(subjectMap)) {
    if (lower.includes(keyword)) return subject;
  }
  return null;
}

// ---------------------------------------------------------------------------
// Lightweight client-side conversion (partial – backend does the full parse)
// ---------------------------------------------------------------------------

/**
 * Partially converts known Banglish words to Bengali.
 * The backend performs the authoritative full conversion.
 */
export function partialBanglishToBangla(text) {
  if (!text) return text;
  const words = text.split(/\s+/);
  return words
    .map((word) => {
      const clean = word.toLowerCase().replace(/[^a-z]/g, "");
      return COMMON_BANGLISH[clean] || word;
    })
    .join(" ");
}

/**
 * Returns a hint message to display to the user when Banglish is detected.
 */
export function getBanglishHint(text) {
  if (!isBanglish(text)) return null;
  return "💡 আপনি ইংরেজি হরফে বাংলা লিখছেন — AI স্বয়ংক্রিয়ভাবে বুঝতে পারবে!";
}

/**
 * Validate that the input is non-empty and within length limits.
 */
export function validateInput(text, maxLength = 4000) {
  if (!text || text.trim().length === 0) {
    return { valid: false, error: "প্রশ্নটি খালি রাখা যাবে না।" };
  }
  if (text.length > maxLength) {
    return { valid: false, error: `প্রশ্ন ${maxLength} অক্ষরের বেশি হতে পারবে না।` };
  }
  return { valid: true, error: null };
}
