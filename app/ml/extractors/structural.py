"""
구조적 데이터 특성 추출기 구현
"""
import pickle
import numpy as np
from typing import Dict, Any, List, Union

from app.ml.extractors.base import BaseExtractor


class StructuralExtractor(BaseExtractor):
    """
    구조적 데이터에서 특성 추출
    
    플랫폼별 json 구조, 카테고리 등의 구조적 데이터를 특성으로 변환
    """
    
    def _initialize(self):
        """
        구조적 데이터 추출기 초기화
        """
        self.platform_mapping = {}  # 플랫폼 -> 인덱스 매핑
        self.is_fitted = False
    
    def _encode_platform(self, platform: str) -> List[int]:
        """
        플랫폼을 원-핫 인코딩 벡터로 변환
        
        Args:
            platform: 플랫폼 이름
        
        Returns:
            원-핫 인코딩 벡터
        """
        if not self.is_fitted:
            raise ValueError("구조적 추출기가 학습되지 않았습니다. fit() 메서드를 먼저 호출하세요.")
        
        # 알 수 없는 플랫폼인 경우 0 벡터 반환
        if platform not in self.platform_mapping:
            return [0] * len(self.platform_mapping)
        
        # 원-핫 인코딩 벡터 생성
        vector = [0] * len(self.platform_mapping)
        vector[self.platform_mapping[platform]] = 1
        
        return vector
    
    def _extract_naver_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        네이버 커머스 특성 추출
        
        Args:
            data: 네이버 커머스 제품 데이터
        
        Returns:
            추출된 특성
        """
        features = {}
        
        # 채널 제품 정보 추출
        if 'channelProducts' in data and isinstance(data['channelProducts'], list) and data['channelProducts']:
            channel_product = data['channelProducts'][0]
            
            # 제조사명
            features['has_manufacturer'] = 1 if channel_product.get('manufacturerName') else 0
            
            # 브랜드명
            features['has_brand'] = 1 if channel_product.get('brandName') else 0
            
            # 카테고리 정보
            features['has_category'] = 1 if channel_product.get('categoryId') else 0
            
            # 셀러 태그
            seller_tags = channel_product.get('sellerTags', [])
            features['seller_tag_count'] = len(seller_tags)
        else:
            features['has_manufacturer'] = 0
            features['has_brand'] = 0
            features['has_category'] = 0
            features['seller_tag_count'] = 0
        
        return features
    
    def _extract_cafe24_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        카페24 특성 추출
        
        Args:
            data: 카페24 제품 데이터
        
        Returns:
            추출된 특성
        """
        features = {}
        
        # 제품 태그 정보
        features['product_tag_count'] = len(data.get('product_tag', []))
        
        # 옵션 정보
        options = data.get('options', {})
        if options and isinstance(options, dict):
            features['has_options'] = 1 if options.get('has_option') == 'T' else 0
            
            # 옵션 유형 및 개수
            option_list = options.get('options', [])
            features['option_count'] = len(option_list)
            
            # 옵션 값 개수 (첫 번째 옵션만 사용)
            if option_list and len(option_list) > 0:
                option_values = option_list[0].get('option_value', [])
                features['option_value_count'] = len(option_values)
            else:
                features['option_value_count'] = 0
        else:
            features['has_options'] = 0
            features['option_count'] = 0
            features['option_value_count'] = 0
        
        return features
    
    def extract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        데이터에서 구조적 특성 추출
        
        Args:
            data: 제품 데이터
        
        Returns:
            구조적 특성 벡터
        """
        if not self.is_fitted:
            raise ValueError("구조적 추출기가 학습되지 않았습니다. fit() 메서드를 먼저 호출하세요.")
        
        features = {}
        
        # 플랫폼 특성
        platform = data.get('platform', '')
        features['platform_vector'] = self._encode_platform(platform)
        
        # 플랫폼별 특수 특성
        if platform == 'naverCommerce':
            platform_features = self._extract_naver_features(data.get('data', {}))
        elif platform == 'cafe24':
            platform_features = self._extract_cafe24_features(data.get('data', {}))
        else:
            platform_features = {}
        
        features.update(platform_features)
        
        return features
    
    def fit(self, data: List[Dict[str, Any]]):
        """
        구조적 데이터를 기반으로 추출기 학습
        
        Args:
            data: 학습에 사용할 제품 데이터 리스트
        """
        # 고유 플랫폼 추출
        platforms = set()
        for item in data:
            platform = item.get('platform', '')
            if platform:
                platforms.add(platform)
        
        # 플랫폼 인덱스 매핑 생성
        self.platform_mapping = {platform: idx for idx, platform in enumerate(sorted(platforms))}
        
        self.is_fitted = True
    
    def save(self, path: str):
        """
        구조적 데이터 추출기 상태 저장
        
        Args:
            path: 저장 경로
        """
        state = {
            'platform_mapping': self.platform_mapping,
            'is_fitted': self.is_fitted,
            'config': self.config
        }
        with open(path, 'wb') as f:
            pickle.dump(state, f)
    
    def load(self, path: str):
        """
        구조적 데이터 추출기 상태 로드
        
        Args:
            path: 로드할 파일 경로
        """
        with open(path, 'rb') as f:
            state = pickle.load(f)
        
        self.platform_mapping = state['platform_mapping']
        self.is_fitted = state['is_fitted']
        self.config = state['config']
