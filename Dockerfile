# Python 3.11 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 라이브러리 설치
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# uploads 디렉토리 생성
RUN mkdir -p ./uploads

# 포트 설정
EXPOSE 8080

# Gunicorn으로 실행 (shell 형식으로 환경변수 사용)
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --log-level info
