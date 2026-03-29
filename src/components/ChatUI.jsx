import { useState, useRef, useCallback } from "react";

const SUBJECTS = [
  { code: "general", name: "সাধারণ" },
  { code: "bangla", name: "বাংলা" },
  { code: "english", name: "ইংরেজি" },
  { code: "math", name: "গণিত" },
  { code: "physics", name: "পদার্থবিজ্ঞান" },
  { code: "chemistry", name: "রসায়ন" },
  { code: "biology", name: "জীববিজ্ঞান" },
  { code: "ict", name: "তথ্য প্রযুক্তি" },
  { code: "history", name: "ইতিহাস" },
  { code: "geography", name: "ভূগোল" },
  { code: "economics", name: "অর্থনীতি" },
  { code: "higher_math", name: "উচ্চতর গণিত" },
  { code: "general_science", name: "সাধারণ বিজ্ঞান" },
];

const EXAM_TYPES = [
  { code: "General", name: "সাধারণ" },
  { code: "SSC", name: "SSC" },
  { code: "HSC", name: "HSC" },
  { code: "BUET", name: "BUET" },
  { code: "DU", name: "ঢাকা বিশ্ববিদ্যালয়" },
  { code: "Medical", name: "মেডিকেল" },
  { code: "BCS", name: "BCS" },
];

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * ChatUI — Lightweight streaming chat interface for Bangladeshi students.
 *
 * Features:
 *  - Real-time SSE streaming
 *  - Data Saver toggle (compresses images, shorter chunks)
 *  - Subject / Class / Exam-type selector (NCTB context)
 *  - Banglish hint display
 *  - Dark mode support via Tailwind
 */
export const ChatUI = () => {
  const [dataSaverMode, setDataSaverMode] = useState(false);
  const [selectedClass, setSelectedClass] = useState(10);
  const [selectedSubject, setSelectedSubject] = useState("general");
  const [selectedExam, setSelectedExam] = useState("General");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "আস্সালামু আলাইকুম! আমি আপনার NCTB AI শিক্ষা সহকারী। আপনার যেকোনো প্রশ্ন করুন। 🎓",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const appendToLastAssistantMessage = useCallback((chunk) => {
    setMessages((prev) => {
      const updated = [...prev];
      const last = updated[updated.length - 1];
      if (last?.role === "assistant") {
        updated[updated.length - 1] = {
          ...last,
          content: last.content + chunk,
        };
      } else {
        updated.push({ role: "assistant", content: chunk });
      }
      return updated;
    });
  }, []);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    // Append user message
    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");
    setIsLoading(true);

    // Placeholder for assistant response
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(`${API_BASE}/api/v1/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: trimmed,
          class_level: selectedClass,
          subject: selectedSubject,
          exam_type: selectedExam,
          data_saver_mode: dataSaverMode,
          session_id: sessionId,
          include_rag: true,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // Capture session ID from response header
      const sid = response.headers.get("X-Session-ID");
      if (sid && !sessionId) setSessionId(sid);

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop(); // keep incomplete line in buffer

        for (const line of lines) {
          if (!line.startsWith("data:")) continue;
          const raw = line.slice(5).trim();
          if (raw === "[DONE]") break;

          try {
            const parsed = JSON.parse(raw);
            if (parsed.content) {
              appendToLastAssistantMessage(parsed.content);
              scrollToBottom();
            }
            if (parsed.error) {
              appendToLastAssistantMessage(
                `\n\n❌ ত্রুটি: ${parsed.error}`
              );
            }
          } catch {
            // ignore malformed chunks
          }
        }
      }
    } catch (err) {
      if (err.name !== "AbortError") {
        appendToLastAssistantMessage(
          "দুঃখিত, একটি সমস্যা হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।"
        );
      }
    } finally {
      setIsLoading(false);
      scrollToBottom();
    }
  };

  const handleStop = () => {
    abortControllerRef.current?.abort();
    setIsLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      {/* ------------------------------------------------------------------ */}
      {/* Header / Selector bar                                               */}
      {/* ------------------------------------------------------------------ */}
      <header className="p-3 border-b border-gray-200 dark:border-gray-700 bg-green-50 dark:bg-green-900/20">
        <div className="flex flex-wrap items-center gap-2">
          {/* Class selector */}
          <select
            value={selectedClass}
            onChange={(e) => setSelectedClass(Number(e.target.value))}
            className="text-sm border border-gray-300 dark:border-gray-600 rounded px-2 py-1
                       bg-white dark:bg-gray-800 dark:text-gray-100 focus:outline-none focus:ring-1
                       focus:ring-green-500"
            aria-label="শ্রেণী নির্বাচন"
          >
            {[9, 10, 11, 12].map((c) => (
              <option key={c} value={c}>
                শ্রেণী {c}
              </option>
            ))}
          </select>

          {/* Subject selector */}
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            className="text-sm border border-gray-300 dark:border-gray-600 rounded px-2 py-1
                       bg-white dark:bg-gray-800 dark:text-gray-100 focus:outline-none focus:ring-1
                       focus:ring-green-500"
            aria-label="বিষয় নির্বাচন"
          >
            {SUBJECTS.map((s) => (
              <option key={s.code} value={s.code}>
                {s.name}
              </option>
            ))}
          </select>

          {/* Exam type selector */}
          <select
            value={selectedExam}
            onChange={(e) => setSelectedExam(e.target.value)}
            className="text-sm border border-gray-300 dark:border-gray-600 rounded px-2 py-1
                       bg-white dark:bg-gray-800 dark:text-gray-100 focus:outline-none focus:ring-1
                       focus:ring-green-500"
            aria-label="পরীক্ষার ধরন"
          >
            {EXAM_TYPES.map((ex) => (
              <option key={ex.code} value={ex.code}>
                {ex.name}
              </option>
            ))}
          </select>

          {/* Data Saver toggle */}
          <button
            onClick={() => setDataSaverMode((v) => !v)}
            className={`ml-auto text-xs px-3 py-1 rounded-full font-medium transition-colors
              ${
                dataSaverMode
                  ? "bg-green-600 text-white"
                  : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
              }`}
            aria-pressed={dataSaverMode}
            title="ডেটা সেভার মোড"
          >
            {dataSaverMode ? "📶 ডেটা সেভার: চালু" : "📶 ডেটা সেভার: বন্ধ"}
          </button>
        </div>
      </header>

      {/* ------------------------------------------------------------------ */}
      {/* Message list                                                        */}
      {/* ------------------------------------------------------------------ */}
      <main className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] px-4 py-2 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap
                ${
                  msg.role === "user"
                    ? "bg-green-600 text-white rounded-br-sm"
                    : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-bl-sm"
                }`}
            >
              {msg.content || (
                <span className="opacity-50 animate-pulse">▌</span>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </main>

      {/* ------------------------------------------------------------------ */}
      {/* Input bar                                                           */}
      {/* ------------------------------------------------------------------ */}
      <footer className="p-3 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
        <div className="flex gap-2 items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            placeholder="বাংলায় প্রশ্ন করুন... (Ask in Bengali or English)"
            className="flex-1 resize-none p-2 text-sm border border-gray-300 dark:border-gray-600 rounded-xl
                       bg-white dark:bg-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2
                       focus:ring-green-500 max-h-32"
            disabled={isLoading}
            style={{ overflowY: "auto" }}
          />

          {isLoading ? (
            <button
              onClick={handleStop}
              className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white text-sm rounded-xl
                         transition-colors font-medium"
              title="থামুন"
            >
              ⏹
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-40
                         text-white text-sm rounded-xl transition-colors font-medium"
              title="পাঠান"
            >
              পাঠান →
            </button>
          )}
        </div>

        {/* Banglish hint */}
        {input && /[a-zA-Z]/.test(input) && (
          <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
            💡 ইংরেজি হরফে বাংলা লিখলেও AI বুঝতে পারবে (Banglish সাপোর্টেড)
          </p>
        )}
      </footer>
    </div>
  );
};

export default ChatUI;
