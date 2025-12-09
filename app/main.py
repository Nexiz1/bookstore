from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.utils import setup_logging
from app.middleware import LoggingMiddleware
from app.api.routers import items, users
from app.exceptions.handlers import add_exception_handlers


def create_app() -> FastAPI:
    # 로깅 초기화
    setup_logging()

    # 데이터베이스 테이블 생성
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )

    # 미들웨어 등록 (역순으로 실행됨)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # 라우터 등록
    app.include_router(items.router, prefix="/items", tags=["items"])
    app.include_router(users.router, prefix="/users", tags=["users"])

    # 예외 핸들러 등록
    add_exception_handlers(app)

    return app

app = create_app()

@app.get("/")
def read_root():
    return {"Hello": "World"}
