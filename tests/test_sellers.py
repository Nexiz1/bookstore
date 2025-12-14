"""
Sellers API 테스트
- POST /sellers: 판매자 등록
- GET /sellers/me: 내 판매자 정보 조회
- PATCH /sellers/me: 판매자 정보 수정
"""
import pytest
from tests.conftest import assert_success_response, assert_error_response


class TestSellerRegistration:
    """판매자 등록 테스트"""

    def test_register_seller_success(self, client, auth_headers, test_seller_data):
        """정상 판매자 등록"""
        response = client.post("/sellers/", json=test_seller_data, headers=auth_headers)

        data = assert_success_response(response, status_code=201)
        assert data["data"]["business_name"] == test_seller_data["business_name"]

    def test_register_seller_duplicate(self, client, auth_headers, test_seller_data):
        """중복 판매자 등록 시도"""
        # 첫 번째 등록
        client.post("/sellers/", json=test_seller_data, headers=auth_headers)

        # 동일 계정으로 재등록 시도
        response = client.post("/sellers/", json=test_seller_data, headers=auth_headers)

        assert_error_response(response, status_code=409)

    def test_register_seller_without_auth(self, client, test_seller_data):
        """인증 없이 등록 시도"""
        response = client.post("/sellers/", json=test_seller_data)

        assert_error_response(response, status_code=401)


class TestGetSellerProfile:
    """판매자 정보 조회 테스트"""

    def test_get_seller_profile_success(self, client, seller_auth_headers, test_seller_data):
        """정상 판매자 정보 조회"""
        response = client.get("/sellers/me", headers=seller_auth_headers)

        data = assert_success_response(response, status_code=200)
        assert data["data"]["business_name"] == test_seller_data["business_name"]

    def test_get_seller_profile_not_seller(self, client, auth_headers):
        """판매자가 아닌 사용자의 조회 시도"""
        response = client.get("/sellers/me", headers=auth_headers)

        assert_error_response(response, status_code=403)


class TestUpdateSellerProfile:
    """판매자 정보 수정 테스트"""

    def test_update_seller_profile_success(self, client, seller_auth_headers):
        """정상 판매자 정보 수정"""
        update_data = {
            "address": "서울시 마포구",
            "payout_account": "123-456-789012"
        }
        response = client.patch("/sellers/me", json=update_data, headers=seller_auth_headers)

        data = assert_success_response(response, status_code=200)
        assert data["data"]["address"] == "서울시 마포구"
        assert data["data"]["payout_account"] == "123-456-789012"
