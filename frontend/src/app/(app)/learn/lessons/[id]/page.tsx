"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { useNotifications } from "@/contexts/notifications-context";
import { getLesson, submitLesson } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { Lesson, LessonResult } from "@/lib/types";

export default function LessonPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { refresh } = useNotifications();

  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [loading, setLoading] = useState(true);
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [selected, setSelected] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<LessonResult | null>(null);

  useEffect(() => {
    if (!params.id) return;
    getLesson(params.id)
      .then(setLesson)
      .catch(() => toast.error("Could not load lesson"))
      .finally(() => setLoading(false));
  }, [params.id]);

  const questions = lesson?.questions ?? [];
  const current = questions[index];
  const isLast = index === questions.length - 1;
  const progress = useMemo(
    () => (questions.length ? (index / questions.length) * 100 : 0),
    [index, questions.length],
  );

  async function handleNext() {
    if (!current || selected == null) return;
    const nextAnswers = { ...answers, [current.id]: selected };
    setAnswers(nextAnswers);

    if (!isLast) {
      setIndex((i) => i + 1);
      setSelected(null);
      return;
    }

    setSubmitting(true);
    try {
      const payload = Object.entries(nextAnswers).map(
        ([question_id, answer]) => ({ question_id, answer }),
      );
      const res = await submitLesson(params.id, payload);
      setResult(res);
      await refresh();
    } catch {
      toast.error("Could not submit lesson");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-xl space-y-4">
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="mx-auto max-w-xl">
        <p className="text-muted-foreground">Lesson not found.</p>
        <Link href="/learn" className="text-primary text-sm">
          Back to learning
        </Link>
      </div>
    );
  }

  function handleRetry() {
    setResult(null);
    setAnswers({});
    setSelected(null);
    setIndex(0);
  }

  if (result) {
    return (
      <LessonResultView
        lesson={lesson}
        result={result}
        onRetry={handleRetry}
        onExit={() => router.push("/learn")}
      />
    );
  }

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Link href="/learn" className="text-muted-foreground text-sm">
            ✕ Exit
          </Link>
          <span className="text-muted-foreground text-sm">
            {index + 1} / {questions.length}
          </span>
        </div>
        <Progress value={progress} />
      </div>

      {current && (
        <Card>
          <CardContent className="space-y-6 py-6">
            <h2 className="text-lg font-semibold">{current.prompt}</h2>
            <div className="grid gap-3">
              {(current.options ?? ["True", "False"]).map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setSelected(option)}
                  className={cn(
                    "rounded-lg border-2 px-4 py-3 text-left text-sm font-medium transition-colors",
                    selected === option
                      ? "border-primary bg-primary/10"
                      : "border-border hover:bg-muted",
                  )}
                >
                  {option}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Button
        className="w-full"
        size="lg"
        disabled={selected == null || submitting}
        onClick={handleNext}
      >
        {submitting ? "Checking…" : isLast ? "Finish" : "Next"}
      </Button>
    </div>
  );
}

function LessonResultView({
  lesson,
  result,
  onRetry,
  onExit,
}: {
  lesson: Lesson;
  result: LessonResult;
  onRetry: () => void;
  onExit: () => void;
}) {
  const questionsById = Object.fromEntries(
    lesson.questions.map((q) => [q.id, q]),
  );

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <Card className={result.passed ? "border-primary/40 bg-primary/5" : ""}>
        <CardContent className="space-y-3 py-8 text-center">
          <div className="text-5xl">{result.passed ? "🎉" : "💪"}</div>
          <h1 className="text-2xl font-semibold">
            {result.passed ? "Lesson complete!" : "Almost there!"}
          </h1>
          <p className="text-muted-foreground">
            You scored {result.score}% ({result.correct_count}/
            {result.total_questions} correct)
          </p>
          <div className="flex justify-center gap-6 pt-2">
            <Stat icon="✨" label="XP earned" value={`+${result.xp_earned}`} />
            <Stat icon="🔥" label="Streak" value={result.stats.current_streak} />
            <Stat icon="⭐" label="Level" value={result.stats.level} />
          </div>
          {!result.passed && (
            <p className="text-muted-foreground text-sm">
              You need 80% to pass. Review the answers below and try again!
            </p>
          )}
        </CardContent>
      </Card>

      <div className="space-y-3">
        <h2 className="font-semibold">Review</h2>
        {result.results.map((r) => {
          const question = questionsById[r.question_id];
          return (
            <Card key={r.question_id}>
              <CardContent className="space-y-1 py-4">
                <div className="flex items-start gap-2">
                  <span>{r.correct ? "✅" : "❌"}</span>
                  <p className="font-medium">{question?.prompt}</p>
                </div>
                {!r.correct && (
                  <p className="text-muted-foreground pl-6 text-sm">
                    Correct answer: <strong>{r.correct_answer}</strong>
                  </p>
                )}
                {r.explanation && (
                  <p className="text-muted-foreground pl-6 text-sm">
                    {r.explanation}
                  </p>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="flex gap-3">
        <Button variant="outline" className="flex-1" onClick={onRetry}>
          Retry
        </Button>
        <Button className="flex-1" onClick={onExit}>
          Back to learning
        </Button>
      </div>
    </div>
  );
}

function Stat({
  icon,
  label,
  value,
}: {
  icon: string;
  label: string;
  value: string | number;
}) {
  return (
    <div className="flex flex-col items-center">
      <span className="text-xl">{icon}</span>
      <span className="font-semibold">{value}</span>
      <span className="text-muted-foreground text-xs">{label}</span>
    </div>
  );
}
