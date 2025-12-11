import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.core.database import Base
from app.main import app

# 테스트용 인메모리 SQLite 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """테스트용 DB 세션"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """각 테스트마다 새로운 DB 세션 제공"""
    # 테이블 생성은 한 번만 수행
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 테이블 삭제도 한 번만 수행
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """테스트 클라이언트"""
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """테스트용 사용자 데이터"""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "테스트유저",
        "gender": "male",
        "address": "서울시 강남구"
    }


@pytest.fixture
def test_user2_data():
    """두 번째 테스트 사용자 데이터"""
    return {
        "email": "test2@example.com",
        "password": "testpassword456",
        "name": "테스트유저2",
        "gender": "female",
        "address": "서울시 서초구"
    }


@pytest.fixture
def test_seller_data():
    """테스트용 판매자 데이터"""
    return {
        "business_name": "테스트서점",
        "business_number": "123-45-67890",
        "email": "seller@example.com",
        "address": "서울시 종로구",
        "phone_number": "02-1234-5678",
        "payout_account": "110-123-456789",
        "payout_holder": "테스트유저"
    }


@pytest.fixture
def test_book_data():
    """테스트용 도서 데이터"""
    return {
        "title": "테스트도서",
        "author": "테스트저자",
        "publisher": "테스트출판사",
        "summary": "이것은 테스트 도서입니다.",
        "isbn": "978-89-1234-567",
        "price": 15000,
        "status": "ONSALE"
    }


@pytest.fixture
def registered_user(client, test_user_data):
    """회원가입된 사용자"""
    response = client.post("/auth/signup", json=test_user_data)
    return response.json()["data"]


@pytest.fixture
def auth_headers(client, test_user_data, registered_user):
    """인증된 사용자의 헤더"""
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/auth/login", json=login_data)
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seller_user(client, auth_headers, test_seller_data, db_session):
    """판매자로 등록된 사용자"""
    response = client.post("/sellers/", json=test_seller_data, headers=auth_headers)
    return response.json()["data"]


@pytest.fixture
def seller_auth_headers(client, test_user_data, seller_user):
    """판매자 인증 헤더 (seller_user fixture 이후 사용)"""
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/auth/login", json=login_data)
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def created_book(client, seller_auth_headers, test_book_data):
    """테스트용 도서 생성"""
    response = client.post("/books/", json=test_book_data, headers=seller_auth_headers)
    return response.json()["data"]


@pytest.fixture
def buyer_headers(client, test_user2_data):
    """구매자 인증 헤더"""
    client.post("/auth/signup", json=test_user2_data)
    login_response = client.post("/auth/login", json={
        "email": test_user2_data["email"],
        "password": test_user2_data["password"]
    })
    token = login_response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, db_session):
    """관리자 인증 헤더 (DB에서 직접 권한 부여)"""
    from app.models.user import User

    # Admin 사용자 생성
    admin_data = {
        "email": "admin@example.com",
        "password": "adminpassword123",
        "name": "관리자"
    }
    client.post("/auth/signup", json=admin_data)

    # DB에서 직접 admin 권한 부여 (API 엔드포인트가 없으므로 불가피)
    admin_user = db_session.query(User).filter(User.email == "admin@example.com").first()
    admin_user.role = "admin"
    db_session.commit()

    # Admin으로 로그인
    login_response = client.post("/auth/login", json={
        "email": "admin@example.com",
        "password": "adminpassword123"
    })
    token = login_response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
