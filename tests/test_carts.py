"""
Carts API 테스트
- GET /carts: 내 장바구니 조회
- POST /carts: 장바구니 담기
- PATCH /carts/{cart_id}: 수량 변경
- DELETE /carts/{cart_id}: 장바구니 아이템 삭제
"""
import pytest
from tests.conftest import assert_success_response, assert_error_response


class TestGetCart:
    """장바구니 조회 테스트"""

    def test_get_empty_cart(self, client, auth_headers):
        """빈 장바구니 조회"""
        response = client.get("/carts/", headers=auth_headers)

        data = assert_success_response(response, status_code=200)
        assert data["data"]["items"] == []
        assert float(data["data"]["total_amount"]) == 0

    def test_get_cart_without_auth(self, client):
        """인증 없이 조회"""
        response = client.get("/carts/")

        assert_error_response(response, status_code=401)


class TestAddToCart:
    """장바구니 담기 테스트"""

    def test_add_to_cart_success(self, client, buyer_headers, created_book):
        """정상 장바구니 담기"""
        cart_data = {
            "book_id": created_book["id"],
            "quantity": 2
        }
        response = client.post("/carts/", json=cart_data, headers=buyer_headers)

        data = assert_success_response(response, status_code=201)
        assert data["data"]["book_id"] == created_book["id"]
        assert data["data"]["quantity"] == 2

    def test_add_to_cart_duplicate(self, client, buyer_headers, created_book):
        """중복 장바구니 담기"""
        cart_data = {"book_id": created_book["id"], "quantity": 1}
        client.post("/carts/", json=cart_data, headers=buyer_headers)

        # 동일 도서 재추가 시도
        response = client.post("/carts/", json=cart_data, headers=buyer_headers)

        assert_error_response(response, status_code=409)

    def test_add_nonexistent_book(self, client, buyer_headers):
        """존재하지 않는 도서"""
        cart_data = {"book_id": 99999, "quantity": 1}
        response = client.post("/carts/", json=cart_data, headers=buyer_headers)

        assert_error_response(response, status_code=404)


class TestUpdateCartQuantity:
    """장바구니 수량 변경 테스트"""

    def test_update_quantity_success(self, client, buyer_headers, created_book):
        """정상 수량 변경"""
        # 장바구니 담기
        cart_data = {"book_id": created_book["id"], "quantity": 1}
        create_response = client.post("/carts/", json=cart_data, headers=buyer_headers)
        cart_id = create_response.json()["data"]["id"]

        # 수량 변경
        response = client.patch(
            f"/carts/{cart_id}",
            json={"quantity": 5},
            headers=buyer_headers
        )

        data = assert_success_response(response, status_code=200)
        assert data["data"]["quantity"] == 5

    def test_update_quantity_invalid(self, client, buyer_headers, created_book):
        """잘못된 수량 (0 이하)"""
        cart_data = {"book_id": created_book["id"], "quantity": 1}
        create_response = client.post("/carts/", json=cart_data, headers=buyer_headers)
        cart_id = create_response.json()["data"]["id"]

        response = client.patch(
            f"/carts/{cart_id}",
            json={"quantity": 0},
            headers=buyer_headers
        )

        assert response.status_code == 422


class TestRemoveFromCart:
    """장바구니 삭제 테스트"""

    def test_remove_from_cart_success(self, client, buyer_headers, created_book):
        """정상 삭제"""
        cart_data = {"book_id": created_book["id"], "quantity": 1}
        create_response = client.post("/carts/", json=cart_data, headers=buyer_headers)
        cart_id = create_response.json()["data"]["id"]

        response = client.delete(f"/carts/{cart_id}", headers=buyer_headers)

        assert_success_response(response, status_code=200)

        # 삭제 확인
        cart_response = client.get("/carts/", headers=buyer_headers)
        assert cart_response.json()["data"]["total_items"] == 0

    def test_remove_nonexistent_cart_item(self, client, buyer_headers):
        """존재하지 않는 장바구니 아이템"""
        response = client.delete("/carts/99999", headers=buyer_headers)

        assert_error_response(response, status_code=404)
