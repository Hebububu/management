from app.utils.logger import mainLogger
from app.scripts.cafe24tokenmanager import TokenManager

import requests
import json

# 로거 정의
logger = mainLogger()

# 토큰 매니저 정의
token = TokenManager()

class Cafe24DataManager():
    """
    카페 24 관련 데이터를 처리하는 클래스입니다.
    """

    def __init__(self):
        self.logger = logger
        self.token = token
    

    def get_all_products(self, seller_id: str):
        """
        카페 24 전체 제품 데이터를 가져오는 메소드입니다.
        Args:
            seller_id (str): 카페24 스토어명입니다.
        returns:
            all_products (dict): 제품 데이터 객체
            }
        """
        access_token = token.get_access_token()
        logger.info(f'액세스 토큰: {access_token}')

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        all_products = []
        start_no = 1
        limit = 100

        while True:
            info = f'products?embed=options&since_product_no={start_no}&limit={limit}'
            url = f'https://{seller_id}.cafe24api.com/api/v2/admin/{info}'
            response = requests.get(url, headers=headers)

            if response.status_code != 200 or not response.text.strip():
                logger.error('응답이 비어 있습니다. 종료합니다.')
                break
            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.error('JSON 파싱 실패. 종료합니다.')

            products = data.get('products',[])

            num_products = len(products)
            all_products.extend(products)

            logger.info(f'{start_no} 조회, 상품 수: {num_products}')

            if num_products < limit:
                break

            start_no += limit

        return all_products
    
    def sort_products_data(self):
        """
        DB 저장에 필요한 정보를 추출하고 객체로 만드는 메소드입니다.
        """

    def insert_all_products(self):
        """
        카페 24 제품 데이터를 DB에 INSERT 하는 메소드입니다.
        """

