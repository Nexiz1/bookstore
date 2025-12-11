"""
Orders API 테스트
- POST /orders: 주문 생성
- GET /orders: 내 주문 내역 조회
- GET /orders/{order_id}: 주문 상세 조회
- POST /orders/{order_id}/cancel: 주문 취소
- GET /admin/orders: 전체 주문 조회 (Admin)
"""
import pytest


@pytest.fixture
def cart_with_item(client, buyer_headers, created_book):
    """장바구니에 아이템이 담긴 상태"""
    cart_data = {"book_id": created_book["id"], "quantity": 2}
    client.post("/carts/", json=cart_data, headers=buyer_headers)
    return created_book


class TestCreateOrder:
    """주문 생성 테스트"""

    def test_create_order_success(self, client, buyer_headers, cart_with_item):
        """정상 주문 생성"""
        response = client.post("/orders/", json={}, headers=buyer_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "CREATED"
        assert len(data["data"]["items"]) == 1
        assert data["data"]["items"][0]["quantity"] == 2

    def test_create_order_empty_cart(self, client, buyer_headers):
        """빈 장바구니로 주문 시도"""
        response = client.post("/orders/", json={}, headers=buyer_headers)

        assert response.status_code == 400

    def test_create_order_without_auth(self, client):
        """인증 없이 주문"""
        response = client.post("/orders/", json={})

        assert response.status_code == 401


class TestGetOrders:
    """주문 목록 조회 테스트"""

    def test_get_orders_empty(self, client, buyer_headers):
        """빈 주문 목록"""
        response = client.get("/orders/", headers=buyer_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["orders"] == []

    def test_get_orders_with_data(self, client, buyer_headers, cart_with_item):
        """주문이 있는 경우"""
        # 주문 생성
        client.post("/orders/", json={}, headers=buyer_headers)

        response = client.get("/orders/", headers=buyer_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 1


class TestGetOrderDetail:
    """주문 상세 조회 테스트"""

    def test_get_order_detail_success(self, client, buyer_headers, cart_with_item):
        """정상 상세 조회"""
        # 주문 생성
        create_response = client.post("/orders/", json={}, headers=buyer_headers)
        order_id = create_response.json()["data"]["id"]

        response = client.get(f"/orders/{order_id}", headers=buyer_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == order_id
        assert len(data["data"]["items"]) >= 1

    def test_get_order_detail_not_found(self, client, buyer_headers):
        """존재하지 않는 주문"""
        response = client.get("/orders/99999", headers=buyer_headers)

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
        assert data["message"] is not None


class TestCancelOrder:
    """주문 취소 테스트"""

    def test_cancel_order_success(self, client, buyer_headers, cart_with_item):
        """정상 주문 취소"""
        # 주문 생성
        create_response = client.post("/orders/", json={}, headers=buyer_headers)
        order_id = create_response.json()["data"]["id"]

        response = client.post(f"/orders/{order_id}/cancel", headers=buyer_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "REFUND"

    def test_cancel_order_not_found(self, client, buyer_headers):
        """존재하지 않는 주문 취소"""
        response = client.post("/orders/99999/cancel", headers=buyer_headers)

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
        assert data["message"] is not None


class TestAdminOrders:
    """관리자 주문 조회 테스트"""

    def test_get_all_orders_as_admin(self, client, admin_headers, buyer_headers, cart_with_item):
        """관리자로 전체 주문 조회"""
        # 주문 생성
        client.post("/orders/", json={}, headers=buyer_headers)

        response = client.get("/admin/orders", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 1

    def test_get_all_orders_not_admin(self, client, buyer_headers):
        """일반 사용자로 관리자 API 접근"""
        response = client.get("/admin/orders", headers=buyer_headers)

        assert response.status_code == 403
