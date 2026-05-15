from fastapi import status

from app.auth.schemas import TokenData
from app.auth.service import create_access_token, get_password_hash
from app.users.models import User


def auth_header_for(user: User) -> dict[str, str]:
    token = create_access_token(TokenData(sub=str(user.id), role=user.role))
    return {"Authorization": f"Bearer {token}"}


def create_role_user(db, username: str, role: str) -> User:
    user = User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=get_password_hash("password12345"),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestRBACSensitiveActions:
    def test_viewer_cannot_delete_evidence(self, client, viewer_headers):
        response = client.delete("/media/00000000-0000-0000-0000-000000000000", headers=viewer_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_viewer_cannot_export_reports(self, client, viewer_headers):
        response = client.post(
            "/reports/preview?media_ids=00000000-0000-0000-0000-000000000000",
            headers=viewer_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_viewer_cannot_classify_or_modify_tags(self, client, viewer_headers):
        response = client.post(
            "/process/batch",
            headers=viewer_headers,
            json=["00000000-0000-0000-0000-000000000000"],
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_viewer_cannot_access_admin_users(self, client, viewer_headers):
        response = client.get("/users", headers=viewer_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_investigator_can_upload_but_not_delete(self, client, auth_headers):
        upload_response = client.post("/media/upload", headers=auth_headers)
        assert upload_response.status_code in {
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
        }

        delete_response = client.delete(
            "/media/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert delete_response.status_code == status.HTTP_403_FORBIDDEN

    def test_reviewer_can_preview_reports_but_not_upload(self, client, db):
        reviewer = create_role_user(db, "revieweruser", "reviewer")
        headers = auth_header_for(reviewer)

        preview_response = client.post(
            "/reports/preview?media_ids=00000000-0000-0000-0000-000000000000",
            headers=headers,
        )
        assert preview_response.status_code == status.HTTP_200_OK

        upload_response = client.post(
            "/media/upload",
            headers=headers,
            files={"file": ("sample.txt", b"not media", "text/plain")},
        )
        assert upload_response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_access_user_stats(self, client, admin_headers):
        response = client.get("/users/stats/by-role", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
