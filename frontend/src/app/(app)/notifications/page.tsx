"use client";

import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { useNotifications } from "@/contexts/notifications-context";
import {
  getNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from "@/lib/api";
import type { AppNotification } from "@/lib/types";

function formatDate(value: string) {
  return new Date(value).toLocaleString("en-GB", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function NotificationsPage() {
  const { refresh } = useNotifications();
  const [items, setItems] = useState<AppNotification[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      setItems(await getNotifications());
    } catch {
      toast.error("Could not load notifications");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void Promise.resolve().then(load);
  }, [load]);

  async function handleMarkRead(id: string) {
    setItems((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)),
    );
    try {
      await markNotificationRead(id);
      await refresh();
    } catch {
      toast.error("Could not update notification");
    }
  }

  async function handleMarkAll() {
    setItems((prev) => prev.map((n) => ({ ...n, is_read: true })));
    try {
      await markAllNotificationsRead();
      await refresh();
      toast.success("All caught up!");
    } catch {
      toast.error("Could not update notifications");
    }
  }

  const hasUnread = items.some((n) => !n.is_read);

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Notifications
          </h1>
          <p className="text-muted-foreground">
            Your achievements, streaks and level ups.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleMarkAll}
          disabled={!hasUnread}
        >
          Mark all read
        </Button>
      </div>

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <Card>
          <CardContent className="text-muted-foreground py-12 text-center text-sm">
            No notifications yet. Complete a lesson to start earning achievements!
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {items.map((n) => (
            <Card
              key={n.id}
              className={cn(
                "transition-colors",
                !n.is_read && "border-primary/40 bg-primary/5",
              )}
            >
              <CardContent className="flex items-start gap-4 py-4">
                <span className="text-2xl">{n.icon ?? "🔔"}</span>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <p className="font-medium">{n.title}</p>
                    {!n.is_read && (
                      <span className="bg-primary h-2 w-2 rounded-full" />
                    )}
                  </div>
                  <p className="text-muted-foreground text-sm">{n.message}</p>
                  <p className="text-muted-foreground mt-1 text-xs">
                    {formatDate(n.created_at)}
                  </p>
                </div>
                {!n.is_read && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleMarkRead(n.id)}
                  >
                    Mark read
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
