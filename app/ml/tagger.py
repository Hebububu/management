"""
자동 태깅 시스템 구현
"""
import os
import logging
from typing import Dict, Any, List, Union, Optional
from datetime import datetime

from app.ml.extractors.combined import CombinedExtractor
from app.ml.models.company import CompanyModel
from app.ml.models.category import CategoryModel
from app.ml.models.tags import TagsModel
from app.ml.feedback import FeedbackSystem

# 로깅 설정
logger = logging.getLogger(__name__)


class AutoTaggingSystem:
    """
    자동 태깅 시스템
    
    특성 추출기와 분류 모델을 통합하여 제품 태깅을 자동화하는 시스템
    """
    
    def __init__(self, config: Dict[str, Any] = None, db_connection=None):
        """
        자동 태깅 시스템 초기화
        
        Args:
            config: 설정 파라미터를 담은 딕셔너리
            db_connection: 데이터베이스 연결 객체
        """
        self.config = config or {}
        self.db = db_connection
        
        # 특성 추출기 초기화
        extractor_config = self.config.get('extractor', {})
        self.extractor = CombinedExtractor(extractor_config)
        
        # 분류 모델 초기화
        self.models = {
            'company': CompanyModel(self.config.get('company_model', {})),
            'category': CategoryModel(self.config.get('category_model', {})),
            'tags': TagsModel(self.config.get('tags_model', {}))
        }
        
        # 피드백 시스템 초기화
        self.feedback_system = FeedbackSystem(self.db)
        
        # 모델 로드 또는 초기 학습
        self._initialize_models()
    
    def tag_product(self, product_id: int) -> Dict[str, Any]:
        """
        제품 자동 태깅
        
        Args:
            product_id: 태깅할 제품 ID
            
        Returns:
            태깅 결과
        """
        # 제품 정보 조회
        product = self._get_product(product_id)
        if not product:
            return {"error": "Product not found"}
        
        try:
            # 특성 추출
            features = self.extractor.extract(product)
            
            # 각 모델별 예측 수행
            predictions = {
                "company": self.models['company'].predict(features),
                "category": self.models['category'].predict(features),
                "tags": ""  # 태그는 카테고리 예측 이후에 예측
            }
            
            # 카테고리 예측을 기반으로 태그 예측
            category = predictions["category"]
            predictions["tags"] = self.models['tags'].predict(features, category)
            
            # 예측 신뢰도 계산
            confidence = self._get_confidence_scores(features, predictions)
            
            # 결과 반환
            result = {
                "product_id": product_id,
                "predictions": predictions,
                "confidence_scores": confidence
            }
            
            return result
        except Exception as e:
            logger.error(f"제품 {product_id} 태깅 중 오류 발생: {str(e)}")
            return {"error": f"Processing error: {str(e)}"}
    
    def process_feedback(self, product_id: int, corrected_tags: Dict[str, str], user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        사용자 피드백 처리
        
        Args:
            product_id: 제품 ID
            corrected_tags: 사용자가 수정한 태그
            user_id: 피드백을 제공한 사용자 ID (선택적)
            
        Returns:
            처리 결과
        """
        try:
            # 제품 정보 조회
            product = self._get_product(product_id)
            if not product:
                return {"error": "Product not found"}
            
            # 원본 예측 태그 가져오기
            features = self.extractor.extract(product)
            original_predictions = {
                "company": self.models['company'].predict(features),
                "category": self.models['category'].predict(features)
            }
            # 카테고리 예측을 기반으로 태그 예측
            original_predictions["tags"] = self.models['tags'].predict(features, original_predictions["category"])
            
            # 피드백 기록
            feedback_recorded = self.feedback_system.record_feedback(
                product_id, 
                original_predictions, 
                corrected_tags, 
                user_id
            )
            
            if not feedback_recorded:
                return {"status": "error", "message": "Failed to record feedback"}
            
            # 필요 시 모델 업데이트
            self._update_model_if_needed()
            
            return {"status": "success", "message": "Feedback recorded successfully"}
        except Exception as e:
            logger.error(f"피드백 처리 중 오류 발생: {str(e)}")
            return {"status": "error", "message": f"Error processing feedback: {str(e)}"}
    
    def batch_tag_products(self, limit: int = 100) -> Dict[str, Any]:
        """
        다수의 제품 배치 태깅
        
        Args:
            limit: 처리할 최대 제품 수
            
        Returns:
            배치 처리 결과
        """
        if not self.db:
            return {"error": "Database connection is required for batch processing"}
        
        try:
            # 태그가 없는 제품 조회
            untagged_products = self.db.get_untagged_products(limit=limit)
            
            if not untagged_products:
                return {"status": "info", "message": "No untagged products found"}
            
            # 처리 결과 추적
            results = {
                "total": len(untagged_products),
                "successful": 0,
                "failed": 0,
                "products": []
            }
            
            # 각 제품 처리
            for product in untagged_products:
                product_id = product.get("id")
                
                try:
                    # 태그 예측
                    tagging_result = self.tag_product(product_id)
                    
                    if "error" in tagging_result:
                        # 태깅 실패
                        results["failed"] += 1
                        results["products"].append({
                            "id": product_id,
                            "status": "failed",
                            "error": tagging_result["error"]
                        })
                        continue
                    
                    # 데이터베이스에 태그 적용
                    predictions = tagging_result["predictions"]
                    update_result = self.db.update_product_tags(
                        product_id,
                        company=predictions.get("company", ""),
                        category=predictions.get("category", ""),
                        tags=predictions.get("tags", "")
                    )
                    
                    if update_result:
                        results["successful"] += 1
                        results["products"].append({
                            "id": product_id,
                            "status": "success",
                            "tags": predictions
                        })
                    else:
                        results["failed"] += 1
                        results["products"].append({
                            "id": product_id,
                            "status": "failed",
                            "error": "Failed to update database"
                        })
                
                except Exception as e:
                    # 처리 중 오류
                    results["failed"] += 1
                    results["products"].append({
                        "id": product_id,
                        "status": "failed",
                        "error": str(e)
                    })
            
            return results
        
        except Exception as e:
            logger.error(f"배치 처리 중 오류 발생: {str(e)}")
            return {"error": f"Batch processing error: {str(e)}"}
    
    def _get_product(self, product_id: int) -> Dict[str, Any]:
        """
        제품 정보 조회 및 딕셔너리로 변환
        
        Args:
            product_id: 제품 ID
            
        Returns:
            제품 정보 딕셔너리
        """
        if not self.db:
            raise ValueError("데이터베이스 연결이 필요합니다.")
        
        # 제품 정보 조회
        product = self.db.get_product(product_id)
        
        if not product:
            return None
        
        # Product 객체를 딕셔너리로 변환
        return self._convert_product_to_dict(product)
    
    def _convert_product_to_dict(self, product) -> Dict[str, Any]:
        """
        Product 모델 객체를 딕셔너리로 변환
        
        Args:
            product: Product 모델 객체
            
        Returns:
            딕셔너리 형태의 제품 정보
        """
        # Product 객체의 속성에 직접 접근하여 딕셔너리 생성
        return {
            'id': product.id,
            'sale_name': product.sale_name,
            'platform': product.platform,
            'seller_id': product.seller_id,
            'category': product.category,
            'tags': product.tags,
            'company': product.company,
            'product_name': product.product_name,
            'data': product.data,
            'created_at': product.created_at,
            'updated_at': product.updated_at
        }
    
    def _initialize_models(self):
        """
        모델 초기화 (로드 또는 학습)
        """
        model_directory = self.config.get('model_directory', './models')
        extractor_directory = os.path.join(model_directory, 'extractors')
        
        try:
            # 특성 추출기 로드 시도
            self.extractor.load(extractor_directory)
            logger.info("특성 추출기를 성공적으로 로드했습니다.")
            
            # 각 모델 로드 시도
            for name, model in self.models.items():
                model_path = os.path.join(model_directory, f"{name}_model.pkl")
                model.load(model_path)
                logger.info(f"{name} 모델을 성공적으로 로드했습니다.")
            
            logger.info("모든 모델이 성공적으로 로드되었습니다.")
        
        except Exception as e:
            logger.warning(f"모델 로드 중 오류 발생: {str(e)}. 초기 학습을 시도합니다.")
            self._train_initial_models()
    
    def _train_initial_models(self):
        """
        초기 모델 학습
        """
        if not self.db:
            logger.error("데이터베이스 연결 없이 초기 모델을 학습할 수 없습니다.")
            raise ValueError("Database connection is required for initial training")
        
        # 태깅된 제품 데이터 가져오기
        tagged_products_limit = self.config.get('initial_training_limit', 200)
        initial_data = self.db.get_tagged_products(limit=tagged_products_limit)
        
        if not initial_data:
            logger.error("학습 데이터가 없어 초기 모델을 학습할 수 없습니다.")
            raise ValueError("No training data available for initial training")
        
        logger.info(f"총 {len(initial_data)}개의 데이터로 초기 모델을 학습합니다.")
        
        # 특성 추출기 학습
        self.extractor.fit(initial_data)
        
        # 각 모델 학습을 위한 특성 및 레이블 준비
        features = []
        labels = {
            'company': [],
            'category': [],
            'tags': []
        }
        
        for product in initial_data:
            # 특성 추출
            feature = self.extractor.extract(product)
            features.append(feature)
            
            # 레이블 추출
            labels['company'].append(product.get('company', ''))
            labels['category'].append(product.get('category', ''))
            labels['tags'].append(product.get('tags', ''))
        
        # 각 모델 학습
        for name, model in self.models.items():
            model.fit(features, labels[name])
            logger.info(f"{name} 모델 학습 완료")
        
        # 모델 저장
        self._save_models()
        
        logger.info("초기 모델 학습 및 저장 완료")
    
    def _update_model_if_needed(self):
        """
        필요시 모델 업데이트
        """
        # 마지막 업데이트 시간 확인
        last_update = self.config.get('last_model_update')
        
        # 마지막 업데이트 이후 수집된 피드백 수 확인
        feedback_data = self.feedback_system.get_feedback_data(since_timestamp=last_update)
        feedback_count = len(feedback_data)
        
        # 피드백 임계값 확인
        feedback_threshold = self.config.get('feedback_threshold', 20)
        
        if feedback_count >= feedback_threshold:
            logger.info(f"피드백 임계값({feedback_threshold})을 초과하여 모델을 재학습합니다.")
            self._retrain_models()
    
    def _retrain_models(self):
        """
        모델 재학습
        """
        if not self.db:
            logger.error("데이터베이스 연결 없이 모델을 재학습할 수 없습니다.")
            return
        
        try:
            # 기존 태깅 데이터 가져오기
            training_limit = self.config.get('retraining_limit', 500)
            training_data = self.db.get_tagged_products(limit=training_limit)
            
            if not training_data:
                logger.warning("재학습을 위한 태깅 데이터가 없습니다.")
                return
            
            # 피드백 데이터 가져오기
            feedback_data = self.feedback_system.get_feedback_data()
            
            # 피드백 데이터를 학습 데이터로 변환
            feedback_samples = self.feedback_system.update_training_data(feedback_data)
            
            # 학습 데이터 결합
            combined_data = training_data + feedback_samples
            
            logger.info(f"총 {len(combined_data)}개의 데이터로 모델을 재학습합니다.")
            
            # 특성 추출기 재학습
            self.extractor.fit(combined_data)
            
            # 각 모델 학습을 위한 특성 및 레이블 준비
            features = []
            labels = {
                'company': [],
                'category': [],
                'tags': []
            }
            
            for product in combined_data:
                # 특성 추출
                feature = self.extractor.extract(product)
                features.append(feature)
                
                # 레이블 추출
                labels['company'].append(product.get('company', ''))
                labels['category'].append(product.get('category', ''))
                labels['tags'].append(product.get('tags', ''))
            
            # 각 모델 재학습
            for name, model in self.models.items():
                model.fit(features, labels[name])
                logger.info(f"{name} 모델 재학습 완료")
            
            # 모델 저장
            self._save_models()
            
            # 마지막 업데이트 시간 기록
            self.config['last_model_update'] = datetime.now()
            
            logger.info("모델 재학습 및 저장 완료")
        
        except Exception as e:
            logger.error(f"모델 재학습 중 오류 발생: {str(e)}")
    
    def _save_models(self):
        """
        모델 저장
        """
        model_directory = self.config.get('model_directory', './models')
        os.makedirs(model_directory, exist_ok=True)
        
        # 특성 추출기 저장
        extractor_directory = os.path.join(model_directory, 'extractors')
        os.makedirs(extractor_directory, exist_ok=True)
        self.extractor.save(extractor_directory)
        
        # 각 모델 저장
        for name, model in self.models.items():
            model_path = os.path.join(model_directory, f"{name}_model.pkl")
            model.save(model_path)
    
    def _get_confidence_scores(self, features: Dict[str, Any], predictions: Dict[str, str]) -> Dict[str, float]:
        """
        예측 신뢰도 점수 계산
        
        Args:
            features: 특성 데이터
            predictions: 예측 결과
            
        Returns:
            각 예측의 신뢰도 점수
        """
        confidence = {}
        
        # 회사명 신뢰도
        company_probs = self.models['company'].predict_proba(features)
        predicted_company = predictions.get('company', '')
        confidence['company'] = company_probs.get(predicted_company, 0.0)
        
        # 카테고리 신뢰도
        category_probs = self.models['category'].predict_proba(features)
        predicted_category = predictions.get('category', '')
        confidence['category'] = category_probs.get(predicted_category, 0.0)
        
        # 태그 신뢰도 (첫 번째 태그의 신뢰도 사용)
        tags_probs = self.models['tags'].predict_proba(features)
        predicted_tags = predictions.get('tags', '')
        if predicted_tags:
            first_tag = predicted_tags.split('|')[0] if '|' in predicted_tags else predicted_tags
            confidence['tags'] = tags_probs.get(first_tag, 0.0)
        else:
            confidence['tags'] = 0.0
        
        # 전체 신뢰도 (가중 평균)
        weights = {
            'company': 0.3,
            'category': 0.4, 
            'tags': 0.3
        }
        
        overall_score = sum(confidence[key] * weights[key] for key in confidence) / sum(weights.values())
        confidence['overall'] = overall_score
        
        return confidence
