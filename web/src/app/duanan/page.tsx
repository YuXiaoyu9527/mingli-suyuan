"use client";

import { useState } from "react";
import BottomNav from "@/components/BottomNav";
import { askMentor } from "@/lib/api";
import { Swords, ChevronRight, Check, X, Lightbulb, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

// 示例题目
interface Question {
  id: number;
  title: string;
  chapter: string;
  story: string;
  question: string;
  options: { label: string; text: string; hint: string }[];
  correct: number;
  classicalRef: string;
}

const sampleQuestion: Question = {
  id: 4,
  title: "火焚衙门",
  chapter: "第一章 · 阴阳五行",
  story:
    "乾隆四十二年，苏州。巡抚衙门连年失火，三任巡抚皆被烧得焦头烂额。有人举荐一位江西风水先生来看。先生绕衙三日，抚须道：\n\n" +
    '"大人请看——这衙门正门朱漆大红，门朝正南。南为离卦，属火；门色赤红，亦属火。双火相叠，是以招火灾。"',
  question: "按五行生克，改门为何色可破此局？",
  options: [
    { label: "A", text: "青色（木）", hint: "木能生火" },
    { label: "B", text: "黄色（土）", hint: "火能生土" },
    { label: "C", text: "白色（金）", hint: "火能克金" },
    { label: "D", text: "黑色（水）", hint: "水能克火" },
  ],
  correct: 3, // D
  classicalRef: '《三命通会·卷一》：“五行相克，水能克火，火能克金……”',
};

export default function DuananPage() {
  const [selected, setSelected] = useState<number | null>(null);
  const [showHint, setShowHint] = useState(false);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [mentorHint, setMentorHint] = useState<string>("");
  const [mentorLoading, setMentorLoading] = useState(false);

  const handleSelect = async (index: number) => {
    if (selected !== null) return;
    setSelected(index);
    const correct = index === sampleQuestion.correct;
    setIsCorrect(correct);

    // 调用AI导师
    setMentorLoading(true);
    try {
      const studentAnswer = sampleQuestion.options[index].text;
      const correctAnswer = sampleQuestion.options[sampleQuestion.correct].text;
      const data = await askMentor(
        `${sampleQuestion.story}\n\n${sampleQuestion.question}`,
        studentAnswer,
        correctAnswer,
      );
      setMentorHint(data.hint || "");
    } catch {
      // 后端未启动时显示本地提示
    }
    setMentorLoading(false);
  };

  const handleReset = () => {
    setSelected(null);
    setShowHint(false);
    setIsCorrect(null);
    setMentorHint("");
  };

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      {/* 顶部 */}
      <header className="px-5 pt-10 pb-2">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl text-vermillion font-[family-name:var(--font-display)] tracking-wider">
            断案录
          </h1>
          <span className="text-xs text-aged bg-parchment-dark px-2.5 py-1 rounded-full">
            {sampleQuestion.chapter}
          </span>
        </div>
        {/* 进度条 */}
        <div className="mt-3 flex items-center gap-2">
          <span className="text-[11px] text-aged-light min-w-[48px]">
            第 {sampleQuestion.id}/10 题
          </span>
          <div className="flex-1 h-1.5 bg-parchment-dark rounded-full overflow-hidden">
            <div
              className="h-full bg-gold rounded-full transition-all duration-500"
              style={{ width: `${(sampleQuestion.id / 10) * 100}%` }}
            />
          </div>
          <span className="text-[11px] text-gold font-medium">40%</span>
        </div>
      </header>

      <div className="px-5 flex-1 space-y-4 mt-2">
        {/* 故事卡片 */}
        <div className="card-ancient">
          <div className="flex items-start gap-3 mb-3">
            <div className="seal-mark flex-shrink-0 mt-1">案</div>
            <div>
              <h2 className="text-base font-bold text-ink">
                {sampleQuestion.title}
              </h2>
            </div>
          </div>
          <div className="text-sm text-ink-light leading-relaxed whitespace-pre-line font-[family-name:var(--font-body)]">
            {sampleQuestion.story}
          </div>
        </div>

        {/* 问题卡片 */}
        <div className="card-ancient border-gold/30">
          <p className="text-sm font-bold text-ink mb-4">
            ❓ {sampleQuestion.question}
          </p>

          {/* 选项 */}
          <div className="space-y-2.5">
            {sampleQuestion.options.map((opt, index) => {
              const isSelected = selected === index;
              const isThisCorrect = index === sampleQuestion.correct;
              let optionStyle = "border-parchment-darker hover:border-gold/50 hover:bg-gold/5";

              if (isSelected && isThisCorrect) {
                optionStyle =
                  "border-auspicious bg-auspicious/5 ring-1 ring-auspicious/30";
              } else if (isSelected && !isThisCorrect) {
                optionStyle =
                  "border-inauspicious bg-inauspicious/5 ring-1 ring-inauspicious/30";
              } else if (selected !== null && isThisCorrect) {
                optionStyle =
                  "border-auspicious bg-auspicious/5";
              }

              return (
                <button
                  key={index}
                  onClick={() => handleSelect(index)}
                  disabled={selected !== null}
                  className={`w-full flex items-center gap-3 p-3.5 rounded-lg border
                             transition-all duration-200 tap-active
                             ${optionStyle}`}
                >
                  <span
                    className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center
                               justify-center text-xs font-bold border
                               ${isSelected
                                 ? isThisCorrect
                                   ? "bg-auspicious text-white border-auspicious"
                                   : "bg-inauspicious text-white border-inauspicious"
                                 : "bg-parchment-dark text-ink-light border-parchment-darker"
                               }`}
                  >
                    {isSelected && isThisCorrect ? (
                      <Check size={14} />
                    ) : isSelected && !isThisCorrect ? (
                      <X size={14} />
                    ) : (
                      opt.label
                    )}
                  </span>
                  <span className="text-sm text-ink text-left">{opt.text}</span>
                  {opt.hint && (
                    <span className="ml-auto text-[11px] text-aged-light hidden sm:inline">
                      {opt.hint}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {/* 结果反馈 */}
          <AnimatePresence>
            {selected !== null && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                className="mt-4"
              >
                {isCorrect ? (
                  <div className="bg-auspicious/10 border border-auspicious/30 rounded-lg p-4">
                    <p className="text-sm font-bold text-auspicious mb-2">
                      ✅ 断案正确！
                    </p>
                    <div className="classical-quote text-sm">
                      {sampleQuestion.classicalRef}
                    </div>
                    {mentorLoading && <p className="text-xs text-aged mt-2"><Loader2 size={12} className="inline animate-spin" /> AI导师点评中...</p>}
                    {mentorHint && <p className="text-sm text-ink-light mt-3 leading-relaxed whitespace-pre-line">{mentorHint}</p>}
                    <button onClick={handleReset}
                      className="mt-3 flex items-center gap-1 text-sm text-vermillion font-medium tap-active">
                      <ChevronRight size={16} /> 进入下一案
                    </button>
                  </div>
                ) : (
                  <div className="bg-inauspicious/10 border border-inauspicious/30 rounded-lg p-4">
                    <p className="text-sm font-bold text-inauspicious mb-2">
                      ❌ 还需推敲
                    </p>
                    {mentorLoading && <p className="text-xs text-aged mt-2"><Loader2 size={12} className="inline animate-spin" /> AI导师提示中...</p>}
                    {mentorHint && <p className="text-sm text-ink-light mt-2 leading-relaxed whitespace-pre-line">{mentorHint}</p>}
                    <button onClick={handleReset} className="mt-2 text-sm text-vermillion font-medium tap-active">
                      重新作答
                    </button>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* AI 导师提示 */}
        {showHint && selected === null && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="card-ancient border-indigo-traditional/20 bg-indigo-traditional/5"
          >
            <div className="flex items-start gap-2">
              <Lightbulb size={16} className="text-gold mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-aged mb-1">导师提示</p>
                <p className="text-sm text-ink-light">
                  你想想——厨房起火了，你是泼一盆水上去，还是拿扇子使劲扇？
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {/* 提示按钮 */}
        {selected === null && (
          <div className="text-center">
            <button
              onClick={() => setShowHint(!showHint)}
              className="text-sm text-indigo-traditional tap-active
                         hover:text-indigo-light transition-colors"
            >
              {showHint ? "隐藏提示" : "💡 需要导师提示"}
            </button>
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}
