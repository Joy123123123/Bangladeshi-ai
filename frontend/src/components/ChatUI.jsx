import React, { useState, useRef, useEffect } from 'react';

const SUBJECTS = [
    { code: "general", name: "সাধারণ" },
    { code: "bangla", name: "বাংলা" },
    { code: "english", name: "ইংরেজি" },
    { code: "math", name: "গণিত" },
    { code: "physics", name: "পদার্থবিজ্ঞান" },
    { code: "chemistry", name: "রসায়ন" },
    { code: "biology", name: "জীববিজ্ঞান" },
    { code: "ict", name: "আইসিটি" },
    { code: "history", name: "ইতিহাস" },
    { code: "geography", name: "ভূগোল" },
];

const EXAM_TYPES = ["General", "SSC", "HSC", "BUET", "DU", "Medical", "BCS"];

const API_BASE = import.meta.env.VITE_API_BASE || "";

export const ChatUI = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [classLevel, setClassLevel] = useState(10);
    const [subject, setSubject] = useState("general");
    const [examType, setExamType] = useState("General");
    const [dataSaverMode, setDataSaverMode] = useState(false);
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const handleSend = async () => {
        const trimmed = input.trim();
        if (!trimmed || loading) return;

        const userMessage = { role: "user", content: trimmed };
        setMessages(prev => [...prev, userMessage]);
        setInput("");
        setLoading(true);

        try {
            const response = await fetch(`${API_BASE}/api/v1/chat/stream`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: trimmed,
                    class_level: classLevel,
                    subject: subject,
                    exam_type: examType,
                    data_saver_mode: dataSaverMode,
                    preferred_model: "auto",
                    include_rag: true,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantContent = "";

            // Add placeholder for assistant message
            setMessages(prev => [...prev, { role: "assistant", content: "" }]);

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const text = decoder.decode(value, { stream: true });
                const lines = text.split("\n");

                for (const line of lines) {
                    if (!line.startsWith("data: ")) continue;
                    const data = line.slice(6).trim();
                    if (data === "[DONE]") break;

                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.content) {
                            assistantContent += parsed.content;
                            setMessages(prev => [
                                ...prev.slice(0, -1),
                                { role: "assistant", content: assistantContent },
                            ]);
                        }
                    } catch (_) { /* ignore parse errors */ }
                }
            }
        } catch (error) {
            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: `⚠️ ত্রুটি: ${error.message}. অনুগ্রহ করে আবার চেষ্টা করুন।`,
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const bg = dataSaverMode ? "bg-gray-900 text-white" : "bg-white text-gray-900";
    const borderColor = dataSaverMode ? "border-gray-700" : "border-gray-200";
    const inputBg = dataSaverMode ? "bg-gray-800 border-gray-600 text-white placeholder-gray-400" : "bg-white border-gray-300";
    const assistantBg = dataSaverMode ? "bg-gray-800 text-gray-100" : "bg-gray-100 text-gray-900";

    return (
        <div className={`flex flex-col h-screen ${bg}`}>
            {/* Header */}
            <div className={`p-4 border-b ${borderColor} shadow-sm`}>
                <h1 className="text-xl font-bold mb-3">📚 বাংলাদেশী শিক্ষক AI</h1>

                <div className="grid grid-cols-2 gap-2 mb-2">
                    <select
                        value={classLevel}
                        onChange={e => setClassLevel(parseInt(e.target.value))}
                        className={`p-2 rounded border text-sm ${inputBg}`}
                    >
                        {[9, 10, 11, 12].map(c => (
                            <option key={c} value={c}>{c} শ্রেণী</option>
                        ))}
                    </select>

                    <select
                        value={subject}
                        onChange={e => setSubject(e.target.value)}
                        className={`p-2 rounded border text-sm ${inputBg}`}
                    >
                        {SUBJECTS.map(s => (
                            <option key={s.code} value={s.code}>{s.name}</option>
                        ))}
                    </select>
                </div>

                <div className="flex gap-2">
                    <select
                        value={examType}
                        onChange={e => setExamType(e.target.value)}
                        className={`flex-1 p-2 rounded border text-sm ${inputBg}`}
                    >
                        {EXAM_TYPES.map(t => (
                            <option key={t} value={t}>{t}</option>
                        ))}
                    </select>

                    <button
                        onClick={() => setDataSaverMode(m => !m)}
                        className={`px-3 py-2 rounded text-sm font-semibold transition ${
                            dataSaverMode
                                ? "bg-green-600 text-white"
                                : "bg-gray-200 text-gray-800"
                        }`}
                        title="ডেটা সেভার মোড"
                    >
                        💾 {dataSaverMode ? "ON" : "OFF"}
                    </button>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages.length === 0 && (
                    <div className="text-center text-gray-400 mt-16">
                        <p className="text-4xl mb-4">📖</p>
                        <p className="text-lg">আপনার প্রশ্ন করুন...</p>
                        <p className="text-sm mt-2">বাংলা, ইংরেজি বা Banglish-এ লিখতে পারেন</p>
                    </div>
                )}

                {messages.map((msg, i) => (
                    <div
                        key={i}
                        className={`p-3 rounded-lg whitespace-pre-wrap leading-relaxed ${
                            msg.role === "user"
                                ? "bg-blue-500 text-white ml-8 rounded-br-none"
                                : `${assistantBg} mr-8 rounded-bl-none`
                        }`}
                    >
                        {msg.role === "assistant" && (
                            <span className="text-xs font-semibold opacity-60 block mb-1">🤖 শিক্ষক AI</span>
                        )}
                        {msg.content || (loading && i === messages.length - 1 ? "⏳ লিখছি..." : "")}
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className={`p-4 border-t ${borderColor}`}>
                <div className="flex gap-2">
                    <textarea
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="প্রশ্ন করুন... (Banglish OK) • Enter পাঠাতে, Shift+Enter নতুন লাইনে"
                        rows={2}
                        className={`flex-1 p-3 rounded border resize-none text-sm ${inputBg}`}
                        disabled={loading}
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading || !input.trim()}
                        className="px-5 py-2 bg-blue-600 text-white rounded font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition self-end"
                    >
                        {loading ? "⏳" : "📤"}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatUI;
