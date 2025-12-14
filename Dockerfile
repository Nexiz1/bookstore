FROM python:3.12-slim

WORKDIR /app

# [중요] 저장소 설정 수정
# 1. 메인 저장소(deb.debian.org)는 속도가 빠른 mirror.kakao.com으로 변경
# 2. 보안 저장소(security)는 Kakao 미러에 없는 경우가 많으므로 공식(security.debian.org) 유지
RUN if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's/deb.debian.org/mirror.kakao.com/g' /etc/apt/sources.list.d/debian.sources && \
        sed -i 's|mirror.kakao.com/debian-security|security.debian.org/debian-security|g' /etc/apt/sources.list.d/debian.sources; \
    else \
        sed -i 's/deb.debian.org/mirror.kakao.com/g' /etc/apt/sources.list && \
        sed -i 's|mirror.kakao.com/debian-security|security.debian.org/debian-security|g' /etc/apt/sources.list; \
    fi

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 실행 명령어
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]