"""
텍스트 데이터 특성 추출기 구현
"""
import re
import pickle
import numpy as np
from typing import Dict, Any, List, Union
from sklearn.feature_extraction.text import TfidfVectorizer

from app.ml.extractors.base import BaseExtractor


class TextExtractor(BaseExtractor):
    """
    텍스트 데이터에서 특성 추출
    
    제품명(sale_name) 등의 텍스트 데이터를 벡터화하여 특성으로 변환
    """
    
    def _initialize(self):
        """
        텍스트 추출기 초기화
        """
        self.vectorizer = TfidfVectorizer(
            max_features=self.config.get('max_features', 1000),
            ngram_range=self.config.get('ngram_range', (1, 2)),
            min_df=self.config.get('min_df', 2),
            max_df=self.config.get('max_df', 0.95),
            sublinear_tf=self.config.get('sublinear_tf', True)
        )
        self.is_fitted = False
    
    def _preprocess_text(self, text: str) -> str:
        """
        텍스트 전처리
        
        Args:
            text: 원본 텍스트
        
        Returns:
            전처리된 텍스트
        """
        if not text:
            return ""
        
        # 소문자 변환
        text = text.lower()
        
        # 특수문자 처리 (옵션)
        if self.config.get('remove_special_chars', False):
            text = re.sub(r'[^\w\s]', ' ', text)
        
        # 숫자 처리 (옵션)
        if self.config.get('remove_numbers', False):
            text = re.sub(r'\d+', ' ', text)
        
        # 여러 공백 처리
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        데이터에서 텍스트 특성 추출
        
        Args:
            data: 제품 데이터
        
        Returns:
            텍스트 특성 벡터
        """
        if not self.is_fitted:
            raise ValueError("텍스트 추출기가 학습되지 않았습니다. fit() 메서드를 먼저 호출하세요.")
        
        # 텍스트 필드 추출
        sale_name = data.get('sale_name', '')
        
        # 텍스트 전처리
        processed_text = self._preprocess_text(sale_name)
        
        # 벡터화
        if processed_text:
            text_vector = self.vectorizer.transform([processed_text])
            # 희소 행렬을 일반 배열로 변환
            text_features = text_vector.toarray()[0]
        else:
            # 빈 텍스트인 경우 0 벡터 반환
            text_features = np.zeros(len(self.vectorizer.get_feature_names_out()))
        
        return {
            'text_features': text_features,
            'text_feature_names': self.vectorizer.get_feature_names_out().tolist()
        }
    
    def fit(self, data: List[Dict[str, Any]]):
        """
        텍스트 데이터를 기반으로 벡터라이저 학습
        
        Args:
            data: 학습에 사용할 제품 데이터 리스트
        """
        # 텍스트 추출 및 전처리
        texts = []
        for item in data:
            sale_name = item.get('sale_name', '')
            processed_text = self._preprocess_text(sale_name)
            if processed_text:  # 빈 문자열이 아닌 경우만 추가
                texts.append(processed_text)
        
        if not texts:
            raise ValueError("학습할 텍스트 데이터가 없습니다.")
        
        # 벡터라이저 학습
        self.vectorizer.fit(texts)
        self.is_fitted = True
    
    def save(self, path: str):
        """
        텍스트 추출기 상태 저장
        
        Args:
            path: 저장 경로
        """
        state = {
            'vectorizer': self.vectorizer,
            'is_fitted': self.is_fitted,
            'config': self.config
        }
        with open(path, 'wb') as f:
            pickle.dump(state, f)
    
    def load(self, path: str):
        """
        텍스트 추출기 상태 로드
        
        Args:
            path: 로드할 파일 경로
        """
        with open(path, 'rb') as f:
            state = pickle.load(f)
        
        self.vectorizer = state['vectorizer']
        self.is_fitted = state['is_fitted']
        self.config = state['config']
