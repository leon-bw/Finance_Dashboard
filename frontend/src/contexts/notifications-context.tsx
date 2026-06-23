"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { getUnreadCount } from "@/lib/api";

interface NotificationsContextValue {
  unreadCount: number;
  refresh: () => Promise<void>;
}

const NotificationsContext = createContext<
  NotificationsContextValue | undefined
>(undefined);

const POLL_INTERVAL_MS = 30_000;

export function NotificationsProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [unreadCount, setUnreadCount] = useState(0);

  const refresh = useCallback(async () => {
    try {
      setUnreadCount(await getUnreadCount());
    } catch {
      /* ignore transient errors */
    }
  }, []);

  useEffect(() => {
    void Promise.resolve().then(refresh);
    const id = window.setInterval(() => void refresh(), POLL_INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [refresh]);

  const value = useMemo(
    () => ({ unreadCount, refresh }),
    [unreadCount, refresh],
  );

  return (
    <NotificationsContext.Provider value={value}>
      {children}
    </NotificationsContext.Provider>
  );
}

export function useNotifications(): NotificationsContextValue {
  const context = useContext(NotificationsContext);
  if (!context) {
    throw new Error(
      "useNotifications must be used within a NotificationsProvider",
    );
  }
  return context;
}
