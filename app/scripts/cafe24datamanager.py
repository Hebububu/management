from app.utils.logger import mainLogger
from app.scripts.cafe24tokenmanager import TokenManager

import requests
import json
import datetime

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
    
    def sort_products_data(self, all_products: dict, seller_id: str):
        """
        DB 저장에 필요한 정보를 추출하고 객체로 만드는 메소드입니다.
        Args:
            seller_id (str): 카페24 스토어명입니다.
            all_products (dict): 제품 데이터 객체
        returns:
            sorted_products (list): 정렬된 제품 데이터 객체
        """
        sorted_products = []
        for product in all_products:

            logger.info(f'제품명: {product["product_name"]}')
            product_data = {
                'platform': 'cafe24',
                'seller_id': seller_id,
                'product_id': product['product_no'],
                'category': self.select_category(), 
                'company': input('회사명을 입력해주세요: '),
                'sale_name': product['product_name'],
                'product_name': input('관리제품명을 입력해주세요: '),
                'data': product,
                'created_at': datetime.datetime.utcnow(),
                'updated_at': datetime.datetime.utcnow()
            }

            if product_data['product_name'] == '':
                logger.info(f'관리제품명이 입력되지 않았습니다. 기존 제품명을 사용합니다.')
                product_data['product_name'] = product['product_name']

            sorted_products.append(product_data)

        return sorted_products

    def insert_all_products(self):
        """
        카페 24 제품 데이터를 DB에 INSERT 하는 메소드입니다.
        """

    def select_category(self):
        """
        미리 정의된 카테고리 목록을 출력하고, 사용자가 선택한 카테고리를 반환하는 메소드입니다.
        """
        categories = ['액상', '기기', '무화기', '소모품', '기타']

        logger.info('--------------------------------')
        logger.info('카테고리 목록:')
        for idx, category in enumerate(categories, 1):
            logger.info(f'{idx}. {category}')
        logger.info('--------------------------------')

        while True:
            choice = input('카테고리 번호를 입력해주세요: ')
            try:
                choice = int(choice)
                if 1 <= choice <= len(categories):
                    return categories[choice - 1]
                else:
                    logger.info('올바른 카테고리 번호를 입력해주세요.')
            except ValueError:
                logger.info('숫자만 입력 가능합니다.')
    
    def define_product_name(self, category: str):
        """
        제품 데이터를 기반으로 관리 제품명을 정의하는 메소드입니다.
        제품명은 입력받은 상품명과 카테고리에 맞는 소분류, 옵션명을 파이프(|)로 연결하여 구성됩니다.
        대분류(Category)에 따라 미리 정의된 소분류, 옵션명을 사용하거나, 직접 입력할 수 있습니다.
        Args:
            category (str): 대분류 카테고리
        Returns:
            product_name (str): 관리제품명
        """
        product_name = input('상품명을 입력해주세요: ')
        if category == '액상':
            sub_categories = ['입호흡액상', '폐호흡액상', '기타액상']
            logger.info('액상 카테고리 소분류 목록:')
            for idx, sub_category in enumerate(sub_categories, 1):
                logger.info(f'{idx}. {sub_category}')
            sub_choice = input('소분류 번호를 입력해주세요: ')
            if sub_choice.isdigit():
                idx = int(sub_choice)
                if 1 <= idx <= len(sub_categories):
                    sub_category = sub_categories[idx - 1]
                else:
                    logger.info('올바른 소분류 번호를 입력해주세요.')
            else:
                logger.info('숫자만 입력 가능합니다.')

            # 나머지도 만들어야함 

