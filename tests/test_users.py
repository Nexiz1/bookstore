"""
Users API 테스트
- GET /users/me: 내 프로필 조회
- PATCH /users/me: 내 프로필 수정
- POST /users/me/password: 비밀번호 변경
- GET /users: 전체 회원 목록 (Admin)
- PATCH /users/{user_id}/role: 권한 변경 (Admin)
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
