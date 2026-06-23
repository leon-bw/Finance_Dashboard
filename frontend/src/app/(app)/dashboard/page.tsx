"use client";

import { useEffect, useState } from "react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/contexts/auth-context";
import { getLearningStats, getQuickStats } from "@/lib/api";
import type { LearningStats, QuickStats } from "@/lib/types";

function formatCurrency(value: number, currency = "GBP") {
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency,
  }).format(value);
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<QuickStats | null>(null);
  const [learning, setLearning] = useState<LearningStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    Promise.all([getQuickStats(), getLearningStats()])
      .then(([quick, learn]) => {
        if (!active) return;
        setStats(quick);
        setLearning(learn);
      })
      .catch(() => {
        /* errors surface as empty state */
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const currency = user?.currency_preference ?? "GBP";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Welcome back, {user?.first_name} 👋
        </h1>
        <p className="text-muted-foreground">
          Here&apos;s a quick snapshot of your finances and learning.
        </p>
      </div>

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full" />
          ))}
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Net balance"
              value={formatCurrency(stats?.net_balance ?? 0, currency)}
              description="Income minus expenses"
            />
            <StatCard
              title="Total income"
              value={formatCurrency(stats?.total_income ?? 0, currency)}
              description="All recorded income"
            />
            <StatCard
              title="Total expenses"
              value={formatCurrency(stats?.total_expense ?? 0, currency)}
              description="All recorded spending"
            />
            <StatCard
              title="Budget remaining"
              value={
                stats?.budget_remaining != null
                  ? formatCurrency(stats.budget_remaining, currency)
                  : "—"
              }
              description={
                stats?.budget_spent_percentage != null
                  ? `${stats.budget_spent_percentage.toFixed(0)}% of budget used`
                  : "Set a monthly budget to track this"
              }
            />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Your learning journey</CardTitle>
              <CardDescription>
                Keep your streak alive and level up your money skills.
              </CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <Metric label="Level" value={learning?.level ?? 1} icon="⭐" />
              <Metric label="XP" value={learning?.xp_total ?? 0} icon="✨" />
              <Metric
                label="Day streak"
                value={learning?.current_streak ?? 0}
                icon="🔥"
              />
              <Metric label="Hearts" value={learning?.hearts ?? 0} icon="❤️" />
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}

function StatCard({
  title,
  value,
  description,
}: {
  title: string;
  value: string;
  description: string;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{title}</CardDescription>
        <CardTitle className="text-2xl">{value}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground text-xs">{description}</p>
      </CardContent>
    </Card>
  );
}

function Metric({
  label,
  value,
  icon,
}: {
  label: string;
  value: number;
  icon: string;
}) {
  return (
    <div className="bg-muted/40 flex flex-col items-center justify-center rounded-lg p-4 text-center">
      <span className="text-2xl">{icon}</span>
      <span className="mt-1 text-xl font-semibold">{value}</span>
      <span className="text-muted-foreground text-xs">{label}</span>
    </div>
  );
}
