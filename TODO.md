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