from app.scripts.navertokenmanager import NaverTokenManager
from app.scripts.naverdatamanager import NaverDataManager
from app.utils.logger import mainLogger
from app.database.crud.product_crud import ProductCRUD
import json
import os

db = ProductCRUD()
logger = mainLogger()
token = NaverTokenManager(config_prefix='49jd')
naver = NaverDataManager()

products_list = naver.get_all_products_list(config_prefix='49jd')

sorted_product_data = naver.sort_product_data(products_list, config_prefix='49JD')

success_count = 0
fail_count = 0

for product in sorted_product_data:
    try:
        # 제품 데이터를 데이터베이스에 저장
        db.create_product(product)
        success_count += 1  # 저장 성공 카운트 증가
        logger.info(f'{product["sale_name"]} 제품 데이터가 데이터베이스에 저장되었습니다.')
    except Exception as e:
        fail_count += 1  # 저장 실패 시 실패 카운트 증가
        logger.error(f'{product["sale_name"]} 제품 데이터 저장 중 오류 발생: {e}')

logger.info(f'총 {success_count}개의 제품 데이터가 성공적으로 저장되었습니다.')
logger.info(f'총 {fail_count}개의 제품 데이터가 저장에 실패했습니다.')

