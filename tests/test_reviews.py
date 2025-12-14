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


class TestUpdateReview:
    """리뷰 수정 테스트 (PATCH /reviews/{review_id})"""

    def test_update_review_success(self, client, buyer_headers, completed_order):
        """정상 리뷰 수정 - 평점과 코멘트 모두 변경"""
        book_id = completed_order["book"]["id"]
        order_item_id = completed_order["order_item_id"]

        # 먼저 리뷰 작성
        review_data = {
            "order_item_id": order_item_id,
            "rating": 3,
            "comment": "그저 그런 책입니다"
        }
        create_response = client.post(
            f"/books/{book_id}/reviews",
            json=review_data,
            headers=buyer_headers
        )
        review_id = create_response.json()["data"]["id"]

        # 리뷰 수정
        update_data = {
            "rating": 5,
            "comment": "다시 읽어보니 정말 좋은 책입니다!"
        }
        response = client.patch(
            f"/reviews/{review_id}",
            json=update_data,
            headers=buyer_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["rating"] == 5
        assert data["data"]["comment"] == "다시 읽어보니 정말 좋은 책입니다!"
        assert data["message"] == "Review updated successfully"

    def test_update_review_rating_only(self, client, buyer_headers, completed_order):
        """평점만 수정"""
        book_id = completed_order["book"]["id"]
        order_item_id = completed_order["order_item_id"]

        # 리뷰 작성
        review_data = {
            "order_item_id": order_item_id,
            "rating": 3,
            "comment": "원래 코멘트"
        }
        create_response = client.post(
            f"/books/{book_id}/reviews",
            json=review_data,
            headers=buyer_headers
        )
        review_id = create_response.json()["data"]["id"]

        # 평점만 수정
        update_data = {"rating": 4}
        response = client.patch(
            f"/reviews/{review_id}",
            json=update_data,
            headers=buyer_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["rating"] == 4
        assert data["data"]["comment"] == "원래 코멘트"  # 코멘트는 유지

    def test_update_review_comment_only(self, client, buyer_headers, completed_order):
        """코멘트만 수정"""
        book_id = completed_order["book"]["id"]
        order_item_id = completed_order["order_item_id"]

        # 리뷰 작성
        review_data = {
            "order_item_id": order_item_id,
            "rating": 4,
            "comment": "원래 코멘트"
        }
        create_response = client.post(
            f"/books/{book_id}/reviews",
            json=review_data,
            headers=buyer_headers
        )
        review_id = create_response.json()["data"]["id"]

        # 코멘트만 수정
        update_data = {"comment": "수정된 코멘트입니다"}
        response = client.patch(
            f"/reviews/{review_id}",
            json=update_data,
            headers=buyer_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["rating"] == 4  # 평점은 유지
        assert data["data"]["comment"] == "수정된 코멘트입니다"

    def test_update_review_not_owner(self, client, buyer_headers, completed_order, auth_headers):
        """본인이 아닌 리뷰 수정 시도 (403 Forbidden)"""
        book_id = completed_order["book"]["id"]
        order_item_id = completed_order["order_item_id"]

        # buyer가 리뷰 작성
        review_data = {
            "order_item_id": order_item_id,
            "rating": 5,
            "comment": "구매자의 리뷰"
        }
        create_response = client.post(
            f"/books/{book_id}/reviews",
            json=review_data,
            headers=buyer_headers
        )
        review_id = create_response.json()["data"]["id"]

        # 다른 사용자(seller)가 수정 시도
        update_data = {"rating": 1, "comment": "악의적인 수정"}
        response = client.patch(
            f"/reviews/{review_id}",
            json=update_data,
            headers=auth_headers  # seller의 헤더
        )

        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "error"

    def test_update_review_not_found(self, client, buyer_headers):
        """존재하지 않는 리뷰 수정 시도 (404 Not Found)"""
        update_data = {"rating": 5, "comment": "수정"}
        response = client.patch(
            "/reviews/99999",
            json=update_data,
            headers=buyer_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"

    def test_update_review_invalid_rating(self, client, buyer_headers, completed_order):
        """잘못된 평점으로 수정 시도 (422 Validation Error)"""
        book_id = completed_order["book"]["id"]
        order_item_id = completed_order["order_item_id"]

        # 리뷰 작성
        review_data = {
            "order_item_id": order_item_id,
            "rating": 4,
            "comment": "테스트"
        }
        create_response = client.post(
            f"/books/{book_id}/reviews",
            json=review_data,
            headers=buyer_headers
        )
        review_id = create_response.json()["data"]["id"]

        # 잘못된 평점 (6)으로 수정 시도
        update_data = {"rating": 6}
        response = client.patch(
            f"/reviews/{review_id}",
            json=update_data,
            headers=buyer_headers
        )

        assert response.status_code == 422

    def test_update_review_updates_book_rating(self, client, buyer_headers, completed_order):
        """리뷰 수정 시 도서 평점이 재계산되는지 확인"""
        book_id = completed_order["book"]["id"]
        order_item_id = completed_order["order_item_id"]

        # 리뷰 작성 (평점 2)
        review_data = {
            "order_item_id": order_item_id,
            "rating": 2,
            "comment": "별로입니다"
        }
        create_response = client.post(
            f"/books/{book_id}/reviews",
            json=review_data,
            headers=buyer_headers
        )
        review_id = create_response.json()["data"]["id"]

        # 도서 평점 확인
        book_response1 = client.get(f"/books/{book_id}")
        assert float(book_response1.json()["data"]["average_rating"]) == 2.0

        # 리뷰 수정 (평점 5)
        update_data = {"rating": 5}
        client.patch(f"/reviews/{review_id}", json=update_data, headers=buyer_headers)

        # 도서 평점 재확인
        book_response2 = client.get(f"/books/{book_id}")
        assert float(book_response2.json()["data"]["average_rating"]) == 5.0
