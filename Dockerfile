FROM python:3.11

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 설치 파일 복사
COPY requirements.txt .

# OS 패키지 설치 및 크롬/크롬드라이버 설치
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libgbm-dev \
    libglib2.0-0 \
    chromium \
    chromium-driver && \
    rm -rf /var/lib/apt/lists/*

# 환경 변수 설정
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 파이썬 패키지 설치
RUN pip install --upgrade pip && pip install -r requirements.txt

# 앱 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 기본 명령어 설정
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

