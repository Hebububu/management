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

sorted_products = cafe24.sort_products_data(all_products, seller_id)

for product in sorted_products:
    crud.create_product(product)
