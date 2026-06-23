"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/auth-context";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: "📊" },
  { href: "/learn", label: "Learn", icon: "🎓" },
  { href: "/transactions", label: "Transactions", icon: "💳" },
  { href: "/budgets", label: "Budgets", icon: "🎯" },
  { href: "/notifications", label: "Notifications", icon: "🔔" },
];

export function AppSidebar() {
  const pathname = usePathname();
  const { logout } = useAuth();

  return (
    <aside className="bg-card hidden w-60 shrink-0 flex-col border-r md:flex">
      <div className="flex h-16 items-center gap-2 border-b px-6">
        <span className="text-xl">🌱</span>
        <span className="font-semibold tracking-tight">Financial Wellness</span>
      </div>
      <nav className="flex flex-1 flex-col gap-1 p-3">
        {NAV_ITEMS.map((item) => {
          const active =
            pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
              )}
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t p-3">
        <Button
          variant="ghost"
          className="text-muted-foreground hover:text-foreground w-full justify-start gap-3"
          onClick={logout}
        >
          <span className="text-base">🚪</span>
          Sign out
        </Button>
      </div>
    </aside>
  );
}
