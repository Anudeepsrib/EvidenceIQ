"""
EvidenceIQ Authentication Tests
Comprehensive tests for auth endpoints and RBAC.
"""
import pytest
from fastapi import status

from app.auth.service import create_refresh_token, decode_token


class TestAuthentication:
    """Tests for /auth endpoints."""
    
    def test_health_check_no_auth(self, client):
        """Health check should not require authentication."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
        assert response.json()["version"] is not None
    
    def test_login_success(self, client, test_user):
        """Successful login returns tokens."""
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpassword123"}
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
    
    def test_login_invalid_username(self, client):
        """Login with non-existent username fails."""
        response = client.post(
            "/auth/login",
            json={"username": "nonexistent", "password": "password123"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["error"] == "authentication_failed"
    
    def test_login_invalid_password(self, client, test_user):
        """Login with wrong password fails."""
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["error"] == "authentication_failed"
    
    def test_login_inactive_user(self, client, inactive_user):
        """Login with inactive user fails."""
        response = client.post(
            "/auth/login",
            json={"username": "inactiveuser", "password": "inactivepassword123"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_me_success(self, client, test_user, auth_headers):
        """Get current user with valid token."""
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["role"] == "investigator"
        assert data["is_active"] is True
    
    def test_get_me_no_token(self, client):
        """Get current user without token fails."""
        response = client.get("/auth/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_me_invalid_token(self, client):
        """Get current user with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token_success(self, client, test_user):
        """Refresh token returns new access token."""
        # First login to get refresh token
        login_response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpassword123"}
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Use refresh token
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, client):
        """Refresh with invalid token fails."""
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_change_password_success(self, client, test_user, auth_headers):
        """Change password with correct current password."""
        response = client.post(
            "/auth/change-password",
            headers=auth_headers,
            json={"current_password": "testpassword123", "new_password": "newpassword456"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Password updated successfully"
        
        # Verify new password works
        login_response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "newpassword456"}
        )
        assert login_response.status_code == status.HTTP_200_OK
    
    def test_change_password_wrong_current(self, client, test_user, auth_headers):
        """Change password with wrong current password fails."""
        response = client.post(
            "/auth/change-password",
            headers=auth_headers,
            json={"current_password": "wrongpassword", "new_password": "newpassword456"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["error"] == "invalid_password"
    
    def test_change_password_too_short(self, client, test_user, auth_headers):
        """Change password with short new password fails."""
        response = client.post(
            "/auth/change-password",
            headers=auth_headers,
            json={"current_password": "testpassword123", "new_password": "short"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_logout_success(self, client, test_user, auth_headers):
        """Logout endpoint works with valid token."""
        response = client.post("/auth/logout", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Logout successful"


class TestRBAC:
    """Tests for role-based access control."""
    
    def test_admin_can_list_users(self, client, admin_headers):
        """Admin can access user list."""
        response = client.get("/users", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
    
    def test_non_admin_cannot_list_users(self, client, auth_headers):
        """Non-admin cannot access user list."""
        response = client.get("/users", headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_viewer_cannot_list_users(self, client, viewer_headers):
        """Viewer cannot access user list."""
        response = client.get("/users", headers=viewer_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_can_create_user(self, client, admin_headers):
        """Admin can create new user."""
        response = client.post(
            "/users",
            headers=admin_headers,
            json={
                "username": "newuser",
                "password": "newpassword123",
                "email": "new@example.com",
                "role": "viewer"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["role"] == "viewer"
    
    def test_non_admin_cannot_create_user(self, client, auth_headers):
        """Non-admin cannot create users."""
        response = client.post(
            "/users",
            headers=auth_headers,
            json={
                "username": "hacker",
                "password": "hackpassword123",
                "role": "admin"
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_can_delete_user(self, client, admin_headers, test_user):
        """Admin can delete (deactivate) user."""
        response = client.delete(f"/users/{test_user.id}", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
    
    def test_admin_cannot_delete_self(self, client, test_admin, admin_headers):
        """Admin cannot delete themselves."""
        response = client.delete(f"/users/{test_admin.id}", headers=admin_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot delete your own account" in response.json()["message"]


class TestTokenSecurity:
    """Tests for token validation and security."""
    
    def test_token_contains_user_id(self, test_user):
        """Token payload contains user ID."""
        token_data = {"sub": str(test_user.id), "role": test_user.role}
        from app.auth.service import create_access_token
        token = create_access_token(token_data)
        
        decoded = decode_token(token)
        assert decoded["sub"] == str(test_user.id)
        assert decoded["role"] == "investigator"
    
    def test_refresh_token_type_verified(self, test_user):
        """Refresh tokens are type-verified."""
        refresh_token = create_refresh_token(str(test_user.id))
        decoded = decode_token(refresh_token)
        assert decoded["type"] == "refresh"
    
    def test_access_token_rejected_as_refresh(self, client, test_user):
        """Access token cannot be used for refresh."""
        from app.auth.service import create_access_token
        token_data = {"sub": str(test_user.id), "role": test_user.role}
        access_token = create_access_token(token_data)
        
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": access_token}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserManagement:
    """Tests for user CRUD operations."""
    
    def test_create_user_duplicate_username(self, client, admin_headers, test_user):
        """Cannot create user with duplicate username."""
        response = client.post(
            "/users",
            headers=admin_headers,
            json={
                "username": "testuser",  # Already exists
                "password": "password123",
                "role": "viewer"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_user_duplicate_email(self, client, admin_headers, test_user):
        """Cannot create user with duplicate email."""
        response = client.post(
            "/users",
            headers=admin_headers,
            json={
                "username": "newname",
                "password": "password123",
                "email": "test@example.com",  # Already exists
                "role": "viewer"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_user_invalid_role(self, client, admin_headers):
        """Cannot create user with invalid role."""
        response = client.post(
            "/users",
            headers=admin_headers,
            json={
                "username": "baduser",
                "password": "password123",
                "role": "superuser"  # Invalid
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_user_role(self, client, admin_headers, test_user):
        """Admin can update user role."""
        response = client.put(
            f"/users/{test_user.id}",
            headers=admin_headers,
            json={"role": "reviewer"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["role"] == "reviewer"
    
    def test_update_user_email(self, client, admin_headers, test_user):
        """Admin can update user email."""
        response = client.put(
            f"/users/{test_user.id}",
            headers=admin_headers,
            json={"email": "updated@example.com"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == "updated@example.com"
    
    def test_admin_cannot_demote_self(self, client, test_admin, admin_headers):
        """Admin cannot change their own role."""
        response = client.put(
            f"/users/{test_admin.id}",
            headers=admin_headers,
            json={"role": "viewer"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot demote yourself" in response.json()["message"]
