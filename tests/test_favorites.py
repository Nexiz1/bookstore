"""
Favorites API 테스트
- POST /books/{book_id}/favorites: 찜하기 등록
- DELETE /books/{book_id}/favorites: 찜하기 취소
- GET /favorites: 내 찜 목록 조회
"""
import pytest


class TestAddFavorite:
    """찜하기 등록 테스트"""

    def test_add_favorite_success(self, client, buyer_headers, created_book):
        """정상 찜하기 등록"""
        response = client.post(
            f"/books/{created_book['id']}/favorites",
            headers=buyer_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["book_id"] == created_book["id"]
        assert data["data"]["book_title"] == created_book["title"]

    def test_add_favorite_duplicate(self, client, buyer_headers, created_book):
        """중복 찜하기"""
        client.post(f"/books/{created_book['id']}/favorites", headers=buyer_headers)

        response = client.post(
            f"/books/{created_book['id']}/favorites",
            headers=buyer_headers
        )

        assert response.status_code == 409

    def test_add_favorite_nonexistent_book(self, client, buyer_headers):
        """존재하지 않는 도서"""
        response = client.post("/books/99999/favorites", headers=buyer_headers)

        assert response.status_code == 404

    def test_add_favorite_without_auth(self, client, created_book):
        """인증 없이 찜하기"""
        response = client.post(f"/books/{created_book['id']}/favorites")

        assert response.status_code == 401


class TestRemoveFavorite:
    """찜하기 취소 테스트"""

    def test_remove_favorite_success(self, client, buyer_headers, created_book):
        """정상 찜하기 취소"""
        # 찜하기 등록
        client.post(f"/books/{created_book['id']}/favorites", headers=buyer_headers)

        # 취소
        response = client.delete(
            f"/books/{created_book['id']}/favorites",
            headers=buyer_headers
        )

        assert response.status_code == 200

    def test_remove_favorite_not_found(self, client, buyer_headers, created_book):
        """찜하지 않은 도서 취소 시도"""
        response = client.delete(
            f"/books/{created_book['id']}/favorites",
            headers=buyer_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
        assert data["message"] is not None


class TestGetFavorites:
    """찜 목록 조회 테스트"""

    def test_get_favorites_empty(self, client, buyer_headers):
        """빈 찜 목록"""
        response = client.get("/favorites", headers=buyer_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["favorites"] == []
        assert data["data"]["total"] == 0

    def test_get_favorites_with_data(self, client, buyer_headers, created_book):
        """찜 목록이 있는 경우"""
        # 찜하기 등록
        client.post(f"/books/{created_book['id']}/favorites", headers=buyer_headers)

        response = client.get("/favorites", headers=buyer_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 1
        assert data["data"]["favorites"][0]["book_id"] == created_book["id"]

    def test_get_favorites_without_auth(self, client):
        """인증 없이 조회"""
        response = client.get("/favorites")

        assert response.status_code == 401
