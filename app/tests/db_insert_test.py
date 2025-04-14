from app.database.crud.product_crud import ProductCRUD
from app.utils.logger import mainLogger
from app.database.databasesetup import DatabaseSetup
from app.scripts.cafe24datamanager import Cafe24DataManager

logger = mainLogger()

db = DatabaseSetup()

crud = ProductCRUD()

cafe24 = Cafe24DataManager()

seller_id = 'richcp' # 리치로 테스트
platform = 'cafe24'

# 카페24로부터 제품 데이터 불러오기
all_products = cafe24.get_all_products(seller_id)
# 불러온 제품 데이터 필터링하기 (DB에 저장된 제품 데이터 제외)
for product in all_products:
    existing_product = crud.get_product_by_unique_keys(platform, seller_id, product['product_no'])
    if existing_product:
        logger.info(f'제품번호: {product["product_no"]} 제품명: {product["product_name"]} 제품이 이미 존재합니다.')
        continue
    
    else:
        logger.info(f'제품번호: {product["product_no"]} 제품명: {product["product_name"]} 제품이 존재하지 않습니다.')
        
        # DB 저장에 필요한 정보를 추출하고 객체로 만들기
        sorted_product = cafe24.sort_products_data(product, seller_id)[0]  # 리스트의 첫 번째 요소 가져오기

        # 정렬된 제품 데이터를 DB에 저장
        crud.create_product(sorted_product)
