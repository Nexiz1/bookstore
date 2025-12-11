"""
Reviews API 테스트
- POST /books/{book_id}/reviews: 리뷰 작성
- GET /books/{book_id}/reviews: 리뷰 목록 조회
- DELETE /reviews/{review_id}: 리뷰 삭제
"""
import pytest


@pytest.fixture
def completed_order(client, buyer_headers, created_book):
    """완료된 주문 (리뷰 작성 가능 상태)"""
    # 장바구니 담기
    cart_data = {"book_id": created_book["id"], "quantity": 1}
    client.post("/carts/", json=cart_data, headers=buyer_headers)

    # 주문 생성
    order_response = client.post("/orders/", json={}, headers=buyer_headers)
    order = order_response.json()["data"]

    return {
        "order": order,
        "order_item_id": order["items"][0]["id"],
        "book": created_book
    }


class TestCreateReview:
    """리뷰 작성 테스트"""

    def test_create_review_success(self, client, buyer_headers, completed_order):
        """정상 리뷰 작성"""
        book_id = completed_order["book"]["id"]
        order_item_id = completed_order["order_item_id"]

        review_data = {
            "order_item_id": order_item_id,
            "rating": 5,
            "comment": "정말 좋은 책입니다!"
        }
        response = client.post(
            f"/books/{book_id}/reviews",
            json=review_data,
            headers=buyer_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["rating"] == 5
        assert data["data"]["comment"] == "정말 좋은 책입니다!"

    def test_create_review_without_purchase(self, client, buyer_headers, created_book):
        """구매하지 않은 도서에 리뷰 시도"""
        review_data = {
            "order_item_id": 99999,
            "rating": 5,
            "comment": "테스트"
        }
        response = client.post(
            f"/books/{created_book['id']}/reviews",
            json=review_data,
            headers=buyer_headers
        )

        assert response.status_code == 404

    def test_create_review_duplicate(self, client, buyer_headers, completed_order):
        """중복 리뷰 작성 시도"""
        book_id = completed_order["book"]["id"]
        order_item_id = completed_order["order_item_id"]

        review_data = {
            "order_item_id": order_item_id,
            "rating": 5,
            "comment": "첫 번째 리뷰"
        }
        client.post(f"/books/{book_id}/reviews", json=review_data, headers=buyer_headers)

        # 동일 주문 아이템에 중복 리뷰
        response = client.post(
            f"/books/{book_id}/reviews",
            json=review_data,
            headers=buyer_headers
        )

        assert response.status_code == 409

    def test_create_review_invalid_rating(self, client, buyer_headers, completed_order):
        """잘못된 평점 (1-5 범위 외)"""
        book_id = completed_order["book"]["id"]
        order_item_id = completed_order["order_item_id"]

        review_data = {
            "order_item_id": order_item_id,
            "rating": 10,
            "comment": "테스트"
        }
        response = client.post(
            f"/books/{book_id}/reviews",
            json=review_data,
            headers=buyer_headers
        )

        assert response.status_code == 422


class TestGetReviews:
    """리뷰 목록 조회 테스트"""

    def test_get_reviews_empty(self, client, created_book):
        """빈 리뷰 목록"""
        response = client.get(f"/books/{created_book['id']}/reviews")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["reviews"] == []
        assert data["data"]["total"] == 0

    def test_get_reviews_with_data(self, client, buyer_headers, completed_order):
        """리뷰가 있는 경우"""
        book_id = completed_order["book"]["id"]
        order_item_id = completed_order["order_item_id"]

        # 리뷰 작성
        review_data = {
            "order_item_id": order_item_id,
            "rating": 4,
            "comment": "좋은 책입니다"
        }
        client.post(f"/books/{book_id}/reviews", json=review_data, headers=buyer_headers)

        response = client.get(f"/books/{book_id}/reviews")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 1
        assert data["data"]["average_rating"] == 4.0


class TestDeleteReview:
    """리뷰 삭제 테스트"""

    def test_delete_review_success(self, client, buyer_headers, completed_order):
        """정상 리뷰 삭제"""
        book_id = completed_order["book"]["id"]
        order_item_id = completed_order["order_item_id"]

        # 리뷰 작성
        review_data = {
            "order_item_id": order_item_id,
            "rating": 5,
            "comment": "삭제할 리뷰"
        }
        create_response = client.post(
            f"/books/{book_id}/reviews",
            json=review_data,
            headers=buyer_headers
        )
        review_id = create_response.json()["data"]["id"]

        # 리뷰 삭제
        response = client.delete(f"/reviews/{review_id}", headers=buyer_headers)

        assert response.status_code == 200

    def test_delete_review_not_owner(self, client, buyer_headers, completed_order, test_user_data, auth_headers):
        """본인 리뷰가 아닌 경우"""
        book_id = completed_order["book"]["id"]
        order_item_id = completed_order["order_item_id"]

        # 리뷰 작성
        review_data = {
            "order_item_id": order_item_id,
            "rating": 5,
            "comment": "테스트"
        }
        create_response = client.post(
            f"/books/{book_id}/reviews",
            json=review_data,
            headers=buyer_headers
        )
        review_id = create_response.json()["data"]["id"]

        # 다른 사용자로 삭제 시도 (auth_headers는 seller)
        response = client.delete(f"/reviews/{review_id}", headers=auth_headers)

        assert response.status_code == 403

    def test_delete_review_not_found(self, client, buyer_headers):
        """존재하지 않는 리뷰"""
        response = client.delete("/reviews/99999", headers=buyer_headers)

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
        assert data["message"] is not None
