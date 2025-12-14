"""
Admin API 테스트
- GET /admin/orders: 전체 주문 현황 조회 (Admin)
- POST /admin/settlements/calculate: 정산 데이터 생성 (Admin)
"""
import pytest


class TestAdminOrders:
    """관리자 주문 조회 테스트"""

    def test_get_all_orders_as_admin(self, client, admin_headers, buyer_headers, created_book):
        """관리자로 전체 주문 조회"""
        # 주문 생성
        cart_data = {"book_id": created_book["id"], "quantity": 1}
        client.post("/carts/", json=cart_data, headers=buyer_headers)
        client.post("/orders/", json={}, headers=buyer_headers)

        # 전체 주문 조회
        response = client.get("/admin/orders", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["total"] >= 1

    def test_get_all_orders_as_normal_user(self, client, auth_headers):
        """일반 사용자가 전체 주문 조회 시도 (403 Forbidden)"""
        response = client.get("/admin/orders", headers=auth_headers)

        assert response.status_code == 403

    def test_get_all_orders_filter_by_status(self, client, admin_headers, buyer_headers, created_book):
        """상태 필터로 주문 조회"""
        # 주문 생성
        cart_data = {"book_id": created_book["id"], "quantity": 1}
        client.post("/carts/", json=cart_data, headers=buyer_headers)
        client.post("/orders/", json={}, headers=buyer_headers)

        # PENDING 상태 주문만 조회
        response = client.get("/admin/orders?status=PENDING", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        # 모든 주문이 PENDING 상태인지 확인
        for order in data["data"]["orders"]:
            assert order["status"] == "PENDING"


class TestSettlementCalculation:
    """정산 데이터 생성 테스트"""

    def test_calculate_settlements_success(self, client, admin_headers, arrived_order, db_session):
        """정상 정산 데이터 생성"""
        # 정산 실행
        response = client.post("/admin/settlements/calculate", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["created_settlements"] >= 1
        assert data["data"]["total_processed_orders"] >= 1
        assert "정산 데이터가 생성되었습니다" in data["message"]

    def test_calculate_settlements_no_arrived_orders(self, client, admin_headers):
        """ARRIVED 상태 주문이 없을 때 정산"""
        response = client.post("/admin/settlements/calculate", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["created_settlements"] == 0
        assert data["data"]["total_processed_orders"] == 0
        assert "정산할 주문이 없습니다" in data["message"]

    def test_calculate_settlements_not_admin(self, client, auth_headers):
        """일반 사용자가 정산 시도 (403 Forbidden)"""
        response = client.post("/admin/settlements/calculate", headers=auth_headers)

        assert response.status_code == 403

    def test_calculate_settlements_commission_rate(self, client, admin_headers, arrived_order, db_session):
        """정산 시 수수료율(10%) 적용 확인"""
        from app.models.settlement import Settlement
        from decimal import Decimal

        # 정산 실행
        client.post("/admin/settlements/calculate", headers=admin_headers)

        # DB에서 정산 데이터 조회
        settlement = db_session.query(Settlement).first()
        assert settlement is not None

        # 수수료율 10% 검증
        expected_commission = settlement.total_sales * Decimal("0.10")
        expected_payout = settlement.total_sales - expected_commission

        assert settlement.commission == expected_commission
        assert settlement.final_payout == expected_payout

    def test_calculate_settlements_marks_orders_settled(self, client, admin_headers, arrived_order, db_session):
        """정산 후 주문이 정산 완료로 표시되는지 확인"""
        from app.models.order import OrderItem

        order_item_id = arrived_order["order_item_id"]

        # 정산 전 상태 확인
        item_before = db_session.query(OrderItem).filter(OrderItem.id == order_item_id).first()
        assert item_before.is_settled is False

        # 정산 실행
        client.post("/admin/settlements/calculate", headers=admin_headers)

        # 정산 후 상태 확인
        db_session.expire_all()
        item_after = db_session.query(OrderItem).filter(OrderItem.id == order_item_id).first()
        assert item_after.is_settled is True

    def test_calculate_settlements_already_settled_excluded(self, client, admin_headers, arrived_order, db_session):
        """이미 정산된 주문은 제외되는지 확인"""
        # 첫 번째 정산
        response1 = client.post("/admin/settlements/calculate", headers=admin_headers)
        first_count = response1.json()["data"]["total_processed_orders"]
        assert first_count >= 1

        # 두 번째 정산 (동일 주문은 제외되어야 함)
        response2 = client.post("/admin/settlements/calculate", headers=admin_headers)
        second_count = response2.json()["data"]["total_processed_orders"]
        assert second_count == 0
