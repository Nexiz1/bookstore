"""
Books API 테스트
- POST /books: 도서 등록
- GET /books: 도서 목록 조회
- GET /books/{book_id}: 도서 상세 조회
- PUT /books/{book_id}: 도서 수정
- DELETE /books/{book_id}: 도서 삭제
"""
import pytest
from tests.conftest import assert_success_response, assert_error_response


class TestCreateBook:
    """도서 등록 테스트"""

    def test_create_book_success(self, client, seller_auth_headers, test_book_data):
        """정상 도서 등록"""
        response = client.post("/books/", json=test_book_data, headers=seller_auth_headers)

        data = assert_success_response(response, status_code=201)
        assert data["data"]["title"] == test_book_data["title"]
        assert data["data"]["author"] == test_book_data["author"]
        assert float(data["data"]["price"]) == test_book_data["price"]

    def test_create_book_not_seller(self, client, auth_headers, test_book_data):
        """판매자가 아닌 사용자의 등록 시도"""
        response = client.post("/books/", json=test_book_data, headers=auth_headers)

        assert_error_response(response, status_code=403)

    def test_create_book_without_auth(self, client, test_book_data):
        """인증 없이 등록 시도"""
        response = client.post("/books/", json=test_book_data)

        assert_error_response(response, status_code=401)


class TestGetBooks:
    """도서 목록 조회 테스트"""

    def test_get_books_empty(self, client):
        """빈 도서 목록 조회"""
        response = client.get("/books/")

        data = assert_success_response(response, status_code=200)
        assert data["data"]["books"] == []
        assert data["data"]["total"] == 0

    def test_get_books_with_data(self, client, seller_auth_headers, test_book_data):
        """도서가 있는 경우 목록 조회"""
        # 도서 등록
        client.post("/books/", json=test_book_data, headers=seller_auth_headers)

        response = client.get("/books/")

        data = assert_success_response(response, status_code=200)
        assert data["data"]["total"] == 1

    def test_get_books_with_keyword(self, client, seller_auth_headers, test_book_data):
        """키워드 검색"""
        client.post("/books/", json=test_book_data, headers=seller_auth_headers)

        response = client.get("/books/", params={"keyword": "테스트"})

        assert_success_response(response, status_code=200)

    def test_get_books_with_pagination(self, client, seller_auth_headers, test_book_data):
        """페이지네이션"""
        # 여러 도서 등록
        for i in range(3):
            book_data = test_book_data.copy()
            book_data["isbn"] = f"978-89-1234-{i:03d}"
            book_data["title"] = f"테스트도서{i}"
            client.post("/books/", json=book_data, headers=seller_auth_headers)

        response = client.get("/books/", params={"page": 1, "size": 2})

        data = assert_success_response(response, status_code=200)
        assert len(data["data"]["books"]) <= 2

    def test_get_books_with_sort(self, client, seller_auth_headers, test_book_data):
        """정렬 옵션"""
        client.post("/books/", json=test_book_data, headers=seller_auth_headers)

        response = client.get("/books/", params={"sort": "price_desc"})

        assert_success_response(response, status_code=200)


class TestGetBookDetail:
    """도서 상세 조회 테스트"""

    def test_get_book_detail_success(self, client, seller_auth_headers, test_book_data):
        """정상 상세 조회"""
        # 도서 등록
        create_response = client.post("/books/", json=test_book_data, headers=seller_auth_headers)
        book_id = create_response.json()["data"]["id"]

        response = client.get(f"/books/{book_id}")

        data = assert_success_response(response, status_code=200)
        assert data["data"]["id"] == book_id
        assert data["data"]["title"] == test_book_data["title"]

    def test_get_book_detail_not_found(self, client):
        """존재하지 않는 도서"""
        response = client.get("/books/99999")

        assert_error_response(response, status_code=404)


class TestUpdateBook:
    """도서 수정 테스트"""

    def test_update_book_success(self, client, seller_auth_headers, test_book_data):
        """정상 수정"""
        # 도서 등록
        create_response = client.post("/books/", json=test_book_data, headers=seller_auth_headers)
        book_id = create_response.json()["data"]["id"]

        update_data = {
            "title": "수정된도서",
            "price": 20000
        }
        response = client.put(f"/books/{book_id}", json=update_data, headers=seller_auth_headers)

        data = assert_success_response(response, status_code=200)
        assert data["data"]["title"] == "수정된도서"
        assert float(data["data"]["price"]) == 20000

    def test_update_book_not_owner(self, client, seller_auth_headers, test_book_data, test_user2_data):
        """본인 도서가 아닌 경우"""
        # 도서 등록
        create_response = client.post("/books/", json=test_book_data, headers=seller_auth_headers)
        book_id = create_response.json()["data"]["id"]

        # 다른 사용자로 로그인
        client.post("/auth/signup", json=test_user2_data)
        login_response = client.post("/auth/login", json={
            "email": test_user2_data["email"],
            "password": test_user2_data["password"]
        })
        other_token = login_response.json()["data"]["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        # 수정 시도 (seller 권한이 없어서 403)
        update_data = {"title": "해킹시도"}
        response = client.put(f"/books/{book_id}", json=update_data, headers=other_headers)

        assert_error_response(response, status_code=403)


class TestDeleteBook:
    """도서 삭제 테스트"""

    def test_delete_book_success(self, client, seller_auth_headers, test_book_data):
        """정상 삭제 (SOLDOUT 상태로 변경)"""
        # 도서 등록
        create_response = client.post("/books/", json=test_book_data, headers=seller_auth_headers)
        book_id = create_response.json()["data"]["id"]

        response = client.delete(f"/books/{book_id}", headers=seller_auth_headers)

        assert_success_response(response, status_code=200)

    def test_delete_book_not_found(self, client, seller_auth_headers):
        """존재하지 않는 도서"""
        response = client.delete("/books/99999", headers=seller_auth_headers)

        assert_error_response(response, status_code=404)
