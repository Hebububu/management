# 목표: 이커머스 서비스 통합 관리 프로젝트 개발

Cafe24, 네이버 커머스 등 다양한 이커머스 플랫폼의 제품 데이터를 통합하여 관리하고 분석하는 시스템을 개발합니다.
<br/><br/>

## 프로젝트 개발 계획 (Milestone)

[Milestone]
![Milestone](</docs/MILESTONE.png>)
- Edit URL: https://github.com/users/Hebububu/projects/2

<br/><br/>

# 통합 관리 시스템 설계
## 목차

1. [ERD Diagram](#erd-diagram)
    - [테이블 설계 상세 정의](#테이블-설계-상세-정의)
2. [플로우 차트(Flow Chart)](#플로우-차트-flow-chart)
    - [플로우 차트 설명](#플로우-차트-설명)
3. [시퀀스 다이어그램](#시퀀스-다이어그램)
    - [추가 예정](#추가-예정)
4. [FASTAPI API 생성](#FASTAPI-API)
5. [프로젝트 구조 및 실행 방법](#프로젝트-구조-및-실행-방법)
    - [프로젝트 구조](#프로젝트-구조)
    - [기술 스택](#기술-스택)
    - [프로젝트 실행 방법](#프로젝트-실행-방법)
6. [주요 컴포넌트 및 기능](#주요-컴포넌트-및-기능)
7. [데이터 관리 워크플로우](#데이터-관리-워크플로우)
8. [개발 계획](#개발-계획)
9. [기여 가이드라인](#기여-가이드라인)

<br/><br/>

## ERD Diagram
![alt text](</docs/ERD3.png>)
- Edit URL: https://dbdiagram.io/d/management-67edf5b64f7afba184293fba

### 테이블 설계 상세 정의

<details>
<summary>테이블 설계 상세 정의 내역 보기</summary>

```sql
-- 제품 테이블: 다양한 플랫폼(Cafe24, 네이버 등)에서 수집된 제품 데이터 저장
Table product {
  id integer [pk, increment]           -- 고유 식별자 (자동 증가)
  platform string [not null]           -- 플랫폼명 (카페24, 네이버 등)
  seller_id string [not null]          -- 판매자 ID
  product_id integer [not null]        -- 플랫폼별 제품 ID
  category string                      -- 제품 카테고리 (액상, 기기, 무화기 등)
  company string                       -- 제조사/공급사
  sale_name string [not null]          -- 플랫폼에 표시되는 판매명
  product_name string                  -- 관리제품명 (정규화된 실제 제품명)
  tags string                          -- 소분류 및 옵션 태그 (파이프로 구분)
  data json [not null]                 -- 플랫폼별 원본 제품 데이터 (JSON)
  created_at datetime [not null]       -- 생성 시간
  updated_at datetime [not null]       -- 업데이트 시간

  indexes {
    (platform, seller_id, company, category, product_name, tags) [unique, name: 'uq_product']
  }
}

-- 마진 테이블: 제품의 가격, 원가, 마진 정보 저장
Table margin {
  id integer [pk, increment]           -- 고유 식별자 (자동 증가)
  platform string [not null]           -- 플랫폼명 (product 테이블 참조)
  seller_id string [not null]          -- 판매자 ID (product 테이블 참조)
  company string [not null]            -- 제조사/공급사 (product 테이블 참조)
  product_name string [not null]       -- 관리제품명 (product 테이블 참조)
  price integer [not null]             -- 판매가
  cost integer [not null]              -- 원가
  marketplace_charge float [not null]  -- 마켓플레이스 수수료율
  margin integer [not null]            -- 마진 (판매가 - 원가 - 수수료 등)
  margin_rate integer [not null]       -- 마진율 (%)
  gift integer [not null]              -- 사은품 비용
  delivery_fee integer [not null]      -- 배송비
  post_fee integer [not null]          -- 발송비
  category string [not null]           -- 관리용 카테고리
  created_at datetime [not null]       -- 생성 시간
  updated_at datetime [not null]       -- 업데이트 시간

  indexes {
    (platform, seller_id, company, product_name, category) [name: 'fk_margin_product']
  }
}

-- 사용자 테이블: 시스템 사용자 정보 저장
Table user {
  id integer [pk, increment]           -- 고유 식별자 (자동 증가)
  name string [not null]               -- 사용자 이름
  email string [not null]              -- 이메일 주소
  created_at datetime [not null]       -- 계정 생성 시간
  updated_at datetime [not null]       -- 계정 업데이트 시간
}

-- 로그 테이블: 사용자 활동 및 시스템 이벤트 로그 저장
Table log {
  id integer [pk, increment]           -- 고유 식별자 (자동 증가)
  user_id integer [not null]           -- 사용자 ID (user 테이블 참조)
  type string [not null]               -- 로그 유형 (정보, 경고, 오류 등)
  source string [not null]             -- 로그 소스
  message string [not null]            -- 로그 메시지
  ip_address string [not null]         -- 클라이언트 IP 주소
  created_at datetime [not null]       -- 로그 생성 시간
}

-- 출고 테이블: 제품 출고 정보 저장
Table ob {
  id integer [pk, increment]           -- 고유 식별자 (자동 증가)
  history_id integer [not null]        -- 출고 기록 ID (ob_history 테이블 참조)
  created_at datetime [not null]       -- 출고 시간
}

-- 출고 기록 테이블: 출고 이력 상세 정보 저장
Table ob_history {
  id integer [pk, increment]           -- 고유 식별자 (자동 증가)
  platform string [not null]           -- 출고 플랫폼
  seller_id string [not null]          -- 판매자 ID
  product_id string [not null]         -- 제품 ID
  compnay string [not null]            -- 제조사/공급사 (오타: company로 수정 필요)
  product_name string [not null]       -- 제품명
  price integer [not null]             -- 판매가
  category string [not null]           -- 제품 카테고리
  amount integer [not null]            -- 출고 수량
  created_at datetime [not null]       -- 기록 생성 시간
}

-- 크롤링 데이터 테이블: 외부 사이트에서 크롤링한 제품 정보 저장
Table crawled_data {
  id integer [pk, increment]           -- 고유 식별자 (자동 증가)
  product_name string [not null]       -- 제품명 (product 테이블의 product_name과 연계)
  title string [not null]              -- 크롤링한 제품 제목
  url string [not null]                -- 제품 URL
  price integer [not null]             -- 판매가
  discount_price integer               -- 할인가
  created_at datetime [not null]       -- 생성 시간
  updated_at datetime [not null]       -- 업데이트 시간
}

-- 크롤링 쿠폰 데이터 테이블: 크롤링한 제품의 쿠폰 정보 저장
Table crawled_data_coupon {
  id integer [pk, increment]           -- 고유 식별자 (자동 증가)
  crawled_data_id integer [not null]   -- 크롤링 데이터 ID (crawled_data 테이블 참조)
  is_available boolean [not null]      -- 쿠폰 사용 가능 여부
  description string                   -- 쿠폰 설명
  discount_price integer [not null]    -- 쿠폰 할인액
}

-- 크롤링 배송 데이터 테이블: 크롤링한 제품의 배송 정보 저장
Table crawled_data_shipping {
  id integer [pk, increment]           -- 고유 식별자 (자동 증가) 
  crawled_data_id integer [not null]   -- 크롤링 데이터 ID (crawled_data 테이블 참조)
  fee integer [not null]               -- 배송비
  company string [not null]            -- 배송 회사
  condition string [not null]          -- 배송 조건
  free_condition_amount integer [not null] -- 무료 배송 조건 금액
  jeju_fee integer [not null]          -- 제주 추가 배송비
  island_fee integer [not null]        -- 도서산간 추가 배송비
}

-- 크롤링 포인트 데이터 테이블: 크롤링한 제품의 포인트/리뷰 정보 저장
Table crawled_data_point {
  id integer [pk, increment]           -- 고유 식별자 (자동 증가)
  crawled_data_id integer [not null]   -- 크롤링 데이터 ID (crawled_data 테이블 참조)
  text_point integer [not null]        -- 텍스트 리뷰 포인트
  photo_point integer [not null]       -- 포토 리뷰 포인트
  month_text_point integer [not null]  -- 이달의 텍스트 리뷰 포인트
  month_photo_point integer [not null] -- 이달의 포토 리뷰 포인트
  notification_point integer [not null] -- 구매확정 포인트
}

-- 관계 정의
Ref: "product"."id" < "margin"."id"
Ref: "user"."id" < "log"."user_id"
Ref: "ob_history"."id" < "ob"."history_id"
Ref: "crawled_data"."id" < "crawled_data_coupon"."crawled_data_id"
Ref: "crawled_data"."id" < "crawled_data_shipping"."crawled_data_id"
Ref: "crawled_data"."id" < "crawled_data_point"."crawled_data_id"

-- 복합 외래 키 제약 조건
Ref: (product.platform, product.seller_id, product.company, product.product_name, product.category) < (margin.platform, margin.seller_id, margin.company, margin.product_name, margin.category)
```

</details>

## 플로우 차트 (flow Chart)
- 추가 예정
<br/><br/>

## 시퀀스 다이어그램
- 추가 예정

## FASTAPI API
- 추가 예정

## 프로젝트 구조 및 실행 방법

### 프로젝트 구조

```
management/
├── alembic/            # 데이터베이스 마이그레이션 관련 파일
├── app/                # 애플리케이션 메인 코드
│   ├── bot/            # 디스코드 봇 관련 코드
│   │   ├── cogs/       # 봇 명령어 모듈 (카테고리별 기능)
│   │   └── views/      # 디스코드 UI 컴포넌트
│   ├── database/       # 데이터베이스 관련 코드
│   │   └── crud/       # CRUD 연산 구현
│   ├── scripts/        # 외부 API 및 데이터 처리 스크립트
│   ├── tests/          # 테스트 코드
│   └── utils/          # 유틸리티 기능 (로깅 등)
├── data/               # 데이터 파일 저장소
└── docs/               # 문서 및 다이어그램
```

### 기술 스택

- **백엔드**: Python, SQLAlchemy, FastAPI (추후 구현 예정)
- **데이터베이스**: SQLite (개발), PostgreSQL (프로덕션)
- **인터페이스**: Discord.py
- **API 통합**: 
  - Cafe24 API: OAuth 기반 인증 및 제품 데이터 관리
  - 네이버 커머스 API: 스마트스토어 제품 관리
- **데이터 마이그레이션**: Alembic
- **로깅 및 모니터링**: Python logging 라이브러리

### 프로젝트 실행 방법

#### 환경 설정

```bash
# 가상 환경 설정
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
alembic upgrade head

# 환경 변수 설정 (.env 파일)
# 봇 토큰 설정
# BOT_TOKEN=<디스코드_봇_토큰>

# Cafe24 API 설정
# [PREFIX]_CLIENT_ID=<Cafe24_클라이언트_ID>
# [PREFIX]_CLIENT_SECRET=<Cafe24_클라이언트_시크릿>
# [PREFIX]_REDIRECT_URI=<Cafe24_리다이렉트_URI>

# 네이버 커머스 API 설정
# [PREFIX]_NAVER_CLIENT_ID=<네이버_커머스_클라이언트_ID>
# [PREFIX]_NAVER_CLIENT_SECRET=<네이버_커머스_클라이언트_시크릿>

# [PREFIX]는 판매자 구분을 위한 접두어
```

#### 봇 실행

```bash
python -m app.bot.bot
```

## 주요 컴포넌트 및 기능

### 1. 디스코드 봇 시스템

이커머스 플랫폼 데이터 관리 및 모니터링을 위한 인터페이스를 제공합니다.

#### 주요 명령어

- `;;fetch_cafe24_products [seller_id]`: Cafe24 플랫폼에서 제품 정보 가져오기
- `;;fetch_navercommerce_products [seller_id]`: 네이버 커머스 플랫폼에서 제품 정보 가져오기
- `;;add_tags`: 제품에 태그, 카테고리, 회사명 등 추가 정보 입력
- `;;load [extension]`: 확장 모듈 로드
- `;;unload [extension]`: 확장 모듈 언로드
- `;;reload [extension]`: 확장 모듈 리로드

### 2. 데이터베이스 시스템

제품, 마진, 출고 기록, 크롤링 데이터 등을 저장하고 관리합니다.

- **SQLAlchemy ORM**: 객체 관계 매핑을 통한 데이터 모델링
- **마이그레이션 관리**: Alembic을 통한 데이터베이스 스키마 버전 관리
- **관계형 데이터 모델**: 제품-마진, 제품-출고, 크롤링 데이터 간의 관계 정의

### 3. API 통합 시스템

Cafe24, 네이버 커머스 등 외부 플랫폼 API와 연동하여 데이터를 수집합니다.

- **제품 정보 자동 수집**: 플랫폼별 API를 통한 제품 데이터 수집
- **토큰 관리**: API 인증 토큰 자동 갱신 및 관리
  - Cafe24 토큰 관리자: OAuth 기반 액세스 토큰 관리
  - 네이버 커머스 토큰 관리자: 클라이언트 인증 기반 토큰 발급
- **데이터 정규화**: 수집된 데이터의 일관성 확보를 위한 정규화 처리
- **여러 판매자 계정 지원**: 환경 변수를 통한 다중 판매자 계정 설정 지원

### 4. 데이터 관리 시스템

수집된 제품 데이터를 효율적으로 관리합니다.

- **데이터 정규화**: 제품명, 카테고리, 태그 등 정보 정규화
- **중복 제품 필터링**: 동일 제품의 중복 등록 방지
- **태그 시스템**: 카테고리별 소분류와 옵션을 체계적으로 관리
  - 대분류: 액상, 기기, 무화기, 코일, 팟, 일회용기기, 악세사리, 기타
  - 소분류: 각 대분류별 세부 카테고리 (예: 액상 - 입호흡액상/폐호흡액상/첨가제 등)
  - 옵션 태그: 용량, 니코틴 함량 등 상세 옵션 데이터
- **제품 데이터 업데이트**: 기존 제품 정보 자동 업데이트 기능

## 데이터 관리 워크플로우

1. **제품 데이터 수집**: 봇 명령어를 통해 플랫폼에서 데이터 수집
2. **제품 정보 정규화**: 카테고리, 태그, 제품명 등 정보 입력 및 정규화
3. **마진 정보 계산**: 제품별 원가, 판매가 등 정보를 기반으로 마진 계산
4. **데이터 분석 및 모니터링**: 판매 현황, 마진율 등 정보 모니터링

## 개발 계획

### 단기 개발 계획

- ✅ 네이버 커머스 API 연동 및 데이터 관리 기능 구현
- ✅ 카테고리별 태그 시스템 구체화 및 완성
- 디스코드 봇 UI/UX 개선
- 마진 계산 및 분석 도구 개발
- 제품 관리 명령어 확장
- 외부 사이트 제품 정보 크롤링 기능 구현

### 중장기 개발 계획

- 실시간 재고 관리 및 알림 시스템 구축
- 판매 추이, 마진율 등 데이터 분석 및 시각화
- 외부 시스템 연동을 위한 REST API 서버 구현
- 관리자용 웹 대시보드 구현

## 기여 가이드라인

1. **코드 스타일**: PEP 8 스타일 가이드 준수
2. **테스트**: 새로운 기능 추가 시 테스트 코드 작성
3. **문서화**: 코드 및 API 문서화