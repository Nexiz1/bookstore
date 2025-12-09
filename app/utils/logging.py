import logging
import sys
from app.core.config import settings


def setup_logging() -> logging.Logger:
    """애플리케이션 로깅 설정"""

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logger = logging.getLogger("app")
    logger.info(f"로깅 설정 완료 (level: {logging.getLevelName(log_level)})")

    return logger


def get_logger(name: str) -> logging.Logger:
    """모듈별 로거 생성"""
    return logging.getLogger(name)
