from sqlalchemy import and_, or_, func
from sqlalchemy.exc import SQLAlchemyError
from app.database.databasesetup import DatabaseSetup
from app.database.models import Product
from app.utils.logger import mainLogger
import datetime

# 로거 정의
logger = mainLogger()

class ProductCRUD:
    """
    제품 데이터 CRUD 작업을 처리하는 클래스입니다.
    """
    
    def __init__(self):
        self.db = DatabaseSetup()
        
    def create_product(self, product_data):
        """
        새 제품을 데이터베이스에 추가합니다.
        
        Args:
            product_data (dict): 제품 데이터 객체
            
        Returns:
            Product: 생성된 제품 모델 객체
        """
        session = self.db.get_session()
        try:
            # 현재 시간
            current_time = datetime.datetime.utcnow()
            
            # 생성/업데이트 시간이 없으면 현재 시간 설정
            if 'created_at' not in product_data:
                product_data['created_at'] = current_time
            if 'updated_at' not in product_data:
                product_data['updated_at'] = current_time
            
            # 새 제품 모델 생성
            new_product = Product(**product_data)
            
            # 데이터베이스에 추가
            session.add(new_product)
            session.commit()
            
            logger.info(f"새 제품 등록: {new_product.sale_name}")
            return new_product
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"제품 생성 중 오류 발생: {e}")
            raise e
        finally:
            session.close()
    
    def get_product(self, product_id):
        """
        제품 ID로 제품을 조회합니다.
        
        Args:
            product_id (int): 조회할 제품 ID
            
        Returns:
            Product: 조회된 제품 모델 객체
        """
        session = self.db.get_session()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            return product
        except SQLAlchemyError as e:
            logger.error(f"제품 조회 중 오류 발생: {e}")
            return None
        finally:
            session.close()
    
    def update_product_tags(self, product_id, category, tags, company, product_name):
        """
        제품의 태그, 카테고리, 제조사, 제품명 정보를 업데이트합니다.
        
        Args:
            product_id (int): 업데이트할 제품 ID
            category (str): 제품 카테고리
            tags (str): 제품 태그 정보
            company (str): 제조사 이름
            product_name (str): 관리제품명
            
        Returns:
            bool: 업데이트 성공 여부
        """
        session = self.db.get_session()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            
            if not product:
                logger.warning(f"제품 ID {product_id} 찾을 수 없음")
                return False
            
            # 데이터 업데이트
            product.category = category
            product.tags = tags
            product.company = company
            product.product_name = product_name
            product.updated_at = datetime.datetime.utcnow()
            
            session.commit()
            logger.info(f"제품 ID {product_id} 태그 업데이트됨")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"제품 태그 업데이트 중 오류 발생: {e}")
            return False
        finally:
            session.close()
    
    def get_unfulfilled_products(self, seller_id=None):
        """
        태그가 미입력된 제품 목록을 반환합니다.
        
        Args:
            seller_id (str, optional): 판매자 ID로 필터링. 기본값은 None (모든 판매자).
            
        Returns:
            list: 미완성 제품 목록
        """
        session = self.db.get_session()
        try:
            # 미완성 제품 조건
            query = session.query(Product).filter(
                or_(
                    Product.tags == None,
                    Product.category == None,
                    Product.product_name == None,
                    Product.company == None
                )
            )
            
            # 판매자 ID로 필터링
            if seller_id:
                query = query.filter(Product.seller_id == seller_id)
            
            # 결과 정렬 (최근 추가된 순)
            products = query.order_by(Product.created_at.desc()).all()
            return products
            
        except SQLAlchemyError as e:
            logger.error(f"미완성 제품 조회 중 오류 발생: {e}")
            return []
        finally:
            session.close()
    
    def get_next_unfulfilled_product(self, seller_id=None):
        """
        태그가 미입력된 다음 제품을 반환합니다.
        
        Args:
            seller_id (str, optional): 판매자 ID로 필터링. 기본값은 None (모든 판매자).
            
        Returns:
            Product: 다음 미완성 제품
        """
        session = self.db.get_session()
        try:
            # 미완성 제품 조건
            query = session.query(Product).filter(
                or_(
                    Product.tags == None,
                    Product.category == None,
                    Product.product_name == None,
                    Product.company == None
                )
            )
            
            # 판매자 ID로 필터링
            if seller_id:
                query = query.filter(Product.seller_id == seller_id)
            
            # 결과 정렬 (최근 추가된 순) 및 첫 번째 제품 반환
            product = query.order_by(Product.created_at.desc()).first()
            return product
            
        except SQLAlchemyError as e:
            logger.error(f"다음 미완성 제품 조회 중 오류 발생: {e}")
            return None
        finally:
            session.close()
    
    def search_products(self, search_term):
        """
        제품을 검색합니다.
        
        Args:
            search_term (str): 검색어
            
        Returns:
            list: 검색된 제품 목록
        """
        session = self.db.get_session()
        try:
            # 검색 조건
            search_pattern = f"%{search_term}%"
            products = session.query(Product).filter(
                or_(
                    Product.sale_name.ilike(search_pattern),
                    Product.product_name.ilike(search_pattern),
                    Product.company.ilike(search_pattern),
                    Product.tags.ilike(search_pattern),
                    Product.category.ilike(search_pattern)
                )
            ).order_by(Product.updated_at.desc()).all()
            
            return products
            
        except SQLAlchemyError as e:
            logger.error(f"제품 검색 중 오류 발생: {e}")
            return []
        finally:
            session.close()

    def get_category_stats(self, seller_id=None):
        """
        카테고리별 제품 통계를 반환합니다.
        
        Args:
            seller_id (str, optional): 판매자 ID로 필터링. 기본값은 None (모든 판매자).
            
        Returns:
            dict: 카테고리별 제품 수
        """
        session = self.db.get_session()
        try:
            # 기본 쿼리
            query = session.query(
                func.coalesce(Product.category, "미분류").label("category"), 
                func.count(Product.id).label("count")
            )
            
            # 판매자 ID로 필터링
            if seller_id:
                query = query.filter(Product.seller_id == seller_id)
            
            # 그룹화 및 결과 조회
            results = query.group_by("category").all()
            
            # 딕셔너리로 변환
            stats = {}
            for category, count in results:
                stats[category] = count
            
            return stats
            
        except SQLAlchemyError as e:
            logger.error(f"카테고리별 통계 조회 중 오류 발생: {e}")
            return {}
        finally:
            session.close()
    
    def get_recent_products(self, limit=10):
        """
        최근 추가된 제품을 반환합니다.
        
        Args:
            limit (int, optional): 반환할 최대 제품 수. 기본값은 10.
            
        Returns:
            list: 최근 추가된 제품 목록
        """
        session = self.db.get_session()
        try:
            products = session.query(Product).order_by(
                Product.created_at.desc()
            ).limit(limit).all()
            
            return products
            
        except SQLAlchemyError as e:
            logger.error(f"최근 제품 조회 중 오류 발생: {e}")
            return []
        finally:
            session.close()
