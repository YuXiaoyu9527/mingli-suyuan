"use client";

import { useState, useEffect } from "react";
import BottomNav from "@/components/BottomNav";
import FeatureGate from "@/components/FeatureGate";
import { getQuiz, checkAnswer, askMentor } from "@/lib/api";
import { Loader2, ChevronRight, Check, X, Lightbulb, Swords } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface QuizQuestion {
  id: string;
  chapter: string;
  title: string;
  difficulty: number;
  story: string;
  question: string;
  options: { label: string; text: string; hint?: string }[];
}

interface ChapterInfo {
  name: string;
  count: number;
}

export default function DuananPage() {
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [chapters, setChapters] = useState<ChapterInfo[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [correctText, setCorrectText] = useState("");
  const [classicalRef, setClassicalRef] = useState("");
  const [mentorHint, setMentorHint] = useState("");
  const [loading, setLoading] = useState(true);
  const [mentorLoading, setMentorLoading] = useState(false);
  const [showChapters, setShowChapters] = useState(false);
  const [filterChapter, setFilterChapter] = useState<string>("");

  // 进度（localStorage）
  const [progress, setProgress] = useState<Record<string, boolean>>({});

  useEffect(() => {
    // 读取本地进度
    const saved = localStorage.getItem("duanan_progress");
    if (saved) setProgress(JSON.parse(saved));
  }, []);

  useEffect(() => {
    loadQuestions(filterChapter);
  }, [filterChapter]);

  useEffect(() => {
    if (questions.length > 0) {
      setCurrentIdx(0);
      resetQuestion();
    }
  }, [questions]);

  const loadQuestions = async (chapter?: string) => {
    setLoading(true);
    try {
      const data = await getQuiz(chapter || undefined);
      setQuestions(data.questions || []);
      setChapters(data.chapters || []);
    } catch (e) {
      console.error("加载题库失败", e);
    }
    setLoading(false);
  };

  const resetQuestion = () => {
    setSelected(null);
    setIsCorrect(null);
    setCorrectText("");
    setClassicalRef("");
    setMentorHint("");
  };

  const currentQ = questions[currentIdx];
  if (!currentQ) {
    // 显示空状态
  }

  const handleSelect = async (index: number) => {
    if (selected !== null) return;
    setSelected(index);

    try {
      const check = await checkAnswer(currentQ.id, index);
      setIsCorrect(check.correct);
      if (check.correct) {
        setCorrectText(check.correct_text);
        setClassicalRef(check.classical_ref);
        // 保存进度
        const newP = { ...progress, [currentQ.id]: true };
        setProgress(newP);
        localStorage.setItem("duanan_progress", JSON.stringify(newP));
      }

      // AI导师
      setMentorLoading(true);
      try {
        const correctAnswer = currentQ.options[check.correct_answer]?.text || "";
        const data = await askMentor(
          `${currentQ.story}\n\n${currentQ.question}`,
          currentQ.options[index].text,
          correctAnswer,
        );
        setMentorHint(data.hint || "");
      } catch {}
      setMentorLoading(false);
    } catch {
      // 离线模式
      const correct = index === 3; // fallback
      setIsCorrect(correct);
    }
  };

  const nextQuestion = () => {
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(currentIdx + 1);
      resetQuestion();
    }
  };

  const prevQuestion = () => {
    if (currentIdx > 0) {
      setCurrentIdx(currentIdx - 1);
      resetQuestion();
    }
  };

  const totalCompleted = Object.keys(progress).length;
  const totalQuestions = questions.length;
  const chapterProgress = questions.length > 0
    ? Math.round((totalCompleted / totalQuestions) * 100)
    : 0;

  if (loading) {
    return (
      <div className="flex flex-col min-h-dvh pb-20 items-center justify-center gap-3">
        <Loader2 size={32} className="animate-spin text-gold" />
        <p className="text-text-secondary text-sm">加载题库...</p>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      {/* 顶部 */}
      <header className="px-5 pt-10 pb-2">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl text-text font-[family-name:var(--font-display)] tracking-wider">
            断案录
          </h1>
          <button
            onClick={() => setShowChapters(!showChapters)}
            className="text-xs text-text-secondary bg-bg-subtle px-2.5 py-1 rounded-full tap-active">
            {filterChapter || "全部章节"} ▾
          </button>
        </div>

        {/* 进度条（多邻国式） */}
        <div className="mt-3 flex items-center gap-2">
          <Swords size={14} className="text-gold" />
          <span className="text-[11px] text-text-tertiary min-w-[72px]">
            {totalCompleted}/{totalQuestions} 已过
          </span>
          <div className="flex-1 h-1.5 bg-bg-subtle rounded-full overflow-hidden">
            <div className="h-full bg-gold rounded-full transition-all duration-500"
              style={{ width: `${chapterProgress}%` }} />
          </div>
          <span className="text-[11px] text-gold font-medium">{chapterProgress}%</span>
        </div>
      </header>

      {/* 章节选择 */}
      <AnimatePresence>
        {showChapters && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="px-5 overflow-hidden">
            <div className="dao-card mb-3">
              <button onClick={() => { setFilterChapter(""); setShowChapters(false); }}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm mb-1
                  ${!filterChapter ? "bg-accent/10 text-accent font-bold" : "text-text"}`}>
                全部章节（{questions.length}题）
              </button>
              {chapters.map((ch) => (
                <button key={ch.name}
                  onClick={() => { setFilterChapter(ch.name); setShowChapters(false); }}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm mb-1
                    ${filterChapter === ch.name ? "bg-accent/10 text-accent font-bold" : "text-text"}`}>
                  {ch.name}（{ch.count}题）
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="px-5 flex-1 space-y-4 mt-2">
        {/* 题目指示器 */}
        <div className="flex items-center justify-between text-xs text-text-secondary">
          <button onClick={prevQuestion} disabled={currentIdx === 0}
            className={`tap-active ${currentIdx === 0 ? "opacity-30" : "text-accent"}`}>
            ← 上一题
          </button>
          <span>{currentIdx + 1} / {questions.length}</span>
          <button onClick={nextQuestion} disabled={currentIdx >= questions.length - 1}
            className={`tap-active ${currentIdx >= questions.length - 1 ? "opacity-30" : "text-accent"}`}>
            下一题 →
          </button>
        </div>

        {/* 完成标记 */}
        {currentQ && progress[currentQ.id] && (
          <div className="text-center">
            <span className="inline-block px-2 py-0.5 bg-green/10 text-green text-[10px] rounded-full border border-green/20">
              ✅ 已完成
            </span>
          </div>
        )}

        {/* 难度标记 */}
        {currentQ && (
          <div className="flex items-center gap-1 text-[10px] text-text-secondary">
            <span>难度：</span>
            {[1, 2, 3].map((d) => (
              <span key={d} className={d <= currentQ.difficulty ? "text-gold" : "text-dao-paper-darker"}>
                ★
              </span>
            ))}
          </div>
        )}

        {/* 故事卡片 */}
        <div className="dao-card">
          <div className="flex items-start gap-3 mb-3">
            <div className="seal jing-seal flex-shrink-0">案</div>
            <div>
              <h2 className="text-base font-bold text-text">
                {currentQ?.title}
              </h2>
              <p className="text-[10px] text-text-secondary mt-0.5">{currentQ?.chapter}</p>
            </div>
          </div>
          <div className="text-sm text-text leading-relaxed whitespace-pre-line font-[family-name:var(--font-body)]">
            {currentQ?.story}
          </div>
        </div>

        {/* 问题卡片 */}
        {currentQ && (
          <div className="dao-card" style={{ borderColor: "rgba(201, 169, 110, 0.3)" }}>
            <p className="text-sm font-bold text-text mb-4">
              ❓ {currentQ.question}
            </p>

            <div className="space-y-2">
              {currentQ.options.map((opt, index) => {
                const isSelected = selected === index;
                const isThisCorrect = selected !== null && isCorrect && index === selected;

                let style = "border-border hover:border-gold/50";
                if (isSelected && isCorrect) style = "border-green bg-green/5 ring-1 ring-dao-jade/30";
                else if (isSelected && isCorrect === false) style = "border-accent bg-accent/5 ring-1 ring-dao-red/30";

                return (
                  <button key={index}
                    onClick={() => handleSelect(index)}
                    disabled={selected !== null}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg border
                               transition-all duration-200 tap-active ${style}`}>
                    <span className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center
                                     justify-center text-xs font-bold border
                                     ${isSelected
                                       ? isCorrect
                                         ? "bg-green text-white border-green"
                                         : "bg-accent text-white border-accent"
                                       : "bg-bg-subtle text-text border-border"}`}>
                      {isSelected && isCorrect ? <Check size={14} />
                        : isSelected && isCorrect === false ? <X size={14} />
                          : opt.label}
                    </span>
                    <span className="text-sm text-text text-left">{opt.text}</span>
                  </button>
                );
              })}
            </div>

            {/* 结果反馈 */}
            <AnimatePresence>
              {selected !== null && (
                <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mt-4">
                  {isCorrect ? (
                    <div className="bg-green/10 border border-green/30 rounded-lg p-4">
                      <p className="text-sm font-bold text-green mb-2">✅ 断案正确！</p>
                      {classicalRef && (
                        <div className="classical-quote text-sm">{classicalRef}</div>
                      )}
                      {mentorLoading && <p className="text-xs text-text-secondary mt-2 flex items-center gap-1">
                        <Loader2 size={12} className="animate-spin" />AI导师点评中...</p>}
                      {mentorHint && <p className="text-sm text-text mt-3 leading-relaxed whitespace-pre-line">{mentorHint}</p>}
                      <button onClick={nextQuestion} disabled={currentIdx >= questions.length - 1}
                        className="mt-3 flex items-center gap-1 text-sm text-accent font-medium tap-active">
                        <ChevronRight size={16} /> {currentIdx >= questions.length - 1 ? "已是最后一题" : "进入下一案"}
                      </button>
                    </div>
                  ) : (
                    <div className="bg-accent/10 border border-accent/30 rounded-lg p-4">
                      <p className="text-sm font-bold text-accent mb-2">❌ 还需推敲</p>
                      {mentorLoading && <p className="text-xs text-text-secondary flex items-center gap-1">
                        <Loader2 size={12} className="animate-spin" />AI导师提示中...</p>}
                      {mentorHint && <p className="text-sm text-text leading-relaxed whitespace-pre-line">{mentorHint}</p>}
                      <button onClick={resetQuestion} className="mt-2 text-sm text-accent font-medium tap-active">
                        重新作答
                      </button>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}
