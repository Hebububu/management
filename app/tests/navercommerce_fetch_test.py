from app.scripts.navertokenmanager import NaverTokenManager
from app.scripts.naverdatamanager import NaverDataManager
from app.utils.logger import mainLogger
import json
import os

logger = mainLogger()
token = NaverTokenManager(config_prefix='49jd')
naver = NaverDataManager()

products_list = naver.get_all_products_list(config_prefix='49jd')

sorted_product_data = naver.sort_product_data(products_list, config_prefix='49JD')

json_data = json.dumps(sorted_product_data, default=str, indent=4, ensure_ascii=False)

with open('navercommerce_fetch_test.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)

logger.info('navercommerce_fetch_test.json 파일이 생성되었습니다.')
