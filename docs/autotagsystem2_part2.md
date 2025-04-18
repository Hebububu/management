## 3. 구현 계획

### 3.1 1단계: 데이터 준비 및 초기 모델 개발 (1-2주)

#### 3.1.1 학습 데이터 준비
- 100~200개 제품을 대상으로 정확한 수동 태깅 진행
- 다양한 제품군과 패턴을 포괄하는 대표성 있는 데이터셋 구성
- 회사명, 카테고리, 태그에 대한 명확한 레이블링

#### 3.1.2 특성 추출 모듈 개발
```python
class FeatureExtractor:
    def __init__(self, config=None):
        self.config = config or {}
        self.text_vectorizer = self._initialize_text_vectorizer()
    
    def extract_features(self, product_data):
        """제품 데이터에서 특성 추출"""
        features = {}
        
        # 텍스트 특성 추출
        text_features = self._extract_text_features(product_data.get('sale_name', ''))
        features['text'] = text_features
        
        # 구조적 특성 추출
        struct_features = self._extract_structural_features(
            product_data.get('platform', ''),
            product_data.get('data', {})
        )
        features['structural'] = struct_features
        
        return features
    
    def _extract_text_features(self, text):
        """텍스트 데이터에서 특성 추출"""
        # 텍스트 전처리
        text = self._preprocess_text(text)
        
        # 특성 벡터화
        text_vector = self.text_vectorizer.transform([text])
        
        return text_vector
    
    def _extract_structural_features(self, platform, data):
        """구조적 데이터에서 특성 추출"""
        features = {}
        
        # 플랫폼 원-핫 인코딩
        features['platform'] = self._encode_platform(platform)
        
        # 데이터 구조 특성 추출
        if platform == 'naverCommerce':
            features.update(self._extract_naver_features(data))
        elif platform == 'cafe24':
            features.update(self._extract_cafe24_features(data))
        
        return features
    
    def _preprocess_text(self, text):
        """텍스트 전처리 (정규화, 불용어 제거 등)"""
        # 구현...
        return text
    
    def _initialize_text_vectorizer(self):
        """텍스트 벡터화 모델 초기화"""
        # TF-IDF 또는 Word Embeddings 모델 초기화
        # 구현...
        pass
```

#### 3.1.3 초기 모델 개발
```python
from sklearn.ensemble import RandomForestClassifier
import joblib

class ProductTaggerML:
    def __init__(self, config=None):
        self.config = config or {}
        self.feature_extractor = FeatureExtractor(self.config)
        self.models = {
            'company': self._create_model('company'),
            'category': self._create_model('category'),
            'tags': self._create_model('tags')
        }
    
    def train(self, training_data):
        """모델 학습"""
        X = []
        y_company = []
        y_category = []
        y_tags = []
        
        # 학습 데이터 처리
        for product in training_data:
            features = self.feature_extractor.extract_features(product)
            X.append(features)
            
            y_company.append(product.get('company', ''))
            y_category.append(product.get('category', ''))
            y_tags.append(product.get('tags', ''))
        
        # 모델 학습
        self.models['company'].fit(X, y_company)
        self.models['category'].fit(X, y_category)
        self.models['tags'].fit(X, y_tags)
    
    def predict(self, product_data):
        """태그 예측"""
        features = self.feature_extractor.extract_features(product_data)
        
        predictions = {
            'company': self.models['company'].predict([features])[0],
            'category': self.models['category'].predict([features])[0],
            'tags': self.models['tags'].predict([features])[0]
        }
        
        return predictions
    
    def save_models(self, directory):
        """모델 저장"""
        for name, model in self.models.items():
            joblib.dump(model, f"{directory}/{name}_model.pkl")
    
    def load_models(self, directory):
        """모델 로드"""
        for name in self.models:
            self.models[name] = joblib.load(f"{directory}/{name}_model.pkl")
    
    def _create_model(self, model_type):
        """모델 유형에 따른 모델 생성"""
        # 간단히 RandomForest 사용 (향후 다른 알고리즘으로 대체 가능)
        return RandomForestClassifier()
```

### 3.2 2단계: 피드백 시스템 및 통합 개발 (1-2주)

#### 3.2.1 피드백 시스템 구현
```python
class FeedbackSystem:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def record_feedback(self, product_id, original_tags, corrected_tags, user_id=None):
        """사용자 피드백 기록"""
        feedback_data = {
            'product_id': product_id,
            'original_tags': original_tags,
            'corrected_tags': corrected_tags,
            'user_id': user_id,
            'timestamp': datetime.now()
        }
        
        # 데이터베이스에 피드백 저장
        self.db.save_feedback(feedback_data)
        
        return True
    
    def get_feedback_data(self, since_timestamp=None):
        """수집된 피드백 데이터 조회"""
        query = {}
        if since_timestamp:
            query['timestamp'] = {'$gt': since_timestamp}
        
        return self.db.get_feedback(query)
    
    def update_training_data(self, feedback_data):
        """피드백을 학습 데이터에 반영"""
        # 피드백 데이터를 학습 데이터 형식으로 변환
        training_samples = []
        
        for feedback in feedback_data:
            product = self.db.get_product(feedback['product_id'])
            if product:
                # 수정된 태그로 학습 샘플 생성
                sample = {
                    'sale_name': product['sale_name'],
                    'data': product['data'],
                    'platform': product['platform'],
                    'company': feedback['corrected_tags'].get('company'),
                    'category': feedback['corrected_tags'].get('category'),
                    'tags': feedback['corrected_tags'].get('tags')
                }
                training_samples.append(sample)
        
        return training_samples
```

#### 3.2.2 통합 시스템 구현
```python
class AutoTaggingSystem:
    def __init__(self, config=None):
        self.config = config or {}
        self.db = self._initialize_db_connection()
        self.ml_tagger = ProductTaggerML(self.config)
        self.feedback_system = FeedbackSystem(self.db)
        
        # 모델 로드 또는 초기 학습
        self._initialize_models()
    
    def tag_product(self, product_id):
        """제품 자동 태깅"""
        # 제품 정보 조회
        product = self.db.get_product(product_id)
        if not product:
            return {"error": "Product not found"}
        
        # 태그 예측
        predictions = self.ml_tagger.predict(product)
        
        # 결과 반환
        result = {
            "product_id": product_id,
            "predictions": predictions,
            "confidence_scores": self._get_confidence_scores(predictions)
        }
        
        return result
    
    def process_feedback(self, product_id, corrected_tags, user_id=None):
        """사용자 피드백 처리"""
        # 원본 예측 태그 가져오기
        product = self.db.get_product(product_id)
        original_predictions = self.ml_tagger.predict(product)
        
        # 피드백 기록
        self.feedback_system.record_feedback(
            product_id, 
            original_predictions, 
            corrected_tags, 
            user_id
        )
        
        # 학습 데이터에 피드백 반영 (선택적)
        self._update_model_if_needed()
        
        return {"status": "success", "message": "Feedback recorded"}
    
    def _initialize_models(self):
        """모델 초기화"""
        try:
            # 저장된 모델 로드 시도
            self.ml_tagger.load_models(self.config.get('model_directory', './models'))
        except:
            # 모델이 없으면 초기 학습 데이터로 학습
            initial_data = self.db.get_tagged_products(limit=200)
            if initial_data:
                self.ml_tagger.train(initial_data)
                
                # 학습된 모델 저장
                self.ml_tagger.save_models(self.config.get('model_directory', './models'))
    
    def _update_model_if_needed(self):
        """필요시 모델 업데이트"""
        # 마지막 업데이트 이후 축적된 피드백 수 확인
        feedback_count = len(self.feedback_system.get_feedback_data(
            since_timestamp=self.config.get('last_model_update')
        ))
        
        # 설정된 임계값 초과시 모델 재학습
        if feedback_count >= self.config.get('feedback_threshold', 20):
            self._retrain_models()
    
    def _retrain_models(self):
        """모델 재학습"""
        # 기존 학습 데이터 로드
        training_data = self.db.get_tagged_products(limit=500)
        
        # 피드백 데이터 추가
        feedback_data = self.feedback_system.get_feedback_data()
        feedback_samples = self.feedback_system.update_training_data(feedback_data)
        
        training_data.extend(feedback_samples)
        
        # 모델 재학습
        self.ml_tagger.train(training_data)
        
        # 업데이트된 모델 저장
        self.ml_tagger.save_models(self.config.get('model_directory', './models'))
        
        # 마지막 업데이트 시간 기록
        self.config['last_model_update'] = datetime.now()
```