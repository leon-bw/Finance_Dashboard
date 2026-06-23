"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { getCourse } from "@/lib/api";
import type { CourseDetail } from "@/lib/types";

export default function CourseDetailPage() {
  const params = useParams<{ id: string }>();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!params.id) return;
    getCourse(params.id)
      .then(setCourse)
      .catch(() => {
        /* show empty */
      })
      .finally(() => setLoading(false));
  }, [params.id]);

  if (loading) {
    return (
      <div className="mx-auto max-w-2xl space-y-4">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  if (!course) {
    return (
      <div className="mx-auto max-w-2xl">
        <p className="text-muted-foreground">Course not found.</p>
        <Link href="/learn" className="text-primary text-sm">
          Back to courses
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div>
        <Link href="/learn" className="text-muted-foreground text-sm">
          ← Back to courses
        </Link>
        <div className="mt-2 flex items-center gap-3">
          <span className="text-3xl">{course.icon ?? "📘"}</span>
          <h1 className="text-2xl font-semibold tracking-tight">
            {course.title}
          </h1>
        </div>
        {course.description && (
          <p className="text-muted-foreground mt-1">{course.description}</p>
        )}
      </div>

      {course.units.map((unit) => (
        <section key={unit.id} className="space-y-3">
          <div>
            <h2 className="font-semibold">{unit.title}</h2>
            {unit.description && (
              <p className="text-muted-foreground text-sm">
                {unit.description}
              </p>
            )}
          </div>
          <div className="space-y-2">
            {unit.lessons.map((lesson) => {
              const completed = lesson.status === "completed";
              return (
                <Link key={lesson.id} href={`/learn/lessons/${lesson.id}`}>
                  <Card
                    className={cn(
                      "hover:border-primary/50 transition-colors",
                      completed && "border-primary/40 bg-primary/5",
                    )}
                  >
                    <CardContent className="flex items-center justify-between py-4">
                      <div className="flex items-center gap-3">
                        <span className="text-xl">
                          {completed ? "✅" : "📖"}
                        </span>
                        <div>
                          <p className="font-medium">{lesson.title}</p>
                          <p className="text-muted-foreground text-xs">
                            {lesson.xp_reward} XP
                            {lesson.score != null &&
                              ` · best score ${lesson.score}%`}
                          </p>
                        </div>
                      </div>
                      {completed ? (
                        <Badge variant="secondary">Complete</Badge>
                      ) : (
                        <Badge>Start</Badge>
                      )}
                    </CardContent>
                  </Card>
                </Link>
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
}
