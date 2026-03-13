"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  Sparkles,
  ListChecks,
  Film,
} from "lucide-react";
import { APP_NAME, NAV_ITEMS } from "@/lib/constants";

const ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  LayoutDashboard,
  Users,
  Sparkles,
  ListChecks,
  Film,
};

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-60 flex-col border-r border-border bg-bg-secondary">
      {/* Logo */}
      <div className="flex items-center gap-2 px-5 py-5">
        <span className="text-xl">🍒</span>
        <span className="text-lg font-bold text-text-primary">{APP_NAME}</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-2">
        {NAV_ITEMS.map((item) => {
          const Icon = ICONS[item.icon];
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-accent-cyan/10 text-accent-cyan"
                  : "text-text-secondary hover:bg-bg-tertiary hover:text-text-primary"
              }`}
            >
              {Icon && <Icon className="h-4 w-4" />}
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-border px-5 py-4">
        <p className="text-xs text-text-secondary">v1.0.0</p>
      </div>
    </aside>
  );
}
