"""
Users API 테스트
- GET /users/me: 내 프로필 조회
- PATCH /users/me: 내 프로필 수정
- POST /users/me/password: 비밀번호 변경
- GET /users: 전체 회원 목록 (Admin)
- PATCH /users/{user_id}/role: 권한 변경 (Admin)
- PATCH /users/{user_id}/deactivate: 사용자 계정 비활성화 (Admin)
"""
import pytest


class TestGetMyProfile:
    """내 프로필 조회 테스트"""

    def test_get_my_profile_success(self, client, auth_headers, test_user_data):
        """정상 프로필 조회"""
        response = client.get("/users/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["email"] == test_user_data["email"]
        assert data["data"]["name"] == test_user_data["name"]

    def test_get_my_profile_without_auth(self, client):
        """인증 없이 조회 시도"""
        response = client.get("/users/me")

        assert response.status_code == 401


class TestUpdateMyProfile:
    """내 프로필 수정 테스트"""

    def test_update_profile_success(self, client, auth_headers):
        """정상 프로필 수정"""
        update_data = {
            "name": "수정된이름",
            "address": "서울시 송파구",
            "phone_number": "010-9999-8888"
        }
        response = client.patch("/users/me", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "수정된이름"
        assert data["data"]["address"] == "서울시 송파구"

    def test_update_profile_partial(self, client, auth_headers):
        """일부 필드만 수정"""
        update_data = {"address": "부산시 해운대구"}
        response = client.patch("/users/me", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["data"]["address"] == "부산시 해운대구"


class TestChangePassword:
    """비밀번호 변경 테스트"""

    def test_change_password_success(self, client, auth_headers, test_user_data):
        """정상 비밀번호 변경"""
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": "newpassword123"
        }
        response = client.post("/users/me/password", json=password_data, headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # 새 비밀번호로 로그인 확인
        login_response = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": "newpassword123"
        })
        assert login_response.status_code == 200

    def test_change_password_wrong_current(self, client, auth_headers):
        """현재 비밀번호 틀림"""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        response = client.post("/users/me/password", json=password_data, headers=auth_headers)

        assert response.status_code == 401

    def test_change_password_short_new(self, client, auth_headers, test_user_data):
        """새 비밀번호가 너무 짧음"""
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": "short"
        }
        response = client.post("/users/me/password", json=password_data, headers=auth_headers)

        assert response.status_code == 422


class TestAdminUserManagement:
    """관리자 사용자 관리 테스트"""

    def test_get_all_users_as_admin(self, client, admin_headers, test_user_data):
        """관리자로 전체 사용자 조회"""
        # 일반 사용자 추가 생성
        client.post("/auth/signup", json=test_user_data)

        # 전체 사용자 조회
        response = client.get("/users/", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 2

    def test_get_all_users_as_normal_user(self, client, auth_headers):
        """일반 사용자로 전체 조회 시도 (권한 없음)"""
        response = client.get("/users/", headers=auth_headers)

        assert response.status_code == 403

    def test_update_user_role(self, client, admin_headers, test_user_data):
        """사용자 권한 변경"""
        # 대상 사용자 생성
        signup_response = client.post("/auth/signup", json=test_user_data)
        target_user_id = signup_response.json()["data"]["id"]

        # 권한 변경
        response = client.patch(
            f"/users/{target_user_id}/role",
            json={"role": "seller"},
            headers=admin_headers
        )

        assert response.status_code == 200
        assert response.json()["data"]["role"] == "seller"


class TestUserDeactivation:
    """사용자 계정 비활성화 테스트"""

    def test_deactivate_user_success(self, client, admin_headers, test_user_data, db_session):
        """Admin이 사용자 계정 비활성화 성공"""
        from app.models.user import User

        # 대상 사용자 생성
        signup_response = client.post("/auth/signup", json=test_user_data)
        target_user_id = signup_response.json()["data"]["id"]

        # 비활성화 전 상태 확인
        user_before = db_session.query(User).filter(User.id == target_user_id).first()
        assert user_before.is_active is True

        # 계정 비활성화
        response = client.patch(
            f"/users/{target_user_id}/deactivate",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["is_active"] is False
        assert data["message"] == "User account deactivated successfully"

        # DB에서 is_active 값 검증
        db_session.expire_all()  # 캐시 무효화
        user_after = db_session.query(User).filter(User.id == target_user_id).first()
        assert user_after.is_active is False

    def test_deactivate_user_not_admin(self, client, auth_headers, test_user2_data):
        """일반 사용자가 비활성화 시도 (403 Forbidden)"""
        # 다른 사용자 생성
        signup_response = client.post("/auth/signup", json=test_user2_data)
        target_user_id = signup_response.json()["data"]["id"]

        # 일반 사용자로 비활성화 시도
        response = client.patch(
            f"/users/{target_user_id}/deactivate",
            headers=auth_headers
        )

        assert response.status_code == 403

    def test_deactivate_admin_forbidden(self, client, admin_headers, db_session):
        """Admin 계정 비활성화 시도 (403 Forbidden)"""
        from app.models.user import User

        # Admin 사용자 ID 조회
        admin_user = db_session.query(User).filter(User.role == "admin").first()

        # Admin 자신 비활성화 시도
        response = client.patch(
            f"/users/{admin_user.id}/deactivate",
            headers=admin_headers
        )

        assert response.status_code == 403

    def test_deactivate_user_not_found(self, client, admin_headers):
        """존재하지 않는 사용자 비활성화 시도 (404 Not Found)"""
        response = client.patch(
            "/users/99999/deactivate",
            headers=admin_headers
        )

        assert response.status_code == 404

    def test_deactivated_user_login_blocked(self, client, deactivated_user):
        """비활성화된 계정으로 로그인 시도 (401 Unauthorized)"""
        login_data = {
            "email": deactivated_user["email"],
            "password": deactivated_user["password"]
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401

    def test_deactivated_user_api_access_blocked(self, client, test_user_data, admin_headers, db_session):
        """비활성화된 계정의 토큰으로 API 접근 시도 (401 Unauthorized)"""
        # 사용자 생성 및 로그인
        client.post("/auth/signup", json=test_user_data)
        login_response = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["data"]["access_token"]
        user_headers = {"Authorization": f"Bearer {token}"}

        # 정상 접근 확인
        me_response = client.get("/users/me", headers=user_headers)
        assert me_response.status_code == 200
        user_id = me_response.json()["data"]["id"]

        # Admin이 계정 비활성화
        client.patch(f"/users/{user_id}/deactivate", headers=admin_headers)

        # 비활성화된 토큰으로 API 접근 시도
        blocked_response = client.get("/users/me", headers=user_headers)
        assert blocked_response.status_code == 401
