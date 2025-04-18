# 250407

```md
카페24 토큰 매니저 만들기
임시 상품 데이터 긁어오고 검증하기
저장해야 할 데이터 정의하기
긁어온 데이터 검증하기
데이터베이스에 인서트하기
```

# 250409
fetch 할 데이터 정의

- platform
- seller_id
- product_id
- company 
- sale_name
- product_name
- data

platform은 하드코딩
seller_id는 유동적으로 가져오게 (Args로 가져오는걸로 해결봄.)

scripts에 cafe24datamanager 만들어서 class로 관리하기
data fetch, insert 로직까지 만들면 될듯..? (Data fetch 까지는 됐음)

db 정의하고 alembic init부터 하자. (끝남)

외부 키 참조를 ForeignKeyConstiraint로 정의함 (Product 테이블에 UniqueConstirant 추가)

밥먹고 할것
alembic base.metadata 설정 (models 임포트 했어야 했음. 실수함.)
마이그레이션 생성 및 적용 (끝났음.)
실제 테이블 생성된거 확인하기 (잘 됐음.)

alembic 도입 완료

CRUD 구현 생각하기 (일단 CREATE부터 만들건데, 각 플랫폼별로 data가 다르니까 각각의 datamanager에서 정리하고 업로드하는 방식으로 하는게 좋을 거 같음. 밑에서 계속)

DB에 인서트할 데이터 정렬(데이터에서 필요한 정보만 추출하여 바로 INSERT 가능하게끔 정리하기..)

fetch -> fetch 한 데이터에서 platform, seller_id, product_id, company(손수입력해야함), sale_name, product_name (손수입력해야함), data(fetch한 그대로 오리지널 데이터 사용), created_at(datetime 규격), updated_at(datetime 규격) 추출 및 삽입하기 -> DB INSERT 할 수 있게 객체로 만들기 -> 실제 DB 인서트

# 250410

## product_name 정규식 표현 생각하기

모든 정보를 넣으려고 하지 말고 쓸 정보만 추려내는 식으로 하자. 
어차피 margin 테이블에서 category로 넣어야 하는데.. 

차라리 product 테이블에도 category를 넣고, 그 카테고리 입력 후에 product_name 정규화하는게 나을지도 모름

select_category 메소드로 카테고리 선택 구현함. 

정규식 표현대로 sort_products_data에 구현


## 대분류 
- 대분류 | 액상 / 기기 / 무화기 / 코일 / 팟 / 일회용기기 / 악세사리 / 기타

### 액상
- 액상 소분류 | 입호흡액상 / 폐호흡액상 / 첨가제 / 기타액상
- 액상 용량 옵션명 | 60ml / 30ml / 100ml (혹은 직접입력)
- 액상 니코틴 함유량 옵션명 | 3mg / 6mg / 9mg / 무니코틴 / (혹은 직접입력) // 저농도 묶어서 저장하는 로직 생각하기 

### 기기
- 기기 소분류 | 입호흡기기 / 폐호흡기기 / AIO기기 / 기타기기
- 기기 옵션명 | 자유입력(혹은 생략)

### 무화기
- 무화기 소분류 | RDA / RTA / RDTA / 기성탱크 / 팟탱크 / AIO팟 / 일회용 / 기타무화기
- 무화기 옵션명 | 입호흡탱크 / 폐호흡탱크
- 무화기 세부 옵션 | 자유입력(혹은 생략)

### 코일
- 코일 옵션명 | 자유입력(혹은 생략)

### 팟
- 팟 소분류 | 일체형팟 / 공팟 / 기타팟
- 옴 옵션 | 자유입력(혹은 생략)

### 일회용기기
- 일회용기기 소분류 | 일체형 / 교체형 / 무니코틴 / 기타일회용기기
- 일회용기기 옵션명 | 배터리 / 카트리지 (교체형인 경우) / 혹은 자유입력 혹은 생략 

### 악세사리
- 악세사리 소분류 | 경통 / 드립팁 / 캡 / 케이스 / 도어 / 배터리 / 충전기 / 리빌드용품 / 기타악세사리
- 악세사리 옵션명 | 자유입력(혹은 생략)

### 기타
- 기타 옵션명 | 자유입력(혹은 생략)

</br></br>

## 구현 방법 생각..?

product_name = '회사명'|'제품명'
tags = '소분류'|'소분류 하위 소분류'|'옵션명'(선택사항)

소모품인경우 옵션명 사용.. 이 잦을듯 (옴수라던가..)
액상의 경우 company가 애매한 경우가 많은데.. 

1. 수입사를 company에 넣을 것인가. (자사액상의 경우 이게 맞는데)
2. 제조업체를 company에 넣을 것인가. (다수의 도매몰에서 판매하는 경우)
3. 제조사 자체가 모호한 경우.. 

## 액상 카테고리 기입

1. 자사액상 -> 제조사 기입
2. 브랜드 액상 -> 제조업체 기입
3. 비주류 액상 -> 액상명 기입

## 로직

sort_products_data 메소드에서 category 입력

입력된 카테고리 = 대분류

대분류에 맞는 소분류 선택 -> 옵션명 입력 (위에 정의한 대로 구현)

이게 discord.py로 구현할때는 Args로 받아야 할 거 같으니까 나중에 함수 수정해야할듯


위에꺼 대충 다 하고 할거

insert_all_products 메소드 구현

실제 DB 삽입 노가다 시작.. 

DB 삽입을 일괄로 하지 말고, 입력할때마다 1개씩 삽입하도록 하는게 나을듯. 
중간에 끊었을 때 답이 없다.

# 250414

위에서 생각한 product_name 정규화 방식대로 define_product_name() 메소드를 구현했다. 

저번에 생각했던 대로 sort_products_data -> define_product_name -> insert_products 

제품 한개당 한개씩 DB에 등록하는 로직으로 만들면 될 것 같다.

제품 등록시 중복(이미 DB에 인서트 되어 있는 상품이면) data만 업데이트 하게끔 로직을 수정해야함. 

메소드 새로 만들기

get_product_by_unique_keys

create_or_update_product

unique_keys를 통해서 product 필터링
if existing_product를 통해 이미 존재하는 제품이면 data만 업데이트

product 테이블에 tags column 추가. 
product_name은 최소한의 제품명으로 수정.
tags에 소분류 및 옵션명 등등을 넣는걸로 변경

company, product_name, tags, category 같이 직접 입력해야하는 rows는 그냥 null인채로 인서트부터하고
그 뒤에 스크립트 작성해서 넣든지 말던지 할것. 

alembic으로 수정 

환경변수로 스토어별 토큰 관리하기 

# 250415

스토어별 API키 인자로 받아오게끔 tokenmanager 수정 - 했음 
S 스토어 API키 발급받고 DB INSERT - 했음

product crud 에서 update 로직 만들기 - 했음

cafe24datamanager에서 define_tags / select_category 수정 + product_name 입력 메소드 만들기

테스트코드 작성 후 카테고리 입력 + 태그 넣기

오늘 중으로 카페24 데이터는 마무리하고 네이버로 넘어가기 - 2400개라 오늘안에 못함;

UQ 제약조건에 tags도 포함시켜야함.. 

네이버 NaverTokenManager 작성
네이버 NaverDataManger 작성

- 2개 실제 API 키 발급받고 테스트해봐야함. 

product_name 및 기타 직접 입력해야 하는 정보는 일단 제끼고

전부 DB insert 부터 진행..

product 테이블에서 margin 테이블로 마이그레이션하는 스크립트 작성

(어차피 이거 스토어별로 작성해야되지 싶음)

# 250416

딴거 좀 하자.

수기입력을 디스코드 봇으로 하게 UI/UX 만들것.

Cogs 분류 생각 

product 공통 cogs / 플랫폼별 cogs 분리 

봇에서 쓸 수 있게 토큰매니저 수정해야함 

seller_id 로 prefix 입력받기..?

- fetch_{platform}_products -> DB insert -> 유저에게 embed로 unfulfilled product 알림 -> add_tags

- add_tags (product_name, tags, company, category)
    - 구현할거 생각해놓기

# 250417

네이버커머스 fetch test 
네이버커머스 data sort (제조사가 미리 기입되어있어서 편했다.)

- Cogs
productcommands 에서 제품 목록 관련 views를 따로 분리해서 페이지네이션을 만들면 좋을 것 같다. 
search_products랑 unfulfilled_products, recent_products 부분. 

product_name이랑 company를 수기가 아니라 조금이라도 자동화할 수 있는 아이디어를 생각해야한당

# 250417 - 제품 태그 자동화 시스템 구현 계획

## 현재 문제점
- Discord 봇을 통해 제품의 태그(product_name, category, company, tags) 수동으로 입력 중
- 데이터베이스에 총 2,453개 제품 중 태그가 있는 제품은 54개(2.2%)뿐임
- 수동 작업으로는 감당하기 어려운 양

## 개선 방안: 자동화 시스템 구현

### 자동화 알고리즘 핵심 요소
- `sale_name`에서 패턴 분석해 회사명, 제품명, 카테고리 추출
- `data` JSON 필드에서 옵션 정보, 제품 태그 등 추가 정보 추출
- 이미 태그된 54개 제품의 패턴 학습해서 자동화 규칙 개선

### 구현할 Discord 명령어
- `;;auto_tag_products [limit] [preview/apply]` - 여러 제품 자동 태그 부여
- `;;preview_auto_tag <product_id>` - 특정 제품 태그 미리보기
- `;;tag_statistics` - 태그 현황 통계 보기 
- `;;tag_feedback <product_id> <type> [message]` - 태그 알고리즘 개선 피드백

### 개발 단계
1. **기본 태깅 알고리즘 구현** (1-2일)
   - `ProductTagger` 클래스 개발
   - 판매명, JSON 데이터 분석 기능

2. **알고리즘 개선 및 배치 처리** (2-3일)
   - 패턴 학습/매칭 알고리즘 
   - 대량 태그 처리 배치 시스템

3. **사용자 UI 및 피드백 시스템** (1-2일)
   - 태그 편집 모달
   - 피드백 수집 시스템

4. **자동화 및 주기적 실행** (1일)
   - 신규 제품 추가 시 자동 태그 부여
   - 정기적인 태그 검증 작업

## 기대 효과
- 수동 작업 대폭 감소 (97% 이상의 제품을 자동으로 태그화)
- 일관된 태그 데이터 품질 유지
- 제품 관리 워크플로우 효율화

## 확장 계획
- 머신러닝 모델 통합 검토
- 크롤링 데이터 활용한 태그 정확도 향상

# 250418
Kiwipiepy 기반으로 태깅 시스템을 만들면 괜찮겠거니 생각했는데,
내 생각보다 너무 sale_name이 비정형화 되어 있어서 쉽지 않을 것 같다.

태깅할 정보를 조금 더 정확하게 정의한 다음, 그 정의에 맞춰 예시 데이터를 만들고
머신 러닝 모델을 만들어서 학습시키고, 피드백을 주는 방식으로 바꿔서 접근하자. 

