import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.core.database import Base
from app.main import app

# 테스트용 인메모리 SQLite 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """SQLite Foreign Key 제약 조건 활성화.

    SQLite는 기본적으로 Foreign Key 제약을 비활성화하고 있어,
    테스트 환경에서 데이터 무결성 검증이 제대로 이루어지지 않을 수 있습니다.
    이 이벤트 리스너를 통해 Foreign Key 제약을 강제로 활성화합니다.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 테이블은 한 번만 생성
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """각 테스트마다 새로운 DB 세션 제공.

    이 fixture는 테스트 함수에서 직접 DB 조작이 필요할 때 사용됩니다.
    StaticPool을 사용하여 동일한 in-memory DB를 공유하지만,
    세션은 독립적으로 관리됩니다.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()  # 혹시 모를 미완료 트랜잭션 롤백
        db.close()


@pytest.fixture(scope="function", autouse=True)
def cleanup_db(request):
    """각 테스트 후 DB 데이터를 정리합니다.

    autouse=True로 설정하여 모든 테스트에 자동 적용됩니다.
    테스트 전에는 실행하지 않고, 테스트 후에만 실행합니다.
    """
    yield
    # 테스트 후에만 실행 - fixture setup 중에는 실행되지 않음
    if request.node.name:  # 실제 테스트 함수인 경우에만
        db = TestingSessionLocal()
        try:
            # Foreign key 제약을 고려하여 역순으로 삭제
            for table in reversed(Base.metadata.sorted_tables):
                db.execute(table.delete())
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()


@pytest.fixture(scope="function")
def client():
    """테스트 클라이언트.

    각 API 요청마다 새로운 세션을 생성하여 트랜잭션 격리를 보장합니다.
    StaticPool을 사용하므로 동일한 in-memory DB를 공유하지만,
    세션은 독립적으로 관리되어 테스트 간 격리를 보장합니다.
    """
    def override_get_db():
        """테스트용 DB 세션 (매 요청마다 새로운 세션 생성)"""
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

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
