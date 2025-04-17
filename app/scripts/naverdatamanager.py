from app.utils.logger import mainLogger
from app.scripts.navertokenmanager import NaverTokenManager
from app.database.crud.product_crud import ProductCRUD
import datetime
import requests
import json

# 로거 정의
logger = mainLogger()

# 제품 데이터 관리 클래스
crud = ProductCRUD()

class NaverDataManager:
    """
    네이버커머스 스마트스토어 관련 데이터를 처리하는 클래스입니다.
    """

    def __init__(self):
        self.logger = logger
        self.url = 'https://api.commerce.naver.com/external/v1/products/'

    def get_all_products_list(self, config_prefix: str):
        """
        네이버커머스 스마트스토어 전체 제품 목록을 가져오는 메소드입니다.
        Returns:
            all_products_list (list): 네이버커머스 스마트스토어 전체 제품 목록
        """

        token = NaverTokenManager(config_prefix=config_prefix)

        all_products_list = []
        page = 0
        limit = 500


        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json;charset=UTF-8',
            'Authorization': f'Bearer {token.get_access_token()}'
        }

        while True:
            payload = json.dumps({
                'productStatusTypes': [
                    'SALE'
                ],
                'page': page,
                'size': limit,
                'orderType': 'NO',
            })

            response = requests.request('POST',self.url+'search',headers=headers,data=payload)
            data = response.json().get('contents',[])

            logger.info(f'{page}페이지 조회, 상품 수: {len(data)}')

            all_products_list.extend(data)

            if len(data) < limit:
                break

            page += 1

        return all_products_list
    
            

    def get_product_data(self, all_products_list: list, config_prefix: str):
        """
        all_products_list를 기반으로 네이버커머스 제품 데이터를 가져오는 메소드입니다.
        Args:
            all_products_list (list): 네이버커머스 제품 ID 리스트
        Returns:
            product_data (list): 네이버커머스 제품 데이터
        """

        token = NaverTokenManager(config_prefix=config_prefix)

        product_data = []

        for channel_product_number in all_products_list:
            url = f'{self.url}{channel_product_number}'

            payload = {}
            headers = {
                'Accept': 'application/json;charset=UTF-8',
                'Authorization': f'Bearer {token.get_access_token()}'
            }

            response = requests.request('GET',url,headers=headers,data=payload)
            response.raise_for_status()
            data = response.text

            product_data.append(data)

        return product_data
            

    def sort_product_data(self, product_data: dict, config_prefix: str):
        """
        DB 저장에 필요한 정보를 추출하고 객체로 만드는 메소드입니다.
        Args:
            product_data (dict): 네이버커머스 제품 데이터
            seller_id (str): 판매자 ID
        Returns:
            sorted_product_data (dict): DB 저장에 필요한 정보를 추출한 제품 데이터
        """

        sorted_product_data = []

        for product in product_data:
            logger.info(f'제품명: {product["channelProducts"][0]["name"]}')

            product_data = {
                'platform': 'naverCommerce',
                'seller_id': config_prefix,
                'product_id': product['channelProducts'][0]['channelProductNo'],
                'category': None,
                'company': product['channelProducts'][0].get('brandName', None),
                'sale_name': product['channelProducts'][0]['name'],
                'product_name': None,
                'tags': None,
                'data': product,
                'created_at': datetime.datetime.utcnow(),
                'updated_at': datetime.datetime.utcnow()
            }

            sorted_product_data.append(product_data)

        return sorted_product_data


    
    #def select_category(self)
    #굳이 안만들고 그냥 저기서 재활용해도 될거같은데 생각해봄 

    #define_tags(self, category: str)
    #마찬가지일듯


        
        
