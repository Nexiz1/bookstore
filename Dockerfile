# 베이스 이미지
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 파이썬 라이브러리 설치를 위해 requirements.txt 먼저 복사
COPY ./requirements.txt .

# 시스템 라이브러리와 파이썬 라이브러리를 함께 설치
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY ./app ./app

# 포트 노출
EXPOSE 8000

# 기본 실행 명령어
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]