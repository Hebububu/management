from app.utils.logger import mainLogger

from app.database.databasesetup import DatabaseSetup
from app.database.models import Product

# 로거 설정
logger = mainLogger()

# 데이터베이스 셋업 클래스 설정
db = DatabaseSetup()

class ProductCRUD:
    """
    product 테이블의 CRUD를 제공하는 클래스입니다.
    """

    def __init__(self):
        self.db = db

    def create_product(self, product_data: dict) -> Product:
        """
        새로운 제품을 생성하여 DB에 INSERT 합니다.
        Args:
            product_data (dict) : 제품 정보를 담은 딕셔너리
            예시 : {
                'platform' : 'platform_value',
                'seller_id' : 'seller_value',
                'product_id' : 123456789,
                'category' : 'category_value',
                'company' : 'company_value',
                'sale_name' : 'sale_name_value',
                'product_name' : 'product_name_value',
                'data' : { json 객체 },
                'created_at' : datetime 객체,
                'updated_at' : datetime 객체
            }
        returns:
            생성된 Product 객체 (성공 시)
            None (실패 시)
        """

        session = self.db.get_session()
        try:
            new_product = Product(
                platform=product_data['platform'],
                seller_id=product_data['seller_id'],
                product_id=product_data['product_id'],
                category=product_data['category'],
                company=product_data['company'],
                sale_name=product_data['sale_name'],
                product_name=product_data['product_name'],
                data=product_data['data'],
                created_at=product_data['created_at'],
                updated_at=product_data['updated_at']
            )
            session.add(new_product)
            session.commit()
            logger.info(f'{product_data["product_name"]} 제품 생성 완료')
            return new_product
        except Exception as e:
            logger.error(f'제품 생성 중 오류 발생: {e}')
            session.rollback()
            return None
        finally:
            session.close()

    def get_product_by_unique_keys():
        """
        복합 고유키를 사용하여 제품을 조회합니다.
        Args:
            platform (str) : 플랫폼 이름
            seller_id (str) : 판매자 ID
            product_id (int) : 제품 ID
        Returns:
            조회된 Product 객체 (성공 시)
            None (실패 시)
        """

    def create_or_update_product(self, product_data: dict) -> Product:
        """
        제품이 존재하면 data 필드만 업데이트하고,
        없으면 새로 생성합니다.
        Args:
            product_data (dict) : 제품 정보를 담은 딕셔너리
        Returns:
            생성된 Product 객체 (성공 시)
            None (실패 시)
        """

    def get_product_by_id(self, product_id: int) -> Product:
        """
        제품 ID를 기반으로 제품 정보를 조회합니다.
        Args: 
            product_id (int) : 조회할 제품의 고유 ID
        returns:
            조회된 Product 객체 (성공 시)
            None (실패 시)
        """

    def get_product_by_product_name(self, product_name: str) -> Product:
        """
        관리상품명을 기반으로 제품 정보를 조회합니다.
        Args:
            product_name (str) : 조회할 제품의 관리상품명
        returns:
            조회된 Product 객체 (성공 시)
            None (실패 시)
        """

    def update_product(self, product_id: int, update_data: dict) -> bool:
        """
        제품 정보를 업데이트합니다.
        Args:
            product_id (int) : 업데이트 할 제품의 고유 ID
            update_data (dict) : 업데이트 할 데이터를 담은 딕셔너리
                예시 : {'sale_name': 'new_sale_name', 'data': {new_data}}
        returns:
            업데이트 성공 시 True
            업데이트 실패 시 False
        """

    def delete_product(self, product_id: int) -> bool:
        """
        제품 정보를 DB에서 삭제합니다.
        Args:
            product_id (int): 삭제할 제품의 고유 ID
        returns:
            삭제 성공 시 True
            삭제 실패 시 False
        """