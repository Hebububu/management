"""
기본 분류 모델 인터페이스 정의
"""
import os
import pickle
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union

import numpy as np


class BaseModel(ABC):
    """
    모든 분류 모델의 기본 인터페이스
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        모델 초기화
        
        Args:
            config: 설정 파라미터를 담은 딕셔너리
        """
        self.config = config or {}
        self.model = None
        self.is_fitted = False
        self._initialize()
    
    @abstractmethod
    def _initialize(self):
        """
        모델 내부 초기화 로직
        """
        pass
    
    @abstractmethod
    def _preprocess_features(self, features: Dict[str, Any]) -> np.ndarray:
        """
        특성 전처리
        
        Args:
            features: 추출기에서 제공한 특성
            
        Returns:
            모델 입력용 처리된 특성 벡터
        """
        pass
    
    @abstractmethod
    def fit(self, features: List[Dict[str, Any]], labels: List[str]):
        """
        모델 학습
        
        Args:
            features: 학습 데이터 특성 리스트
            labels: 학습 데이터 레이블 리스트
        """
        pass
    
    @abstractmethod
    def predict(self, features: Dict[str, Any]) -> str:
        """
        예측 수행
        
        Args:
            features: 예측할 데이터의 특성
            
        Returns:
            예측 결과
        """
        pass
    
    @abstractmethod
    def predict_proba(self, features: Dict[str, Any]) -> Dict[str, float]:
        """
        예측 확률 계산
        
        Args:
            features: 예측할 데이터의 특성
            
        Returns:
            각 클래스별 예측 확률
        """
        pass
    
    def save(self, path: str):
        """
        모델 저장
        
        Args:
            path: 저장 경로
        """
        if not self.is_fitted:
            raise ValueError("학습되지 않은 모델을 저장할 수 없습니다.")
        
        # 디렉토리 생성
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        state = {
            'model': self.model,
            'config': self.config,
            'is_fitted': self.is_fitted,
            'metadata': self._get_save_metadata()  # 추가 메타데이터
        }
        
        with open(path, 'wb') as f:
            pickle.dump(state, f)
    
    def load(self, path: str):
        """
        모델 로드
        
        Args:
            path: 로드할 파일 경로
        """
        with open(path, 'rb') as f:
            state = pickle.load(f)
        
        self.model = state['model']
        self.config = state['config']
        self.is_fitted = state['is_fitted']
        self._set_load_metadata(state.get('metadata', {}))  # 추가 메타데이터 설정
    
    def _get_save_metadata(self) -> Dict[str, Any]:
        """
        저장 시 추가 메타데이터 수집
        
        Returns:
            저장할 추가 메타데이터
        """
        return {}
    
    def _set_load_metadata(self, metadata: Dict[str, Any]):
        """
        로드 시 추가 메타데이터 설정
        
        Args:
            metadata: 로드된 추가 메타데이터
        """
        pass
