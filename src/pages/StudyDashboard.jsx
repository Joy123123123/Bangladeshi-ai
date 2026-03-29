import { useState } from "react";
import ChatUI from "../components/ChatUI";
import { useDataSaver } from "../hooks/useDataSaver";

const QUICK_SUBJECTS = [
  { code: "math", icon: "📐", name: "গণিত" },
  { code: "physics", icon: "⚛️", name: "পদার্থ" },
  { code: "chemistry", icon: "🧪", name: "রসায়ন" },
  { code: "biology", icon: "🌿", name: "জীববিজ্ঞান" },
  { code: "english", icon: "📝", name: "ইংরেজি" },
  { code: "bangla", icon: "বাং", name: "বাংলা" },
];

const QUICK_EXAMS = [
  { code: "SSC", label: "SSC প্রস্তুতি", color: "bg-blue-100 dark:bg-blue-900" },
  { code: "HSC", label: "HSC প্রস্তুতি", color: "bg-purple-100 dark:bg-purple-900" },
  { code: "BUET", label: "BUET ভর্তি", color: "bg-orange-100 dark:bg-orange-900" },
  { code: "Medical", label: "মেডিকেল ভর্তি", color: "bg-red-100 dark:bg-red-900" },
  { code: "BCS", label: "BCS প্রস্তুতি", color: "bg-green-100 dark:bg-green-900" },
];

/**
 * StudyDashboard — Subject selection, quick shortcuts, and chat integration.
 */
export function StudyDashboard() {
  const [activeView, setActiveView] = useState("dashboard"); // "dashboard" | "chat"
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedExam, setSelectedExam] = useState(null);
  const [selectedClass, setSelectedClass] = useState(10);
  const { dataSaverMode, toggleDataSaver, dataUsageKB, savedKB } = useDataSaver();

  const startChat = (subject = null, exam = null) => {
    if (subject) setSelectedSubject(subject);
    if (exam) setSelectedExam(exam);
    setActiveView("chat");
  };

  if (activeView === "chat") {
    return (
      <div className="h-screen flex flex-col">
        {/* Back button */}
        <button
          onClick={() => setActiveView("dashboard")}
          className="fixed top-2 left-2 z-50 bg-white dark:bg-gray-800 border border-gray-300
                     dark:border-gray-600 text-sm px-3 py-1 rounded-full shadow-sm hover:bg-gray-50
                     dark:hover:bg-gray-700 transition-colors"
        >
          ← ড্যাশবোর্ড
        </button>
        <ChatUI
          initialSubject={selectedSubject}
          initialExam={selectedExam}
          initialClass={selectedClass}
          dataSaverMode={dataSaverMode}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      {/* ------------------------------------------------------------------ */}
      {/* Header                                                              */}
      {/* ------------------------------------------------------------------ */}
      <header className="bg-green-700 text-white p-4 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold">🎓 বাংলাদেশী AI শিক্ষা</h1>
          <p className="text-xs text-green-200">NCTB পাঠ্যক্রম · SSC · HSC · ভর্তি পরীক্ষা</p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <button
            onClick={toggleDataSaver}
            className={`text-xs px-3 py-1 rounded-full font-medium transition-colors
              ${dataSaverMode ? "bg-yellow-400 text-gray-900" : "bg-green-600 text-white border border-green-400"}`}
          >
            {dataSaverMode ? "📶 ডেটা সেভার: চালু" : "📶 ডেটা সেভার: বন্ধ"}
          </button>
          {dataSaverMode && (
            <span className="text-xs text-green-200">
              {savedKB > 0 ? `${savedKB} KB সাশ্রয়` : "সাশ্রয় চলছে..."}
            </span>
          )}
        </div>
      </header>

      <main className="p-4 max-w-2xl mx-auto space-y-6">
        {/* ---------------------------------------------------------------- */}
        {/* Class selector                                                   */}
        {/* ---------------------------------------------------------------- */}
        <section>
          <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-2">
            আপনার শ্রেণী
          </h2>
          <div className="flex gap-2">
            {[9, 10, 11, 12].map((c) => (
              <button
                key={c}
                onClick={() => setSelectedClass(c)}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors
                  ${
                    selectedClass === c
                      ? "bg-green-600 text-white"
                      : "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
                  }`}
              >
                শ্রেণী {c}
              </button>
            ))}
          </div>
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Subject quick-launch                                             */}
        {/* ---------------------------------------------------------------- */}
        <section>
          <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-2">
            বিষয় নির্বাচন করুন
          </h2>
          <div className="grid grid-cols-3 gap-2">
            {QUICK_SUBJECTS.map((s) => (
              <button
                key={s.code}
                onClick={() => startChat(s.code)}
                className="flex flex-col items-center p-3 bg-white dark:bg-gray-800
                           border border-gray-200 dark:border-gray-700 rounded-xl
                           hover:border-green-500 hover:bg-green-50 dark:hover:bg-green-900/20
                           transition-all active:scale-95"
              >
                <span className="text-2xl mb-1">{s.icon}</span>
                <span className="text-xs font-medium">{s.name}</span>
              </button>
            ))}
          </div>
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Admission exam shortcuts                                         */}
        {/* ---------------------------------------------------------------- */}
        <section>
          <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-2">
            ভর্তি পরীক্ষার প্রস্তুতি
          </h2>
          <div className="space-y-2">
            {QUICK_EXAMS.map((ex) => (
              <button
                key={ex.code}
                onClick={() => startChat(null, ex.code)}
                className={`w-full text-left px-4 py-3 rounded-xl ${ex.color}
                             border border-transparent hover:border-green-400 transition-colors
                             font-medium text-sm flex items-center justify-between`}
              >
                <span>{ex.label}</span>
                <span className="text-gray-500 dark:text-gray-400 text-xs">AI সহকারী →</span>
              </button>
            ))}
          </div>
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* General chat CTA                                                 */}
        {/* ---------------------------------------------------------------- */}
        <section>
          <button
            onClick={() => startChat()}
            className="w-full py-4 bg-green-600 hover:bg-green-700 text-white rounded-xl
                       font-semibold text-base transition-colors shadow-md"
          >
            💬 যেকোনো প্রশ্ন করুন
          </button>
          <p className="text-center text-xs text-gray-400 dark:text-gray-500 mt-2">
            বাংলা · ইংরেজি · Banglish — সব ধরনের ভাষায় প্রশ্ন করুন
          </p>
        </section>
      </main>
    </div>
  );
}

export default StudyDashboard;
