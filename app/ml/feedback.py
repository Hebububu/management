"""
사용자 피드백 시스템
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Union, Optional

# 로깅 설정
logger = logging.getLogger(__name__)


class FeedbackSystem:
    """
    사용자 피드백 시스템
    
    사용자 피드백을 수집하고 학습 데이터로 변환하는 기능 제공
    """
    
    def __init__(self, db_connection=None):
        """
        피드백 시스템 초기화
        
        Args:
            db_connection: 데이터베이스 연결 객체
        """
        self.db = db_connection
    
    def record_feedback(self, product_id: int, original_tags: Dict[str, Any], 
                        corrected_tags: Dict[str, Any], user_id: Optional[str] = None) -> bool:
        """
        사용자 피드백 기록
        
        Args:
            product_id: 제품 ID
            original_tags: 원본 예측 태그
            corrected_tags: 사용자가 수정한 태그
            user_id: 피드백을 제공한 사용자 ID (선택적)
            
        Returns:
            피드백 기록 성공 여부
        """
        # 피드백 데이터 구성
        feedback_data = {
            'product_id': product_id,
            'original_tags': original_tags,
            'corrected_tags': corrected_tags,
            'user_id': user_id,
            'timestamp': datetime.now()
        }
        
        try:
            # 데이터베이스에 피드백 저장
            if self.db:
                self.db.save_feedback(feedback_data)
                logger.info(f"제품 {product_id}에 대한 피드백이 성공적으로 기록되었습니다.")
            else:
                logger.warning("데이터베이스 연결이 없어 피드백을 기록할 수 없습니다.")
                return False
                
            return True
        except Exception as e:
            logger.error(f"피드백 기록 중 오류 발생: {str(e)}")
            return False
    
    def get_feedback_data(self, since_timestamp: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        수집된 피드백 데이터 조회
        
        Args:
            since_timestamp: 이 시간 이후의 피드백만 조회 (선택적)
            
        Returns:
            피드백 데이터 목록
        """
        try:
            if not self.db:
                logger.warning("데이터베이스 연결이 없어 피드백을 조회할 수 없습니다.")
                return []
            
            # 쿼리 조건 구성
            query = {}
            if since_timestamp:
                query['timestamp'] = {'$gt': since_timestamp}
            
            # 데이터베이스에서 피드백 조회
            feedback_data = self.db.get_feedback(query)
            logger.info(f"총 {len(feedback_data)}개의 피드백 데이터를 조회했습니다.")
            
            return feedback_data
        except Exception as e:
            logger.error(f"피드백 조회 중 오류 발생: {str(e)}")
            return []
    
    def update_training_data(self, feedback_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        피드백을 학습 데이터로 변환
        
        Args:
            feedback_data: 피드백 데이터 목록
            
        Returns:
            학습용 데이터 목록
        """
        if not self.db:
            logger.warning("데이터베이스 연결이 없어 학습 데이터를 생성할 수 없습니다.")
            return []
        
        training_samples = []
        
        for feedback in feedback_data:
            try:
                # 제품 정보 조회
                product_id = feedback.get('product_id')
                if not product_id:
                    continue
                
                product = self.db.get_product(product_id)
                if not product:
                    logger.warning(f"제품 ID {product_id}에 대한 정보를 찾을 수 없습니다.")
                    continue
                
                # 수정된 태그 정보 추출
                corrected_tags = feedback.get('corrected_tags', {})
                if not corrected_tags:
                    continue
                
                # 학습 샘플 생성
                sample = {
                    'sale_name': product.get('sale_name', ''),
                    'data': product.get('data', {}),
                    'platform': product.get('platform', ''),
                    'company': corrected_tags.get('company', ''),
                    'category': corrected_tags.get('category', ''),
                    'tags': corrected_tags.get('tags', '')
                }
                
                # 필수 필드 검증
                if not sample['sale_name'] or not any([sample['company'], sample['category'], sample['tags']]):
                    continue
                
                training_samples.append(sample)
            except Exception as e:
                logger.error(f"피드백 처리 중 오류 발생: {str(e)}")
                continue
        
        logger.info(f"총 {len(training_samples)}개의 학습 샘플을 생성했습니다.")
        return training_samples
