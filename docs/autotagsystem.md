# 제품 태그 자동화 시스템 설계 및 구현 가이드

## 1. 개요

### 1.1 현재 문제점
- 제품의 태그(`product_name`, `category`, `company`, `tags`)를 Discord 봇 명령어를 통해 수동으로 입력
- 전체 2,453개 제품 중 태그가 있는 제품은 54개(2.2%)에 불과함
- 수동 작업으로는 감당하기 어려운 양의 데이터

### 1.2 해결 방안
- 자동화 알고리즘을 통해 `sale_name`과 `data` JSON 필드에서 패턴을 분석해 자동으로 태그 부여
- 계층적 접근법: 기본 키워드 매칭 → 퍼지 매칭 → 유사 제품 기반 추론
- 사용자 피드백을 학습에 반영하여 지속적으로 알고리즘 개선

## 2. 자동 태깅 알고리즘

### 2.1 기본 구조
- `ProductTagger` 클래스: 제품에 태그를 부여하는 핵심 알고리즘
- 회사명, 카테고리, 제품명, 태그를 순차적으로 추출
- 추출된 정보로 DB 업데이트

### 2.2 키워드 기반 매칭 (1단계)
```python
def extract_company(self, sale_name):
    """판매명에서 회사/브랜드명 추출"""
    sale_name_lower = sale_name.lower()
    for company in self.known_companies:
        if company.lower() in sale_name_lower:
            return company
    return None
```

- 장점: 빠르고 간단함, 명확한 매칭일 경우 정확함
- 단점: 새로운 패턴, 오타, 변형에 취약함

### 2.3 퍼지 매칭 (2단계)
```python
def extract_company_fuzzy(self, sale_name):
    """퍼지 매칭으로 회사/브랜드명 추출"""
    # fuzzywuzzy 라이브러리 사용
    words = sale_name.split()
    for word in words:
        if len(word) < 3:  # 너무 짧은 단어는 건너뛰기
            continue
        best_match, score = process.extractOne(word, self.known_companies)
        if score >= 75:  # 75% 이상 유사도
            return best_match
    return None
```

- 장점: 오타나 변형된 표현에도 대응 가능
- 단점: 키워드 매칭보다 느림, 가끔 잘못된 매칭 가능성

### 2.4 유사 제품 기반 추론 (3단계)
```python
def enhance_with_similar_products(self, db_connection, sale_name, tag_result):
    """유사 제품을 기반으로 태그 결과 보완"""
    if not tag_result["company"] or not tag_result["category"]:
        similar_products = self.find_similar_products(db_connection, sale_name)
        if similar_products and similar_products[0][0] >= 70:  # 70% 이상 유사도
            best_match = similar_products[0][1]
            # 빈 값을 유사한 제품의 값으로 채우기
            if not tag_result["company"] and best_match["company"]:
                tag_result["company"] = best_match["company"]
            # ... 다른 필드도 유사하게 처리
    return tag_result
```

- 장점: 이전에 태그된 제품의 정보를 활용해 정확도 향상
- 단점: 유사한 제품이 없으면 효과 없음, 계산 비용 높음

## 3. 피드백 학습 시스템

### 3.1 사용자 피드백 수집
```python
def record_feedback(self, product_id, original_values, corrected_values):
    """태그 수정 피드백 기록"""
    # 피드백 데이터베이스에 수정 내용 저장
    # 원본 태그와 수정된 태그 비교하여 패턴 학습
```

### 3.2 패턴 학습 및 활용
```python
def update_learned_patterns(self, cursor):
    """피드백을 기반으로 학습된 패턴 업데이트"""
    # 여러 번 수정된 패턴을 찾아 신뢰도 계산
    # 신뢰도가 높은 패턴은 향후 태깅에 활용
```

- 사용자가 수정한 내용을 학습 데이터로 활용
- 시간이 지날수록 알고리즘의 정확도 향상
- 새로운 브랜드, 카테고리 등장 시 자동으로 학습

## 4. 구현 계획

### 4.1 기본 태깅 시스템 구현 (1-2일)
- `ProductTagger` 클래스 구현
- 하드코딩된 키워드 기반 매칭 구현
- Discord 명령어 기본 구조 구현

### 4.2 알고리즘 개선 및 배치 처리 (2-3일)
- 퍼지 매칭 구현 (fuzzywuzzy 활용)
- 유사 제품 기반 추론 구현
- 대량 처리 배치 시스템 구현

### 4.3 피드백 시스템 및 UI 개선 (1-2일)
- 피드백 데이터베이스 구조 설계
- 학습 알고리즘 구현
- Discord UI 개선 (버튼, 모달 등)

### 4.4 자동화 및 주기적 실행 (1일)
- 신규 제품 자동 태그 시스템
- 정기적인 검증 및 업데이트 작업

## 5. 필요한 라이브러리 및 기술

### 5.1 핵심 라이브러리
- **fuzzywuzzy**: 문자열 유사도 계산 (`pip install fuzzywuzzy`)
- **python-Levenshtein**: fuzzywuzzy 성능 향상 (`pip install python-Levenshtein`)
- **sqlite3**: 데이터베이스 작업 (Python 표준 라이브러리)
- **re**: 정규표현식 처리 (Python 표준 라이브러리)

### 5.2 추가 라이브러리 (선택사항)
- **pandas**: 대량 데이터 처리 성능 향상
- **nltk**: 자연어 처리 기능 추가

## 6. Discord 봇 명령어

### 6.1 자동 태그 명령어
- `;;auto_tag_products [limit] [preview/apply]`: 자동으로 제품에 태그 부여
  - limit: 처리할 제품 수 (기본값: 10)
  - mode: preview(미리보기) 또는 apply(적용)

```
예: ;;auto_tag_products 50 preview  # 50개 제품 태그 미리보기
    ;;auto_tag_products 100 apply   # 100개 제품에 태그 적용
```

### 6.2 개별 제품 태그 명령어
- `;;preview_auto_tag <product_id>`: 특정 제품의 자동 태그 미리보기

```
예: ;;preview_auto_tag 123  # ID가 123인 제품의 태그 미리보기
```

### 6.3 태그 통계 명령어
- `;;tag_statistics`: 제품 태그 통계 정보 확인

### 6.4 피드백 명령어
- `;;tag_feedback <product_id> <feedback_type> [message]`: 태그 알고리즘 개선 피드백 제공

## 7. 코드 구현 예시

### 7.1 ProductTagger 클래스
```python
class ProductTagger:
    def __init__(self):
        # 알려진 회사/브랜드명
        self.known_companies = [
            "고드름", "크로닉쥬스", "파이브폰즈", "디톡스", "애플힙", 
            "긱베이프", "칠렉스", "이그니스", "이지스"
        ]
        
        # 카테고리별 키워드
        self.category_keywords = {
            "액상": ["액상", "주스", "ml", "mg", "니코틴", "입호흡액상", "폐호흡액상"],
            "기기": ["기기", "디바이스", "모드", "입호흡기기", "폐호흡기기"],
            "팟": ["팟", "pod", "카트리지", "공팟", "일체형팟"],
            "코일": ["코일", "저항", "옴", "ohm"],
            "일회용기기": ["일회용", "전담", "전자담배"]
        }
        
        # 용량 및 니코틴 정규식
        self.volume_pattern = re.compile(r'(\d+)\s*ml', re.IGNORECASE)
        self.nicotine_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*mg', re.IGNORECASE)
    
    def tag_product(self, product):
        """제품에 태그 부여"""
        sale_name = product["sale_name"]
        data_json = json.loads(product["data"]) if isinstance(product["data"], str) else product["data"]
        
        # 단계적 추출 과정...
        company = self.extract_company(sale_name) or self.extract_company_fuzzy(sale_name)
        category = self.extract_category(sale_name, data_json)
        product_name = self.extract_product_name(sale_name, company)
        tags = self.extract_tags(sale_name, data_json, company, category)
        
        return {
            "company": company,
            "category": category,
            "product_name": product_name,
            "tags": tags
        }
    
    # 기타 메서드 구현...
```

### 7.2 Discord Cog 구현
```python
class TaggerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "management.db"
        self.tagger = ProductTagger()
        self.feedback_learner = FeedbackLearner(self.db_path)
    
    @commands.command(name="auto_tag_products")
    async def auto_tag_products(self, ctx, limit: int = 10, mode: str = "preview"):
        """제품에 자동으로 태그 부여"""
        # 구현 내용...
    
    @commands.command(name="preview_auto_tag")
    async def preview_auto_tag(self, ctx, product_id: int):
        """특정 제품의 자동 태그 미리보기"""
        # 구현 내용...
    
    # 기타 명령어 구현...
```

## 8. 고려사항 및 개선 방향

### 8.1 하드코딩 키워드의 한계
- 하드코딩된 키워드는 새로운 패턴 인식에 취약
- 해결책: 퍼지 매칭, 자가 학습 시스템, 단어 임베딩 활용

### 8.2 성능 최적화
- 유사도 계산은 계산 비용이 높음
- 해결책: 캐싱, 배치 처리, 인덱싱 최적화

### 8.3 정확도 향상
- 초기에는 정확도가 낮을 수 있음
- 해결책: 사용자 피드백 기반 지속적 학습, 하이브리드 접근법

### 8.4 실용적 접근법
- 완벽한 자동화보다 수동 작업 80-90% 대체에 집중
- 단계적 구현: 기본 기능 → 고급 기능
- 지속적인 모니터링 및 개선

## 9. 결론

제품 태그 자동화 시스템은 수천 개의 제품을 효율적으로 관리하는 강력한 도구가 될 수 있습니다. 단계적 접근 방식과 지속적인 학습을 통해 시간이 지날수록 더 똑똑해지는 시스템을 구축할 수 있습니다. 초기에는 하드코딩된 규칙으로 시작하더라도, 퍼지 매칭과 유사 제품 비교, 사용자 피드백 학습을 통해 점진적으로 정확도를 높일 수 있습니다.

이 문서의 구현 가이드를 따라 기본 시스템을 구축한 후, 실제 사용 경험에 따라 지속적으로 개선해 나가는 것이 바람직합니다. 결국 완벽한 자동화는 어렵더라도, 수동 작업의 대부분을 대체하여 관리 효율성을 크게 높일 수 있을 것입니다.
