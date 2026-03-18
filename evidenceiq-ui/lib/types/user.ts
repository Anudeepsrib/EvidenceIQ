/**
 * User Types
 * TypeScript interfaces for user management.
 */

import type { Role } from "./auth";

export interface User {
  id: string;
  username: string;
  email: string;
  role: Role;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export interface CreateUserRequest {
  username: string;
  email: string;
  password: string;
  role: Role;
}

export interface UpdateUserRequest {
  email?: string;
  role?: Role;
  is_active?: boolean;
}

export interface UserListResponse {
  users: User[];
  total: number;
  page: number;
  page_size: number;
}

export interface UserStats {
  total_users: number;
  by_role: Record<Role, number>;
  active_users: number;
  inactive_users: number;
}

export interface ChangeRoleRequest {
  new_role: Role;
  reason: string;
}

export interface DeactivateUserRequest {
  reason: string;
}
