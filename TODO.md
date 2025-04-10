# 250407

```md
카페24 토큰 매니저 만들기
임시 상품 데이터 긁어오고 검증하기
저장해야 할 데이터 정의하기
긁어온 데이터 검증하기
데이터베이스에 인서트하기
```

# 250409
```md
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
```

# 250410

```md
product_name 정규식 표현 생각하기

모든 정보를 넣으려고 하지 말고 쓸 정보만 추려내는 식으로 하자. 
어차피 Margin 테이블에서 category로 넣어야 하는데.. 

차라리 product 테이블에도 category를 넣고, 그 카테고리 입력 후에 product_name 정규화하는게 나을지도 모름

정규식 표현대로 sort_products_data에 구현

- 대분류 | 액상 / 기기 / 무화기 / 소모품 / 기타
- 액상 소분류 | 입호흡액상 / 폐호흡액상 / 기타액상
- 액상 옵션명 | 60ml / 30ml / (혹은 생략)
- 액상 옵션명2 | 3mg / 6mg / 9mg / (혹은 생략)
- 기기 소분류 | 입호흡기기 / 폐호흡기기 / 기타기기

product_name = '제품명' + ' ' + '대분류' + ' ' + '소분류' + ' ' + '옵션명(선택)' 
strip을 공백으로 할지, 다른 문자열을 사용할지? ('|' 쓰는것도 나쁘지 않을 거 같은데)

소모품인경우 옵션명 사용.. 이 잦을듯
액상의 경우 company가 애매한 경우가 많은데..

1. 수입사를 company에 넣을 것인가. (자사액상의 경우 이게 맞는데)
2. 제조업체를 company에 넣을 것인가. (다수의 도매몰에서 판매하는 경우)
3. 제조사 자체가 모호한 경우.. 

로직은

대분류 선택 -> 대분류에 맞는 소분류 선택 -> 옵션명 입력(미입력시 생략)

이게 discord.py로 구현할때는 Args로 받아야 할 거 같으니까 나중에 함수 수정해야할듯


위에꺼 대충 다 하고 할거
insert_all_products 메소드 구현


```
