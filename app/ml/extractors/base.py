"""
기본 특성 추출기 인터페이스 정의
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union


class BaseExtractor(ABC):
    """
    특성 추출기의 기본 인터페이스
    모든 특성 추출기는 이 클래스를 상속받아야 함
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        특성 추출기 초기화
        
        Args:
            config: 설정 파라미터를 담은 딕셔너리
        """
        self.config = config or {}
        self._initialize()
    
    @abstractmethod
    def _initialize(self):
        """
        추출기 내부 초기화 로직
        """
        pass
    
    @abstractmethod
    def extract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        데이터에서 특성 추출
        
        Args:
            data: 특성을 추출할 데이터
            
        Returns:
            추출된 특성을 포함하는 딕셔너리
        """
        pass
    
    @abstractmethod
    def fit(self, data: List[Dict[str, Any]]):
        """
        데이터를 기반으로 추출기 학습(필요한 경우)
        
        Args:
            data: 학습에 사용할 데이터 리스트
        """
        pass
    
    @abstractmethod
    def save(self, path: str):
        """
        추출기 상태 저장
        
        Args:
            path: 저장 경로
        """
        pass
    
    @abstractmethod
    def load(self, path: str):
        """
        추출기 상태 로드
        
        Args:
            path: 로드할 파일 경로
        """
        pass
