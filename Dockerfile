# 베이스 이미지 선택
FROM python:3.11

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 설치를 위한 파일 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 전체 코드 복사
COPY . .

# 포트 설정 (기본 8000)
EXPOSE 8000

# 기본 실행 명령
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
