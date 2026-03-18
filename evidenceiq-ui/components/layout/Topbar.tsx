/**
 * Topbar Component
 * Top navigation bar with user info and logout.
 */

"use client";

import { useRouter } from "next/navigation";
import { User, LogOut } from "lucide-react";
import { toast } from "sonner";

import { useAuthStore } from "@/lib/stores/authStore";
import { api } from "@/lib/api/auth";

export function Topbar() {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    try {
      await api.logout();
    } catch (error) {
      // Ignore error, client-side logout still happens
    } finally {
      logout();
      router.push("/login");
      toast.success("Logged out successfully");
    }
  };

  if (!user) return null;

  return (
    <header className="h-16 bg-surface border-b border-border flex items-center justify-between px-6 ml-14 lg:ml-56">
      {/* Left: Breadcrumbs or page title could go here */}
      <div />

      {/* Right: User info and actions */}
      <div className="flex items-center gap-4">
        {/* User info */}
        <div className="flex items-center gap-2 text-sm">
          <div className="w-8 h-8 rounded-full bg-accent-muted flex items-center justify-center">
            <User className="w-4 h-4 text-accent" />
          </div>
          <div className="hidden sm:block">
            <p className="font-medium text-text-primary">{user.username}</p>
            <p className="text-xs text-text-secondary font-mono uppercase">
              {user.role}
            </p>
          </div>
        </div>

        {/* Logout button */}
        <button
          onClick={handleLogout}
          className="p-2 text-text-secondary hover:text-error transition-colors"
          title="Logout"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
}
