/**
 * Settings Page
 * User settings and preferences.
 */

"use client";

import { Settings } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";

export default function SettingsPage() {
  return (
    <div>
      <PageHeader
        title="Settings"
        description="System and user preferences"
      />

      <div className="bg-surface border border-border rounded-lg p-8 text-center">
        <Settings className="w-12 h-12 text-text-tertiary mx-auto mb-4" />
        <p className="text-text-secondary">
          Settings functionality will be implemented here.
        </p>
        <p className="text-text-tertiary text-sm mt-2">
          Password change, preferences, and system configuration.
        </p>
      </div>
    </div>
  );
}
