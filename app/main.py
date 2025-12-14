import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

# 라우터 임포트
from app.api.routers import (
    admin,
    auth,
    books,
    carts,
    favorites,
    orders,
    rankings,
    reviews,
    sales,
    sellers,
    settlements,
    users,
)
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.limiter import limiter
from app.core.redis import close_redis_client
from app.exceptions.handlers import add_exception_handlers, rate_limit_exceeded_handler
from app.middleware import LoggingMiddleware
from app.schemas.response import HealthResponse
from app.services.ranking_service import RankingService

# 모델 임포트 (테이블 생성을 위해 필요)
from app.models import (
    Book,
    Cart,
    Favorite,
    Order,
    OrderItem,
    Ranking,
    Review,
    SaleBookList,
    SaleInform,
    SellerProfile,
    Settlement,
    SettlementOrder,
    User,
)
from app.utils import setup_logging

logger = logging.getLogger(__name__)

# APScheduler 인스턴스 (전역)
scheduler = AsyncIOScheduler()


async def scheduled_ranking_cache_job():
    """스케줄러에 의해 10분마다 실행되는 랭킹 캐시 작업."""
    logger.info("Scheduled job: Refreshing ranking cache...")
    db = SessionLocal()
    try:
        await RankingService.calculate_and_cache_rankings(db)
    except Exception as e:
        logger.error(f"Scheduled ranking cache job failed: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup and shutdown events."""
    # === Startup ===
    logger.info("Application starting up...")

    # 스케줄러 시작
    scheduler.add_job(
        scheduled_ranking_cache_job,
        "interval",
        seconds=600,  # 10분마다 실행
        id="ranking_cache_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler started - ranking cache job scheduled every 10 minutes")

    # 앱 시작 시 즉시 1회 랭킹 캐시 실행 (약간의 지연 후)
    asyncio.create_task(initial_ranking_cache())

    yield

    # === Shutdown ===
    logger.info("Application shutting down...")

    # 스케줄러 종료
    scheduler.shutdown(wait=False)
    logger.info("APScheduler shutdown")

    # Redis 연결 종료
    await close_redis_client()
    logger.info("Redis connection closed")


async def initial_ranking_cache():
    """앱 시작 시 초기 랭킹 캐시 수행."""
    # DB 연결이 준비될 때까지 잠시 대기
    await asyncio.sleep(2)
    logger.info("Initial ranking cache on startup...")
    db = SessionLocal()
    try:
        await RankingService.calculate_and_cache_rankings(db)
        logger.info("Initial ranking cache completed")
    except Exception as e:
        logger.error(f"Initial ranking cache failed: {e}")
    finally:
        db.close()


def create_app() -> FastAPI:
    # 로깅 초기화
    setup_logging()

    # 데이터베이스 테이블 생성
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        description="BookStore API - 온라인 서점 백엔드 API",
        lifespan=lifespan,
    )

    # Rate Limiter 상태 저장소 설정
    app.state.limiter = limiter

    # Rate Limit 예외 핸들러 등록 (표준 에러 포맷 사용)
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # 미들웨어 등록 (역순으로 실행됨)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # 라우터 등록 (34개 엔드포인트)
    # 1. 인증 (4개): signup, login, refresh, logout
    app.include_router(auth.router, prefix="/auth", tags=["Auth"])

    # 2. 회원 (5개): /me, /me (patch), /me/password, /, /{user_id}/role
    app.include_router(users.router, prefix="/users", tags=["Users"])

    # 3. 판매자 (3개): /, /me, /me (patch)
    app.include_router(sellers.router, prefix="/sellers", tags=["Sellers"])

    # 4. 도서 (5개): /, / (get), /{book_id}, /{book_id} (put), /{book_id} (delete)
    app.include_router(books.router, prefix="/books", tags=["Books"])

    # 5. 장바구니 (4개): /, / (post), /{cart_id} (patch), /{cart_id} (delete)
    app.include_router(carts.router, prefix="/carts", tags=["Carts"])

    # 6. 주문 (4개): /, / (get), /{order_id}, /{order_id}/cancel
    app.include_router(orders.router, prefix="/orders", tags=["Orders"])

    # 7. 리뷰 (3개): /books/{book_id}/reviews (post, get), /reviews/{review_id} (delete)
    app.include_router(reviews.router, tags=["Reviews"])

    # 8. 찜하기 (3개): /books/{book_id}/favorites (post, delete), /favorites
    app.include_router(favorites.router, tags=["Favorites"])

    # 9. 랭킹 (1개): /rankings (Redis 캐시 적용)
    app.include_router(rankings.router, prefix="/rankings", tags=["Rankings"])

    # 10. 세일 (2개): /, /{sale_id}/books
    app.include_router(sales.router, prefix="/sales", tags=["Sales"])

    # 11. 정산 (1개): /settlements
    app.include_router(settlements.router, prefix="/settlements", tags=["Settlements"])

    # 12. 관리자 (1개): /admin/orders
    app.include_router(admin.router, prefix="/admin", tags=["Admin"])

    # 예외 핸들러 등록
    add_exception_handlers(app)

    return app


app = create_app()


@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to BookStore API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"], response_model=HealthResponse)
def health_check():
    """헬스 체크 엔드포인트

    서버 상태를 확인하는 엔드포인트입니다.
    인증 없이 접근 가능합니다.

    Returns:
        HealthResponse: 서버 상태, 버전, 타임스탬프
    """
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    )
