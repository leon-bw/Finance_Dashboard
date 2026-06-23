"use client";

import Link from "next/link";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/contexts/auth-context";
import { useNotifications } from "@/contexts/notifications-context";
import { cn } from "@/lib/utils";

export function AppTopbar() {
  const { user, logout } = useAuth();
  const { unreadCount } = useNotifications();

  const initials = user
    ? `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`.toUpperCase()
    : "?";

  return (
    <header className="flex h-16 items-center justify-between border-b px-6">
      <div className="md:hidden">
        <span className="font-semibold">🌱 Financial Wellness</span>
      </div>
      <div className="ml-auto flex items-center gap-2">
        <Link
          href="/notifications"
          aria-label="Notifications"
          className={cn(
            buttonVariants({ variant: "ghost", size: "icon" }),
            "relative",
          )}
        >
          <span className="text-lg">🔔</span>
          {unreadCount > 0 && (
            <Badge className="absolute -top-1 -right-1 h-5 min-w-5 justify-center rounded-full px-1 text-xs">
              {unreadCount > 9 ? "9+" : unreadCount}
            </Badge>
          )}
        </Link>

        <DropdownMenu>
          <DropdownMenuTrigger className="hover:bg-muted flex items-center gap-2 rounded-md px-2 py-1.5 outline-none">
            <Avatar className="h-8 w-8">
              <AvatarFallback>{initials}</AvatarFallback>
            </Avatar>
            <span className="hidden text-sm font-medium sm:inline">
              {user?.first_name}
            </span>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuLabel>
              {user?.first_name} {user?.last_name}
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout}>Sign out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
