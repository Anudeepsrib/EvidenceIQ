/**
 * Login Form Component
 * Secure terminal-style login with role-based redirects.
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

import { cn } from "@/lib/utils/cn";
import { useAuthStore } from "@/lib/stores/authStore";
import { api } from "@/lib/api/auth";
import type { Role } from "@/lib/types/auth";

const loginSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginForm() {
  const router = useRouter();
  const setUser = useAuthStore((state) => state.setUser);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      const response = await api.login(data);
      
      // Store tokens
      localStorage.setItem("access_token", response.access_token);
      localStorage.setItem("refresh_token", response.refresh_token);
      
      // Set user in store
      setUser(response.user);
      
      toast.success("Login successful");
      
      // Role-based redirect
      const role = response.user.role;
      const redirectPath = getRedirectPath(role);
      router.push(redirectPath);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  const getRedirectPath = (role: Role): string => {
    switch (role) {
      case "admin":
      case "investigator":
        return "/media";
      case "reviewer":
      case "viewer":
        return "/search";
      default:
        return "/search";
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label
          htmlFor="username"
          className="block text-xs font-mono uppercase tracking-widest text-text-tertiary mb-2"
        >
          Operator ID
        </label>
        <input
          id="username"
          type="text"
          {...register("username")}
          className="w-full px-4 py-3 bg-surface-raised border border-border rounded text-text-primary placeholder-text-tertiary focus:outline-none focus:ring-1 focus:ring-accent/50 focus:border-accent transition-all duration-200"
          placeholder="Enter username..."
          disabled={isLoading}
        />
        {errors.username && (
          <p className="mt-1 text-[10px] text-error uppercase font-mono">{errors.username.message}</p>
        )}
      </div>

      <div>
        <label
          htmlFor="password"
          className="block text-xs font-mono uppercase tracking-widest text-text-tertiary mb-2"
        >
          Secure Key
        </label>
        <input
          id="password"
          type="password"
          {...register("password")}
          className="w-full px-4 py-3 bg-surface-raised border border-border rounded text-text-primary placeholder-text-tertiary focus:outline-none focus:ring-1 focus:ring-accent/50 focus:border-accent transition-all duration-200"
          placeholder="Enter password..."
          disabled={isLoading}
        />
        {errors.password && (
          <p className="mt-1 text-[10px] text-error uppercase font-mono">{errors.password.message}</p>
        )}
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="relative overflow-hidden w-full py-3 px-4 bg-accent hover:bg-accent-hover text-background font-bold rounded transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed group"
      >
        <span className={cn(
          "flex items-center justify-center gap-2 transition-transform duration-300",
          isLoading ? "opacity-0" : "group-hover:translate-x-1"
        )}>
          Authorize Access
        </span>
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <Loader2 className="w-5 h-5 animate-spin" />
          </div>
        )}
      </button>
    </form>
  );
}
