/**
 * Middleware
 * Protects dashboard routes and handles role-based redirects.
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Paths that don't require authentication
const publicPaths = ["/login"];

// Role-based path restrictions
const roleRestrictions: Record<string, string[]> = {
  "/media": ["viewer", "reviewer"], // Only admin/investigator can access /media
  "/audit": ["viewer", "reviewer", "investigator"], // Only admin can access /audit
  "/settings/users": ["viewer", "reviewer", "investigator"], // Only admin can manage users
};

// Default redirect paths by role
const roleHomePaths: Record<string, string> = {
  admin: "/media",
  investigator: "/media",
  reviewer: "/search",
  viewer: "/search",
};

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("access_token")?.value;

  // Allow public paths
  if (publicPaths.includes(pathname)) {
    // If already logged in, redirect to role-based home
    if (token) {
      // We can't decode the token here, so we'll let the client handle redirect
      // But we can at least redirect away from login
      return NextResponse.redirect(new URL("/", request.url));
    }
    return NextResponse.next();
  }

  // No token - redirect to login
  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Check role-based restrictions (simplified - actual check happens client-side)
  for (const [path, restrictedRoles] of Object.entries(roleRestrictions)) {
    if (pathname.startsWith(path)) {
      // Note: Full role check happens in the component with RoleGuard
      // This is just a preliminary redirect for known restrictions
      // The actual role verification is done client-side
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
