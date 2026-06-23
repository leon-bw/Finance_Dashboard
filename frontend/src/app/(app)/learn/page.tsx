"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { getCourses } from "@/lib/api";
import type { CourseSummary } from "@/lib/types";

export default function LearnPage() {
  const [courses, setCourses] = useState<CourseSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCourses()
      .then(setCourses)
      .catch(() => {
        /* show empty state */
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Learn</h1>
        <p className="text-muted-foreground">
          Bite-sized courses to build your financial confidence.
        </p>
      </div>

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-44 w-full" />
          ))}
        </div>
      ) : courses.length === 0 ? (
        <Card>
          <CardContent className="text-muted-foreground py-12 text-center text-sm">
            No courses available yet. Check back soon!
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {courses.map((course) => (
            <Link key={course.id} href={`/learn/courses/${course.id}`}>
              <Card className="hover:border-primary/50 h-full transition-colors">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <span
                      className="flex h-11 w-11 items-center justify-center rounded-lg text-2xl"
                      style={{
                        backgroundColor: course.colour ?? "var(--muted)",
                      }}
                    >
                      {course.icon ?? "📘"}
                    </span>
                    <CardTitle>{course.title}</CardTitle>
                  </div>
                  {course.description && (
                    <p className="text-muted-foreground text-sm">
                      {course.description}
                    </p>
                  )}
                </CardHeader>
                <CardContent className="space-y-2">
                  <Progress value={course.progress_percentage} />
                  <p className="text-muted-foreground text-xs">
                    {course.completed_lessons}/{course.total_lessons} lessons
                    complete
                  </p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
