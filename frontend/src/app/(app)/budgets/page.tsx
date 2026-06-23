"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/contexts/auth-context";
import {
  createBudget,
  deleteBudget,
  getBudgets,
  getCategories,
  updateBudget,
} from "@/lib/api";
import type {
  Budget,
  BudgetPayload,
  BudgetPeriod,
  Category,
} from "@/lib/types";

const SELECT_CLASS =
  "border-input bg-transparent flex h-9 w-full rounded-md border px-3 py-1 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring/50";

const PERIODS: BudgetPeriod[] = ["daily", "weekly", "monthly", "yearly"];

interface FormState {
  amount: number;
  period: BudgetPeriod;
  category_id: string;
  start_date: string;
  end_date: string;
  alert_percent: number;
}

function emptyForm(): FormState {
  const start = new Date();
  const end = new Date();
  end.setDate(end.getDate() + 30);
  return {
    amount: 0,
    period: "monthly",
    category_id: "",
    start_date: start.toISOString().slice(0, 10),
    end_date: end.toISOString().slice(0, 10),
    alert_percent: 80,
  };
}

export default function BudgetsPage() {
  const { user } = useAuth();
  const currency = user?.currency_preference ?? "GBP";

  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Budget | null>(null);
  const [form, setForm] = useState<FormState>(emptyForm());
  const [saving, setSaving] = useState(false);

  function formatCurrency(value: number) {
    return new Intl.NumberFormat("en-GB", {
      style: "currency",
      currency,
    }).format(value);
  }

  function categoryName(id: string | null) {
    if (!id) return "Overall";
    return categories.find((c) => c.id === id)?.name ?? "Category";
  }

  async function load() {
    try {
      const [b, cats] = await Promise.all([getBudgets(), getCategories()]);
      setBudgets(b);
      setCategories(cats);
    } catch {
      toast.error("Could not load budgets");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void Promise.resolve().then(load);
  }, []);

  function openCreate() {
    setEditing(null);
    setForm(emptyForm());
    setDialogOpen(true);
  }

  function openEdit(budget: Budget) {
    setEditing(budget);
    setForm({
      amount: budget.amount,
      period: budget.period,
      category_id: budget.category_id ?? "",
      start_date: budget.start_date.slice(0, 10),
      end_date: budget.end_date.slice(0, 10),
      alert_percent: Math.round(budget.alert_threshold * 100),
    });
    setDialogOpen(true);
  }

  async function handleSave() {
    if (form.amount <= 0) {
      toast.error("Amount must be greater than zero");
      return;
    }
    if (new Date(form.end_date) <= new Date(form.start_date)) {
      toast.error("End date must be after start date");
      return;
    }
    setSaving(true);
    try {
      const payload: BudgetPayload = {
        amount: form.amount,
        period: form.period,
        category_id: form.category_id || null,
        start_date: new Date(form.start_date).toISOString(),
        end_date: new Date(form.end_date).toISOString(),
        alert_threshold: form.alert_percent / 100,
      };
      if (editing) {
        await updateBudget(editing.id, payload);
        toast.success("Budget updated");
      } else {
        await createBudget(payload);
        toast.success("Budget created");
      }
      setDialogOpen(false);
      await load();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Could not save budget");
    } finally {
      setSaving(false);
    }
  }

  async function handleToggleActive(budget: Budget) {
    try {
      await updateBudget(budget.id, { is_active: !budget.is_active });
      await load();
    } catch {
      toast.error("Could not update budget");
    }
  }

  async function handleDelete(budget: Budget) {
    if (!confirm("Delete this budget?")) return;
    try {
      await deleteBudget(budget.id);
      setBudgets((prev) => prev.filter((b) => b.id !== budget.id));
      toast.success("Budget deleted");
    } catch {
      toast.error("Could not delete budget");
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Budgets</h1>
          <p className="text-muted-foreground">
            Set spending limits and track your progress.
          </p>
        </div>
        <Button onClick={openCreate}>Create budget</Button>
      </div>

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-36 w-full" />
          ))}
        </div>
      ) : budgets.length === 0 ? (
        <Card>
          <CardContent className="text-muted-foreground py-12 text-center text-sm">
            No budgets yet. Create one to start tracking your spending limits.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {budgets.map((budget) => (
            <Card key={budget.id}>
              <CardContent className="space-y-3 py-5">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium">{categoryName(budget.category_id)}</p>
                    <p className="text-muted-foreground text-sm capitalize">
                      {budget.period}
                    </p>
                  </div>
                  <Badge variant={budget.is_active ? "default" : "secondary"}>
                    {budget.is_active ? "Active" : "Inactive"}
                  </Badge>
                </div>
                <p className="text-2xl font-semibold">
                  {formatCurrency(budget.amount)}
                </p>
                <p className="text-muted-foreground text-xs">
                  {new Date(budget.start_date).toLocaleDateString("en-GB")} –{" "}
                  {new Date(budget.end_date).toLocaleDateString("en-GB")} · alert
                  at {Math.round(budget.alert_threshold * 100)}%
                </p>
                <div className="flex gap-2 pt-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => openEdit(budget)}
                  >
                    Edit
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleToggleActive(budget)}
                  >
                    {budget.is_active ? "Deactivate" : "Activate"}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(budget)}
                  >
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editing ? "Edit budget" : "Create budget"}
            </DialogTitle>
            <DialogDescription>
              Set an amount, period and optional category.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="amount">Amount</Label>
                <Input
                  id="amount"
                  type="number"
                  min="0"
                  step="0.01"
                  value={form.amount || ""}
                  onChange={(e) =>
                    setForm({ ...form, amount: Number(e.target.value) })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="period">Period</Label>
                <select
                  id="period"
                  className={SELECT_CLASS}
                  value={form.period}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      period: e.target.value as BudgetPeriod,
                    })
                  }
                >
                  {PERIODS.map((p) => (
                    <option key={p} value={p} className="capitalize">
                      {p}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <select
                id="category"
                className={SELECT_CLASS}
                value={form.category_id}
                onChange={(e) =>
                  setForm({ ...form, category_id: e.target.value })
                }
              >
                <option value="">Overall (no category)</option>
                {categories
                  .filter((c) => c.type === "expense")
                  .map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.icon ? `${c.icon} ` : ""}
                      {c.name}
                    </option>
                  ))}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="start_date">Start date</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={form.start_date}
                  onChange={(e) =>
                    setForm({ ...form, start_date: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end_date">End date</Label>
                <Input
                  id="end_date"
                  type="date"
                  value={form.end_date}
                  onChange={(e) =>
                    setForm({ ...form, end_date: e.target.value })
                  }
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="alert">Alert threshold (%)</Label>
              <Input
                id="alert"
                type="number"
                min="0"
                max="100"
                value={form.alert_percent}
                onChange={(e) =>
                  setForm({ ...form, alert_percent: Number(e.target.value) })
                }
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDialogOpen(false)}
              disabled={saving}
            >
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              {saving ? "Saving…" : "Save"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
