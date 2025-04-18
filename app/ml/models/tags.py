"""
태그 분류 모델 구현
"""
import re
import numpy as np
from typing import Dict, Any, List, Union
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import MultiLabelBinarizer

from app.ml.models.base import BaseModel


class TagsModel(BaseModel):
    """
    태그 분류 모델
    
    제품 특성을 바탕으로 태그를 예측하는 다중 레이블 분류 모델
    """
    
    def _initialize(self):
        """
        태그 모델 초기화
        """
        # 기본 분류기로 RandomForest 사용
        base_classifier = RandomForestClassifier(
            n_estimators=self.config.get('n_estimators', 100),
            max_depth=self.config.get('max_depth', None),
            min_samples_split=self.config.get('min_samples_split', 2),
            min_samples_leaf=self.config.get('min_samples_leaf', 1),
            random_state=self.config.get('random_state', 42),
            class_weight=self.config.get('class_weight', 'balanced')
        )
        
        # 다중 레이블 분류를 위한 멀티아웃풋 분류기
        self.model = MultiOutputClassifier(base_classifier)
        
        # 다중 레이블 이진화기
        self.mlb = MultiLabelBinarizer()
        
        # 특성 이름 목록 (디버깅 및 분석용)
        self.feature_names_ = []
        
        # 태그 사전 정의
        self.category_tags_mapping = self._initialize_category_tags_mapping()
    
    def _initialize_category_tags_mapping(self) -> Dict[str, List[str]]:
        """
        카테고리별 태그 맵핑 초기화
        
        Returns:
            카테고리별 태그 목록
        """
        return {
            '액상': ['입호흡액상', '폐호흡액상', '첨가제', '기타액상'],
            '기기': ['입호흡기기', '폐호흡기기', 'AIO기기', '기타기기'],
            '무화기': ['RDA', 'RTA', 'RDTA', '기성탱크', '팟탱크', 'AIO팟', '일회용', '기타무화기'],
            '팟': ['일체형팟', '공팟', '기타팟'],
            '일회용기기': ['일체형', '교체형', '무니코틴', '기타일회용기기'],
            '악세사리': ['경통', '드립팁', '캡', '케이스', '도어', '배터리', '충전기', '리빌드용품', '기타악세사리'],
            '코일': [],  # 코일은 소분류 없이 옵션만 사용
            '기타': []   # 기타도 소분류 없이 옵션만 사용
        }
    
    def _preprocess_tags(self, tags_str: str) -> List[str]:
        """
        태그 문자열을 태그 목록으로 변환
        
        Args:
            tags_str: '|'로 구분된 태그 문자열
            
        Returns:
            태그 목록
        """
        if not tags_str:
            return []
        
        # '|'로 구분된 태그 분리
        tags = [tag.strip() for tag in tags_str.split('|')]
        return [tag for tag in tags if tag]  # 빈 태그 제거
    
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
        태그 모델 학습
        
        Args:
            features: 학습 데이터 특성 리스트
            labels: 학습 데이터 태그 문자열 리스트 ('|'로 구분)
        """
        if not features or not labels or len(features) != len(labels):
            raise ValueError("특성과 레이블의 수가 일치하지 않거나 비어 있습니다.")
        
        # 태그 문자열을 태그 목록으로 변환
        tag_sets = [self._preprocess_tags(tag_str) for tag_str in labels]
        
        # 다중 레이블 이진화
        y = self.mlb.fit_transform(tag_sets)
        
        # 전처리된 특성 생성
        X = np.array([self._preprocess_features(f) for f in features])
        
        # 특성 이름 기록 (첫 번째 샘플만 사용)
        if features and 'text' in features[0] and 'text_feature_names' in features[0]['text']:
            text_feature_names = features[0]['text']['text_feature_names']
            structural_feature_count = X.shape[1] - len(text_feature_names)
            structural_feature_names = [f'structural_{i}' for i in range(structural_feature_count)]
            self.feature_names_ = text_feature_names + structural_feature_names
        
        # 모델 학습
        self.model.fit(X, y)
        
        self.is_fitted = True
    
    def predict(self, features: Dict[str, Any], category: str = None) -> str:
        """
        태그 예측
        
        Args:
            features: 예측할 데이터의 특성
            category: 제품 카테고리 (제공된 경우 카테고리에 맞는 태그 필터링)
            
        Returns:
            예측된 태그 문자열 ('|'로 구분)
        """
        if not self.is_fitted:
            raise ValueError("모델이 학습되지 않았습니다.")
        
        # 특성 전처리
        X = self._preprocess_features(features).reshape(1, -1)
        
        # 이진 예측 수행
        y_pred_binary = self.model.predict(X)[0]
        
        # 이진 예측을 태그 목록으로 변환
        predicted_tags = self.mlb.inverse_transform(y_pred_binary.reshape(1, -1))[0]
        
        # 카테고리가 제공된 경우 해당 카테고리에 적합한 태그만 필터링
        if category and category in self.category_tags_mapping:
            valid_tags = self.category_tags_mapping[category]
            if valid_tags:
                # 소분류 태그 필터링
                # 첫 번째 태그는 소분류여야 함
                filtered_tags = []
                
                # 소분류 태그 중 예측된 태그가 있는지 확인
                has_subcategory = False
                for tag in predicted_tags:
                    if tag in valid_tags:
                        filtered_tags.append(tag)
                        has_subcategory = True
                        break
                
                # 소분류 태그가 없는 경우 기본값 추가
                if not has_subcategory and valid_tags:
                    # 기본적으로 첫 번째 소분류 사용
                    filtered_tags.append(valid_tags[0])
                
                # 나머지 태그 추가 (소분류가 아닌 태그)
                for tag in predicted_tags:
                    if tag not in valid_tags:
                        filtered_tags.append(tag)
                
                predicted_tags = filtered_tags
        
        # 태그 목록을 문자열로 변환
        return '|'.join(predicted_tags)
    
    def predict_proba(self, features: Dict[str, Any]) -> Dict[str, float]:
        """
        태그 예측 확률 계산 (다중 레이블이라 단순화된 확률만 제공)
        
        Args:
            features: 예측할 데이터의 특성
            
        Returns:
            각 태그별 예측 확률
        """
        if not self.is_fitted:
            raise ValueError("모델이 학습되지 않았습니다.")
        
        # 특성 전처리
        X = self._preprocess_features(features).reshape(1, -1)
        
        # 확률 예측 (다중 레이블이라 각 클래스에 대한 확률을 개별적으로 계산)
        y_proba = []
        for estimator in self.model.estimators_:
            y_proba.append(estimator.predict_proba(X)[0, 1])  # 양성 클래스 확률만 추출
        
        # 태그-확률 매핑
        result = {tag: float(prob) for tag, prob in zip(self.mlb.classes_, y_proba)}
        
        return result
    
    def build_tag_from_category(self, category: str, subtags: List[str] = None, options: List[str] = None) -> str:
        """
        카테고리에 맞는 태그 문자열 생성
        
        Args:
            category: 제품 카테고리
            subtags: 소분류 태그 목록 (선택적)
            options: 옵션 태그 목록 (선택적)
            
        Returns:
            생성된 태그 문자열
        """
        if category not in self.category_tags_mapping:
            return ""
        
        tags = []
        
        # 소분류 추가
        valid_subtags = self.category_tags_mapping[category]
        if subtags:
            # 제공된 소분류 중 유효한 것만 추가
            for subtag in subtags:
                if subtag in valid_subtags:
                    tags.append(subtag)
                    break
        
        # 소분류가 없으면 기본값 추가 (필요한 경우)
        if not tags and valid_subtags:
            tags.append(valid_subtags[0])
        
        # 옵션 추가
        if options:
            tags.extend(options)
        
        return '|'.join(tags)
    
    def _get_save_metadata(self) -> Dict[str, Any]:
        """
        저장 시 추가 메타데이터 수집
        
        Returns:
            저장할 추가 메타데이터
        """
        return {
            'feature_names_': self.feature_names_,
            'mlb_classes_': self.mlb.classes_.tolist() if hasattr(self.mlb, 'classes_') else [],
            'category_tags_mapping': self.category_tags_mapping
        }
    
    def _set_load_metadata(self, metadata: Dict[str, Any]):
        """
        로드 시 추가 메타데이터 설정
        
        Args:
            metadata: 로드된 추가 메타데이터
        """
        self.feature_names_ = metadata.get('feature_names_', [])
        self.category_tags_mapping = metadata.get('category_tags_mapping', self._initialize_category_tags_mapping())
        
        # MLBinarizer 클래스 복원
        if 'mlb_classes_' in metadata and metadata['mlb_classes_']:
            self.mlb.classes_ = np.array(metadata['mlb_classes_'])
