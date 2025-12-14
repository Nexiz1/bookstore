"""
Rankings API 테스트
- GET /rankings: 도서 랭킹 조회 (Redis 캐시 + DB 폴백)
"""
import asyncio
import pytest
from tests.conftest import assert_success_response, assert_error_response
from app.services.ranking_service import RankingService


class TestGetRankings:
    """랭킹 조회 테스트"""

    def test_get_rankings_empty(self, client):
        """랭킹 데이터가 없을 때 빈 목록 반환"""
        response = client.get("/rankings/")

        data = assert_success_response(response, status_code=200)
        assert data["data"]["rankings"] == []
        assert data["data"]["ranking_type"] == "purchaseCount"

    def test_get_rankings_purchase_count(self, client, buyer_headers, created_book, db_session):
        """판매량 순 랭킹 조회"""
        # 구매 생성
        cart_data = {"book_id": created_book["id"], "quantity": 3}
        client.post("/carts/", json=cart_data, headers=buyer_headers)
        client.post("/orders/", json={}, headers=buyer_headers)

        # 랭킹 데이터 집계 (스케줄러 대신 수동 실행)
        asyncio.run(RankingService.calculate_and_cache_rankings(db_session))

        # 판매량 순 랭킹 조회
        response = client.get("/rankings/?type=purchaseCount")

        data = assert_success_response(response, status_code=200)
        assert data["data"]["ranking_type"] == "purchaseCount"
        assert len(data["data"]["rankings"]) >= 1

        # 첫 번째 아이템 검증
        first_item = data["data"]["rankings"][0]
        assert first_item["rank"] == 1
        assert first_item["book_id"] == created_book["id"]
        assert first_item["purchase_count"] == 3

    def test_get_rankings_average_rating(self, client, buyer_headers, completed_order, db_session):
        """평점 순 랭킹 조회"""
        book_id = completed_order["book"]["id"]
        order_item_id = completed_order["order_item_id"]

        # 리뷰 작성
        review_data = {
            "order_item_id": order_item_id,
            "rating": 5,
            "comment": "최고의 책입니다!"
        }
        client.post(f"/books/{book_id}/reviews", json=review_data, headers=buyer_headers)

        # 랭킹 데이터 집계 (스케줄러 대신 수동 실행)
        asyncio.run(RankingService.calculate_and_cache_rankings(db_session))

        # 평점 순 랭킹 조회
        response = client.get("/rankings/?type=averageRating")

        data = assert_success_response(response, status_code=200)
        assert data["data"]["ranking_type"] == "averageRating"
        assert len(data["data"]["rankings"]) >= 1

        # 첫 번째 아이템 검증
        first_item = data["data"]["rankings"][0]
        assert first_item["rank"] == 1
        assert float(first_item["average_rating"]) == 5.0

    def test_get_rankings_with_limit(self, client, seller_auth_headers, buyer_headers, test_book_data):
        """limit 파라미터로 결과 수 제한"""
        # 여러 도서 생성 및 구매
        for i in range(5):
            book_data = {**test_book_data, "title": f"테스트도서{i}", "isbn": f"978-89-1234-56{i}"}
            book_response = client.post("/books/", json=book_data, headers=seller_auth_headers)
            book_id = book_response.json()["data"]["id"]

            cart_data = {"book_id": book_id, "quantity": i + 1}
            client.post("/carts/", json=cart_data, headers=buyer_headers)

        client.post("/orders/", json={}, headers=buyer_headers)

        # limit=3으로 조회
        response = client.get("/rankings/?limit=3")

        data = assert_success_response(response, status_code=200)
        assert len(data["data"]["rankings"]) <= 3

    def test_get_rankings_invalid_type(self, client):
        """잘못된 랭킹 타입 (422 Validation Error)"""
        response = client.get("/rankings/?type=invalidType")

        assert response.status_code == 422


class TestRankingsCache:
    """랭킹 캐싱 테스트"""

    def test_rankings_uses_mock_redis(self, client, mock_redis):
        """Mock Redis가 올바르게 설정되었는지 확인"""
        # 랭킹 조회 시 에러 없이 동작해야 함
        response = client.get("/rankings/")

        assert_success_response(response, status_code=200)

    def test_rankings_cache_fallback_to_db(self, client, buyer_headers, created_book, mock_redis, db_session):
        """캐시 미스 시 DB에서 조회 후 캐싱"""
        # 초기 상태: 캐시 비어있음
        mock_redis.clear()

        # 구매 생성
        cart_data = {"book_id": created_book["id"], "quantity": 2}
        client.post("/carts/", json=cart_data, headers=buyer_headers)
        client.post("/orders/", json={}, headers=buyer_headers)

        # 랭킹 데이터 집계 (스케줄러 대신 수동 실행)
        asyncio.run(RankingService.calculate_and_cache_rankings(db_session))

        # 캐시를 비워서 DB 폴백 테스트
        mock_redis.clear()

        # 랭킹 조회 (DB 폴백 후 캐싱)
        response = client.get("/rankings/?type=purchaseCount")

        data = assert_success_response(response, status_code=200)
        assert len(data["data"]["rankings"]) >= 1
