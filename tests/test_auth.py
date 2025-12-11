"""
Auth API 테스트
- POST /auth/signup: 회원가입
- POST /auth/login: 로그인
- POST /auth/refresh: 토큰 재발급
- POST /auth/logout: 로그아웃
"""
import pytest


class TestSignup:
    """회원가입 테스트"""

    def test_signup_success(self, client, test_user_data):
        """정상 회원가입"""
        response = client.post("/auth/signup", json=test_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["email"] == test_user_data["email"]
        assert data["data"]["name"] == test_user_data["name"]
        assert "id" in data["data"]

    def test_signup_duplicate_email(self, client, test_user_data):
        """중복 이메일로 회원가입 시도"""
        # 첫 번째 가입
        client.post("/auth/signup", json=test_user_data)

        # 동일 이메일로 재가입 시도
        response = client.post("/auth/signup", json=test_user_data)

        assert response.status_code == 409
        assert response.json()["status"] == "error"

    def test_signup_invalid_email(self, client):
        """잘못된 이메일 형식"""
        invalid_data = {
            "email": "invalid-email",
            "password": "testpassword123",
            "name": "테스트"
        }
        response = client.post("/auth/signup", json=invalid_data)

        assert response.status_code == 422

    def test_signup_short_password(self, client):
        """짧은 비밀번호"""
        invalid_data = {
            "email": "test@example.com",
            "password": "short",
            "name": "테스트"
        }
        response = client.post("/auth/signup", json=invalid_data)

        assert response.status_code == 422


class TestLogin:
    """로그인 테스트"""

    def test_login_success(self, client, test_user_data, registered_user):
        """정상 로그인"""
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user_data, registered_user):
        """잘못된 비밀번호"""
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert response.json()["status"] == "error"

    def test_login_nonexistent_user(self, client):
        """존재하지 않는 사용자"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "testpassword123"
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401


class TestTokenRefresh:
    """토큰 재발급 테스트"""

    def test_refresh_token_success(self, client, test_user_data, registered_user):
        """정상 토큰 재발급"""
        # 로그인하여 리프레시 토큰 획득
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        refresh_token = login_response.json()["data"]["refresh_token"]

        # 토큰 재발급
        response = client.post("/auth/refresh", json={"refresh_token": refresh_token})

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    def test_refresh_token_invalid(self, client):
        """잘못된 리프레시 토큰"""
        response = client.post("/auth/refresh", json={"refresh_token": "invalid_token"})

        assert response.status_code == 401


class TestLogout:
    """로그아웃 테스트"""

    def test_logout_success(self, client, auth_headers):
        """정상 로그아웃"""
        response = client.post("/auth/logout", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_logout_without_auth(self, client):
        """인증 없이 로그아웃 시도"""
        response = client.post("/auth/logout")

        assert response.status_code == 401
