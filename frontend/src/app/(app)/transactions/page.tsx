"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/contexts/auth-context";
import {
  createTransaction,
  deleteTransaction,
  getCategories,
  getTransactions,
  updateTransaction,
} from "@/lib/api";
import type {
  Category,
  EntryType,
  Transaction,
  TransactionPayload,
} from "@/lib/types";

const SELECT_CLASS =
  "border-input bg-transparent flex h-9 w-full rounded-md border px-3 py-1 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring/50";

function emptyForm(): TransactionPayload {
  return {
    description: "",
    amount: 0,
    type: "expense",
    category: "",
    account: "Main Account",
    date: new Date().toISOString().slice(0, 10),
  };
}

export default function TransactionsPage() {
  const { user } = useAuth();
  const currency = user?.currency_preference ?? "GBP";

  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Transaction | null>(null);
  const [form, setForm] = useState<TransactionPayload>(emptyForm());
  const [saving, setSaving] = useState(false);

  function formatCurrency(value: number) {
    return new Intl.NumberFormat("en-GB", {
      style: "currency",
      currency,
    }).format(value);
  }

  async function load() {
    try {
      const [tx, cats] = await Promise.all([
        getTransactions(),
        getCategories(),
      ]);
      setTransactions(tx);
      setCategories(cats);
    } catch {
      toast.error("Could not load transactions");
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

  function openEdit(tx: Transaction) {
    setEditing(tx);
    setForm({
      description: tx.description,
      amount: tx.amount,
      type: tx.type,
      category: tx.category,
      account: tx.account,
      date: tx.date.slice(0, 10),
    });
    setDialogOpen(true);
  }

  async function handleSave() {
    if (!form.description || !form.category || form.amount <= 0) {
      toast.error("Please fill in description, amount and category");
      return;
    }
    setSaving(true);
    try {
      const payload: TransactionPayload = {
        ...form,
        date: form.date ? new Date(form.date).toISOString() : null,
      };
      if (editing) {
        await updateTransaction(editing.id, payload);
        toast.success("Transaction updated");
      } else {
        await createTransaction(payload);
        toast.success("Transaction added");
      }
      setDialogOpen(false);
      await load();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Could not save");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(tx: Transaction) {
    if (!confirm(`Delete "${tx.description}"?`)) return;
    try {
      await deleteTransaction(tx.id);
      setTransactions((prev) => prev.filter((t) => t.id !== tx.id));
      toast.success("Transaction deleted");
    } catch {
      toast.error("Could not delete transaction");
    }
  }

  const categoryOptions = categories.filter((c) => c.type === form.type);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Transactions
          </h1>
          <p className="text-muted-foreground">
            Track your income and expenses.
          </p>
        </div>
        <Button onClick={openCreate}>Add transaction</Button>
      </div>

      {loading ? (
        <Skeleton className="h-72 w-full" />
      ) : transactions.length === 0 ? (
        <Card>
          <CardContent className="text-muted-foreground py-12 text-center text-sm">
            No transactions yet. Add your first one to get started.
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {transactions.map((tx) => (
                  <TableRow key={tx.id}>
                    <TableCell className="text-muted-foreground">
                      {new Date(tx.date).toLocaleDateString("en-GB")}
                    </TableCell>
                    <TableCell className="font-medium">
                      {tx.description}
                    </TableCell>
                    <TableCell>{tx.category}</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          tx.type === "income" ? "default" : "secondary"
                        }
                      >
                        {tx.type}
                      </Badge>
                    </TableCell>
                    <TableCell
                      className={
                        tx.type === "income"
                          ? "text-right font-medium text-emerald-600"
                          : "text-right font-medium"
                      }
                    >
                      {tx.type === "income" ? "+" : "-"}
                      {formatCurrency(tx.amount)}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openEdit(tx)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(tx)}
                      >
                        Delete
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editing ? "Edit transaction" : "Add transaction"}
            </DialogTitle>
            <DialogDescription>
              {editing
                ? "Update the details of this transaction."
                : "Record a new income or expense."}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                value={form.description}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
              />
            </div>
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
                <Label htmlFor="type">Type</Label>
                <select
                  id="type"
                  className={SELECT_CLASS}
                  value={form.type}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      type: e.target.value as EntryType,
                      category: "",
                    })
                  }
                >
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <select
                  id="category"
                  className={SELECT_CLASS}
                  value={form.category}
                  onChange={(e) =>
                    setForm({ ...form, category: e.target.value })
                  }
                >
                  <option value="">Select…</option>
                  {categoryOptions.map((c) => (
                    <option key={c.id} value={c.name}>
                      {c.icon ? `${c.icon} ` : ""}
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="date">Date</Label>
                <Input
                  id="date"
                  type="date"
                  value={form.date ?? ""}
                  onChange={(e) => setForm({ ...form, date: e.target.value })}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="account">Account</Label>
              <Input
                id="account"
                value={form.account}
                onChange={(e) => setForm({ ...form, account: e.target.value })}
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
