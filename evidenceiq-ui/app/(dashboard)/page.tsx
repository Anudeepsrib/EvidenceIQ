import { redirect } from "next/navigation";

export default function DashboardRootPage() {
  // Redirect to media library by default
  // Actual role-based redirect happens client-side after auth check
  redirect("/media");
}
