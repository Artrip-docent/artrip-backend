# Artrip Backend

AI 기반 미술 전시 도슨트 서비스의 Django REST API 백엔드입니다.

## 기술 스택

| 분류 | 기술 |
|------|------|
| 프레임워크 | Django 5.1.5, Django REST Framework 3.15.2 |
| 데이터베이스 | MySQL (관계형), MongoDB (대화 로그) |
| 인증 | JWT (SimpleJWT), Kakao OAuth (django-allauth) |
| AI / ML | OpenAI GPT-4o-mini, CLIP, LangChain 0.3, Pinecone 5.4 |
| 이미지 처리 | PyTorch, torchvision, Pillow |
| 벡터 검색 | Faiss (로컬), Pinecone (클라우드) |
| 크롤링 | Selenium |
| API 문서 | drf-yasg (Swagger / Redoc) |

## 프로젝트 구조

```
artrip-backend/
├── Artrip/                  # 프로젝트 설정
│   ├── settings.py
│   ├── urls.py
│   └── utils/
├── accounts/                # 회원가입, 로그인, Kakao OAuth, 프로필
├── artworks/                # 작품 관리, CLIP 이미지 검색, 선호도 분석
├── chat/                    # AI 도슨트 챗봇, MongoDB 대화 저장
├── exhibition/              # 전시 데이터, 갤러리, 좋아요
├── reviews/                 # 전시 리뷰 (별점 1~5)
├── crawler/                 # 네이버 전시 크롤러 (Selenium)
├── indexes/                 # Faiss 인덱스 파일 (artwork.index, artwork_ids.npy)
├── requirements.txt
├── manage.py
└── docker-compose.yml
```

## 핵심 기능

### 1. CLIP 기반 작품 이미지 검색
사용자가 촬영한 작품 사진을 OpenAI CLIP 모델로 벡터화하여 Faiss 인덱스에서 유사 작품 상위 3개를 반환합니다.

### 2. AI 도슨트 챗봇 (SSE 스트리밍)
GPT-4o-mini와 LangChain RAG를 결합하여 전시·작품 관련 질문에 실시간 스트리밍(SSE)으로 답변합니다. 대화 컨텍스트는 MongoDB에, 작품 문서 임베딩은 Pinecone에 저장됩니다.

### 3. 사용자 선호도 분석
사용자가 조회한 작품 이력을 GPT-4로 분석해 스타일·감성 태그를 추출합니다.

### 4. 전시 크롤링
Selenium으로 네이버 검색 결과에서 전시 정보를 자동 수집합니다.

## 주요 API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/auth/register/` | 회원가입 |
| POST | `/auth/login/` | 로그인 (JWT 발급) |
| POST | `/artworks/upload/` | 작품 이미지 업로드 및 유사 작품 검색 |
| POST | `/artworks/analyze-preference/` | 선호도 분석 |
| GET | `/artworks/random/` | 랜덤 작품 추천 |
| POST | `/api/chat/` | AI 도슨트 채팅 (SSE) |
| GET | `/api/chat/history` | 채팅 기록 조회 |
| GET | `/api/exhibition/` | 전시 목록 |
| GET | `/api/exhibition/search/` | 전시 검색 |
| POST | `/api/exhibition/toggle-like/` | 전시 좋아요 토글 |
| POST | `/api/reviews/reviews/` | 리뷰 작성 |
| GET | `/api/artworks/viewinghistory/{user_id}/` | 관람 전시 기록 |
| GET | `/api/artworks/viewinghistory/{user_id}/{exhibition_id}/` | 전시별 작품 기록 |

> Swagger UI: `/swagger/` | Redoc: `/redoc/`

## 환경 설정

### 1. 저장소 클론 및 의존성 설치

```bash
git clone <repository-url>
cd artrip-backend
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 프로젝트 루트에 생성합니다.

```env
# Django
SECRET_KEY=your-django-secret-key
DEBUG=True

# MySQL
DB_NAME=artrip
DB_USER=root
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=3306

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=artrip
MONGODB_COLLECTION=chat_logs

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Pinecone
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=artrip-index

# Kakao OAuth
KAKAO_CLIENT_ID=your-kakao-client-id
KAKAO_CLIENT_SECRET=your-kakao-client-secret
```

### 3. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

### 4. 서버 실행

```bash
python manage.py runserver
```

### Docker로 실행

```bash
docker-compose up -d
```

## 데이터베이스 구조

| 저장소 | 용도 |
|--------|------|
| MySQL | 사용자, 작품, 전시, 갤러리, 리뷰, 관람 이력 |
| MongoDB | 채팅 대화 로그 전문 저장 |
| Pinecone | 작품·전시 문서 임베딩 (RAG용) |
| Faiss (로컬) | CLIP 작품 이미지 임베딩 인덱스 |

## Faiss 인덱스 구성

`indexes/` 디렉터리에 사전 구축된 인덱스 파일이 필요합니다.

- `artwork.index` — CLIP 임베딩으로 구축된 Faiss IVF 인덱스
- `artwork_ids.npy` — 인덱스 벡터 ↔ 작품 ID 매핑

인덱스 재구축이 필요한 경우 `artworks` 앱의 빌드 스크립트를 참고하세요.

## 전시 크롤러 실행

```bash
python manage.py crawl_exhibitions
```

## 개발 환경 요구사항

- Python 3.10 이상
- MySQL 8.0 이상
- MongoDB 6.0 이상
- CUDA (GPU) 또는 CPU 환경 모두 지원 (Faiss-CPU 사용)
