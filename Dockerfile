# 베이스 이미지
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (MySQL 클라이언트 등)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 파이썬 라이브러리 설치를 위해 requirements.txt 먼저 복사
COPY ./requirements.txt .

# 파이썬 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사 (Docker Compose에서 볼륨 마운트 시 덮어쓰기 됨)
COPY ./app ./app

# 포트 노출
EXPOSE 8000

# 기본 실행 명령어 (docker-compose에서 override 가능)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
