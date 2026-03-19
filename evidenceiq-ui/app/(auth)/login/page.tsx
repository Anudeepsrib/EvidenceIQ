/**
 * Login Page
 * Secure institutional-style login with brand assets and animations.
 */

import { LoginForm } from "@/components/auth/LoginForm";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-background scanlines flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-in fade-in slide-in-from-bottom-4 duration-700">
        {/* Logo Section */}
        <div className="text-center mb-10 flex flex-col items-center">
          <div className="w-16 h-16 mb-4 animate-in zoom-in duration-1000 delay-200">
            <img
              src="/logo.png"
              alt="EvidenceIQ"
              className="w-full h-full object-contain"
            />
          </div>
          <h1 className="font-heading italic text-4xl text-accent mb-1 animate-in fade-in slide-in-from-top-2 duration-700 delay-300">
            Evidence
            <span className="font-mono not-italic text-text-primary">IQ</span>
          </h1>
          <p className="text-text-secondary text-sm mb-6 animate-in fade-in duration-1000 delay-500">
            Secure Local Multimodal Intelligence
          </p>
          <div className="w-12 h-0.5 bg-accent opacity-50 animate-in fade-in duration-1000 delay-700" />
        </div>

        {/* Login Card */}
        <div className="bg-surface border border-border rounded-lg p-8 shadow-2xl animate-in fade-in zoom-in-95 duration-500 delay-700">
          <LoginForm />
        </div>

        {/* Footer info */}
        <div className="mt-10 space-y-2 text-center animate-in fade-in duration-1000 delay-1000">
          <p className="text-text-tertiary text-[10px] uppercase tracking-[0.2em]">
            Institutional Access Only
          </p>
          <p className="text-text-tertiary text-xs">
            © 2026 EvidenceIQ Platform
          </p>
        </div>
      </div>
    </div>
  );
}
