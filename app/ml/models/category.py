"""
카테고리 분류 모델 구현
"""
import numpy as np
from typing import Dict, Any, List, Union
from sklearn.ensemble import RandomForestClassifier

from app.ml.models.base import BaseModel


class CategoryModel(BaseModel):
    """
    카테고리 분류 모델
    
    제품 특성을 바탕으로 카테고리를 예측하는 분류 모델
    """
    
    def _initialize(self):
        """
        카테고리 모델 초기화
        """
        # 기본 분류기는 RandomForest 사용
        self.model = RandomForestClassifier(
            n_estimators=self.config.get('n_estimators', 100),
            max_depth=self.config.get('max_depth', None),
            min_samples_split=self.config.get('min_samples_split', 2),
            min_samples_leaf=self.config.get('min_samples_leaf', 1),
            random_state=self.config.get('random_state', 42),
            class_weight=self.config.get('class_weight', 'balanced')
        )
        
        # 클래스 레이블 (카테고리) 목록
        self.classes_ = []
        
        # 특성 이름 목록 (디버깅 및 분석용)
        self.feature_names_ = []
        
        # 유효한 카테고리 정의 (옵션)
        self.valid_categories = self.config.get('valid_categories', [
            '액상', '기기', '무화기', '코일', '팟', '일회용기기', '악세사리', '기타'
        ])
    
    def _preprocess_features(self, features: Dict[str, Any]) -> np.ndarray:
        """
        특성 전처리
        
        Args:
            features: 추출기에서 제공한 특성
            
        Returns:
            모델 입력용 처리된 특성 벡터
        """
        # 텍스트 특성 추출
        text_features = features.get('text', {}).get('text_features', [])
        
        # 구조적 특성 추출
        structural_features = []
        
        # 플랫폼 벡터
        platform_vector = features.get('structural', {}).get('platform_vector', [])
        structural_features.extend(platform_vector)
        
        # 플랫폼별 특수 특성
        for key, value in features.get('structural', {}).items():
            if key != 'platform_vector' and isinstance(value, (int, float)):
                structural_features.append(value)
        
        # 모든 특성 결합
        combined_features = np.concatenate([
            text_features if isinstance(text_features, np.ndarray) else np.array(text_features),
            np.array(structural_features)
        ])
        
        return combined_features
    
    def fit(self, features: List[Dict[str, Any]], labels: List[str]):
        """
        카테고리 모델 학습
        
        Args:
            features: 학습 데이터 특성 리스트
            labels: 학습 데이터 카테고리 리스트
        """
        if not features or not labels or len(features) != len(labels):
            raise ValueError("특성과 레이블의 수가 일치하지 않거나 비어 있습니다.")
        
        # 전처리된 특성 생성
        X = np.array([self._preprocess_features(f) for f in features])
        y = np.array(labels)
        
        # 특성 이름 기록 (첫 번째 샘플만 사용)
        if features and 'text' in features[0] and 'text_feature_names' in features[0]['text']:
            text_feature_names = features[0]['text']['text_feature_names']
            structural_feature_count = X.shape[1] - len(text_feature_names)
            structural_feature_names = [f'structural_{i}' for i in range(structural_feature_count)]
            self.feature_names_ = text_feature_names + structural_feature_names
        
        # 모델 학습
        self.model.fit(X, y)
        
        # 클래스 목록 저장
        self.classes_ = list(self.model.classes_)
        
        self.is_fitted = True
    
    def predict(self, features: Dict[str, Any]) -> str:
        """
        카테고리 예측
        
        Args:
            features: 예측할 데이터의 특성
            
        Returns:
            예측된 카테고리
        """
        if not self.is_fitted:
            raise ValueError("모델이 학습되지 않았습니다.")
        
        # 특성 전처리
        X = self._preprocess_features(features).reshape(1, -1)
        
        # 예측 수행
        prediction = self.model.predict(X)[0]
        
        # 유효한 카테고리 검증 (옵션)
        if self.valid_categories and prediction not in self.valid_categories:
            # 가장 확률이 높은 유효한 카테고리 선택
            probabilities = self.model.predict_proba(X)[0]
            valid_indices = [i for i, c in enumerate(self.classes_) if c in self.valid_categories]
            if valid_indices:
                valid_probs = [(probabilities[i], self.classes_[i]) for i in valid_indices]
                prediction = max(valid_probs, key=lambda x: x[0])[1]
            else:
                prediction = '기타'  # 기본값
        
        return prediction
    
    def predict_proba(self, features: Dict[str, Any]) -> Dict[str, float]:
        """
        카테고리 예측 확률 계산
        
        Args:
            features: 예측할 데이터의 특성
            
        Returns:
            각 카테고리별 예측 확률
        """
        if not self.is_fitted:
            raise ValueError("모델이 학습되지 않았습니다.")
        
        # 특성 전처리
        X = self._preprocess_features(features).reshape(1, -1)
        
        # 확률 예측 수행
        probabilities = self.model.predict_proba(X)[0]
        
        # 카테고리-확률 매핑
        result = {class_name: float(prob) for class_name, prob in zip(self.classes_, probabilities)}
        
        return result
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        특성 중요도 반환
        
        Returns:
            특성별 중요도
        """
        if not self.is_fitted:
            raise ValueError("모델이 학습되지 않았습니다.")
        
        # 특성 중요도가 있는 경우
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            
            # 특성 이름이 있는 경우
            if len(self.feature_names_) == len(importances):
                return {name: float(importance) for name, importance in zip(self.feature_names_, importances)}
            else:
                return {f'feature_{i}': float(importance) for i, importance in enumerate(importances)}
        
        return {}
    
    def _get_save_metadata(self) -> Dict[str, Any]:
        """
        저장 시 추가 메타데이터 수집
        
        Returns:
            저장할 추가 메타데이터
        """
        return {
            'classes_': self.classes_,
            'feature_names_': self.feature_names_,
            'valid_categories': self.valid_categories
        }
    
    def _set_load_metadata(self, metadata: Dict[str, Any]):
        """
        로드 시 추가 메타데이터 설정
        
        Args:
            metadata: 로드된 추가 메타데이터
        """
        self.classes_ = metadata.get('classes_', [])
        self.feature_names_ = metadata.get('feature_names_', [])
        self.valid_categories = metadata.get('valid_categories', self.valid_categories)
