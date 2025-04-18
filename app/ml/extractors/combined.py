"""
통합 특성 추출기
"""
import os
import pickle
import numpy as np
from typing import Dict, Any, List, Union

from app.ml.extractors.base import BaseExtractor
from app.ml.extractors.text import TextExtractor
from app.ml.extractors.structural import StructuralExtractor


class CombinedExtractor(BaseExtractor):
    """
    텍스트 및 구조적 특성을 결합한 통합 추출기
    """
    
    def _initialize(self):
        """
        통합 추출기 초기화
        """
        # 텍스트 추출기 초기화
        text_config = self.config.get('text', {})
        self.text_extractor = TextExtractor(text_config)
        
        # 구조적 데이터 추출기 초기화
        structural_config = self.config.get('structural', {})
        self.structural_extractor = StructuralExtractor(structural_config)
        
        self.is_fitted = False
    
    def extract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        데이터에서 통합 특성 추출
        
        Args:
            data: 제품 데이터
        
        Returns:
            텍스트 및 구조적 특성이 결합된 벡터
        """
        if not self.is_fitted:
            raise ValueError("통합 추출기가 학습되지 않았습니다. fit() 메서드를 먼저 호출하세요.")
        
        # 텍스트 특성 추출
        text_features = self.text_extractor.extract(data)
        
        # 구조적 특성 추출
        structural_features = self.structural_extractor.extract(data)
        
        # 모든 특성 결합
        combined_features = {
            'text': text_features,
            'structural': structural_features
        }
        
        return combined_features
    
    def fit(self, data: List[Dict[str, Any]]):
        """
        데이터를 기반으로 모든 추출기 학습
        
        Args:
            data: 학습에 사용할 제품 데이터 리스트
        """
        # 텍스트 추출기 학습
        self.text_extractor.fit(data)
        
        # 구조적 추출기 학습
        self.structural_extractor.fit(data)
        
        self.is_fitted = True
    
    def save(self, path: str):
        """
        통합 추출기 상태 저장
        
        Args:
            path: 저장 디렉토리 경로
        """
        # 디렉토리 생성
        os.makedirs(path, exist_ok=True)
        
        # 텍스트 추출기 저장
        text_path = os.path.join(path, 'text_extractor.pkl')
        self.text_extractor.save(text_path)
        
        # 구조적 추출기 저장
        structural_path = os.path.join(path, 'structural_extractor.pkl')
        self.structural_extractor.save(structural_path)
        
        # 통합 추출기 메타데이터 저장
        meta_path = os.path.join(path, 'combined_extractor_meta.pkl')
        meta = {
            'is_fitted': self.is_fitted,
            'config': self.config
        }
        with open(meta_path, 'wb') as f:
            pickle.dump(meta, f)
    
    def load(self, path: str):
        """
        통합 추출기 상태 로드
        
        Args:
            path: 로드할 디렉토리 경로
        """
        # 텍스트 추출기 로드
        text_path = os.path.join(path, 'text_extractor.pkl')
        self.text_extractor.load(text_path)
        
        # 구조적 추출기 로드
        structural_path = os.path.join(path, 'structural_extractor.pkl')
        self.structural_extractor.load(structural_path)
        
        # 통합 추출기 메타데이터 로드
        meta_path = os.path.join(path, 'combined_extractor_meta.pkl')
        with open(meta_path, 'rb') as f:
            meta = pickle.load(f)
        
        self.is_fitted = meta['is_fitted']
        self.config = meta['config']
