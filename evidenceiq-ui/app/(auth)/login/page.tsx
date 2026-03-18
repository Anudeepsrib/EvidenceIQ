/**
 * Login Page
 * Secure terminal-style login with scanline texture.
 */

import { LoginForm } from "@/components/auth/LoginForm";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-background scanlines flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="font-heading italic text-3xl text-accent mb-2">
            Evidence
            <span className="font-mono not-italic text-text-primary">IQ</span>
          </h1>
          <p className="text-text-secondary text-sm mb-4">
            Sensitive media stays here.
          </p>
          <div className="w-16 h-0.5 bg-accent mx-auto" />
        </div>

        {/* Login Card */}
        <div className="bg-surface border border-border rounded-lg p-8 shadow-lg">
          <LoginForm />
        </div>

        {/* Footer */}
        <p className="text-center text-text-tertiary text-xs mt-8">
          Internal tool only. Authorized access required.
        </p>
      </div>
    </div>
  );
}
