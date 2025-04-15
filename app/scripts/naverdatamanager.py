from app.utils.logger import mainLogger
from app.scripts.navertokenmanager import NaverTokenManager
from app.database.crud.product_crud import ProductCRUD
import datetime
import requests
import json

# 로거 정의
logger = mainLogger()

# 토큰 매니저 정의
token = NaverTokenManager()

# 제품 데이터 관리 클래스
crud = ProductCRUD()

class NaverDataManager:
    """
    네이버커머스 스마트스토어 관련 데이터를 처리하는 클래스입니다.
    """

    def __init__(self):
        self.logger = logger
        self.token = token.get_access_token()
        self.url = 'https://api.commerce.naver.com/external/v1/products/'

    def get_all_products_list(self):
        """
        네이버커머스 스마트스토어 전체 제품 목록을 가져오는 메소드입니다.
        Returns:
            all_products_list (list): 네이버커머스 스마트스토어 전체 제품 목록
        """

        limit = 500
        page = 0
        all_products_list = []


        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json;charset=UTF-8',
            'Authorization': f'Bearer {self.token}'
        }

        while True:
            payload = json.dumps({
                'searchKeywordType': 'CHANNEL_PRODUCT_NO',
                'channelProductNos': [
                    0
                ],
                'productStatusTypes': [
                    'SALE'
                ],
                'page': page,
                'size': limit,
                'orderType': 'NO',
            })

            response = requests.request('POST',self.url+'search/',headers=headers,data=payload)
            response.raise_for_status()
            data = response.json()

            all_products_list.extend(data)

            if len(data) < limit:
                break

            page += 1

        return all_products_list
            

    def get_product_data(self, all_products_list: list):
        """
        all_products_list를 기반으로 네이버커머스 제품 데이터를 가져오는 메소드입니다.
        Args:
            all_products_list (list): 네이버커머스 제품 ID 리스트
        Returns:
            product_data (list): 네이버커머스 제품 데이터
        """


        product_data = []

        for channel_product_number in all_products_list:
            url = f'{self.url}{channel_product_number}'

            payload = {}
            headers = {
                'Accept': 'application/json;charset=UTF-8',
                'Authorization': f'Bearer {self.token}'
            }

            response = requests.request('GET',url,headers=headers,data=payload)
            response.raise_for_status()
            data = response.json()

            product_data.append(data)

        return product_data
            

    def sort_product_data(self, product_data: dict, seller_id: str):
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
            logger.info(f'제품명: {product["example_name"]}')

            product_data = {
                'platform': 'naver',
                'seller_id': seller_id,
                'product_id': product['channel_product_number'],
                'category': None,
                'company': None,
                'sale_name': product['example_name'],
                'product_name': None,
                'tags': None,
                'data': product,
                'created_at': datetime.datetime.utcnow(),
                'updated_at': datetime.datetime.utcnow()
            }

            if product_data['example_name'] == '':
                logger.info(f'관리제품명이 입력되지 않았습니다. 기존 제품명을 사용합니다.')
                product_data['product_name'] = product['example_name']

            sorted_product_data.append(product_data)

        return sorted_product_data


    
    #def select_category(self)
    #굳이 안만들고 그냥 저기서 재활용해도 될거같은데 생각해봄 

    #define_tags(self, category: str)
    #마찬가지일듯


        
        
