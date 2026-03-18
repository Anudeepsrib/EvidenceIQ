/**
 * Sidebar Component
 * Role-aware navigation with collapsible sidebar.
 */

"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  FolderOpen,
  Search,
  FileText,
  Shield,
  Users,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

import { useAuthStore } from "@/lib/stores/authStore";
import { permissions } from "@/lib/utils/permissions";
import type { Role } from "@/lib/types/auth";
import { cn } from "@/lib/utils/cn";

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  permissionCheck: (role: Role) => boolean;
}

const navItems: NavItem[] = [
  {
    label: "Media Library",
    href: "/media",
    icon: FolderOpen,
    permissionCheck: permissions.canViewMedia,
  },
  {
    label: "Search",
    href: "/search",
    icon: Search,
    permissionCheck: permissions.canSearch,
  },
  {
    label: "Reports",
    href: "/reports",
    icon: FileText,
    permissionCheck: permissions.canViewReports,
  },
  {
    label: "Audit Log",
    href: "/audit",
    icon: Shield,
    permissionCheck: permissions.canViewAuditLog,
  },
  {
    label: "Users",
    href: "/settings/users",
    icon: Users,
    permissionCheck: permissions.canManageUsers,
  },
  {
    label: "Settings",
    href: "/settings",
    icon: Settings,
    permissionCheck: permissions.canViewMedia,
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const user = useAuthStore((state) => state.user);
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Load collapsed state from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("sidebar-collapsed");
    if (saved) {
      setIsCollapsed(saved === "true");
    }
  }, []);

  // Save collapsed state
  const toggleCollapsed = () => {
    const newState = !isCollapsed;
    setIsCollapsed(newState);
    localStorage.setItem("sidebar-collapsed", String(newState));
  };

  const role = user?.role;
  if (!role) return null;

  const visibleNavItems = navItems.filter((item) => item.permissionCheck(role));

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 h-screen bg-surface border-r border-border flex flex-col transition-all duration-200 z-50",
        isCollapsed ? "w-14" : "w-56"
      )}
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-center border-b border-border">
        <Link href="/" className="flex items-center gap-1">
          <span className="font-heading italic text-xl text-accent">
            E
          </span>
          {!isCollapsed && (
            <span className="font-mono text-lg text-text-primary">IQ</span>
          )}
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4">
        <ul className="space-y-1">
          {visibleNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname.startsWith(item.href);

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 text-sm transition-colors",
                    isActive
                      ? "border-l-2 border-accent text-accent bg-accent-muted"
                      : "border-l-2 border-transparent text-text-secondary hover:text-text-primary hover:bg-surface-raised",
                    isCollapsed && "justify-center px-2"
                  )}
                  title={isCollapsed ? item.label : undefined}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  {!isCollapsed && <span>{item.label}</span>}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Bottom section */}
      <div className="border-t border-border py-4">
        {/* Role badge */}
        <div
          className={cn(
            "mx-4 px-3 py-1.5 bg-surface-rounded border border-border rounded-full",
            isCollapsed && "mx-2 px-2"
          )}
        >
          <span
            className={cn(
              "font-mono text-xs uppercase tracking-wider text-accent",
              isCollapsed && "text-[10px]"
            )}
          >
            {isCollapsed ? role.slice(0, 2) : role}
          </span>
        </div>

        {/* Collapse toggle */}
        <button
          onClick={toggleCollapsed}
          className="mt-4 w-full flex items-center justify-center py-2 text-text-tertiary hover:text-text-secondary transition-colors"
          title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {isCollapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <ChevronLeft className="w-5 h-5" />
          )}
        </button>
      </div>
    </aside>
  );
}
