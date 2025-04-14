from app.utils.logger import mainLogger
from app.scripts.cafe24tokenmanager import TokenManager
from app.database.crud.product_crud import ProductCRUD

import requests
import json
import datetime

# 로거 정의
logger = mainLogger()

# 토큰 매니저 정의
token = TokenManager()

# 제품 데이터 관리 클래스   
crud = ProductCRUD()
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
            all_products (dict|list): 제품 데이터 객체 또는 객체 목록
        returns:
            sorted_products (list): 정렬된 제품 데이터 객체
        """
        sorted_products = []
        
        # 단일 제품인 경우 리스트로 변환
        if not isinstance(all_products, list):
            all_products = [all_products]
            
        for product in all_products:
            logger.info(f'제품명: {product["product_name"]}')

            product_data = {
                'platform': 'cafe24',
                'seller_id': seller_id,
                'product_id': product['product_no'],
                'category': None,
                'company': None,
                'sale_name': product['product_name'],
                'product_name': None,
                'tags': None,
                'data': product,
                'created_at': datetime.datetime.utcnow(),
                'updated_at': datetime.datetime.utcnow()
            }

            if product_data['product_name'] == '':
                logger.info(f'관리제품명이 입력되지 않았습니다. 기존 제품명을 사용합니다.')
                product_data['product_name'] = product['product_name']

            sorted_products.append(product_data)

        return sorted_products

    # def insert_products(self, sorted_products: list):
    #     """
    #     카페 24 제품 데이터를 DB에 INSERT 하는 메소드입니다.
    #     Args:
    #         sorted_products (list): 정렬된 제품 데이터 객체
    #     returns:
    #         None
    #     """

    def select_category(self):
        """
        미리 정의된 카테고리 목록을 출력하고, 사용자가 선택한 카테고리를 반환하는 메소드입니다.
        """
        categories = ['액상', '기기', '무화기', '코일', '팟', '일회용기기', '악세사리', '기타']

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
    

    def define_tags(self, category: str):
        """
        제품 데이터를 기반으로 태그를 정의하는 메소드입니다.
        태그는 입력받은 상품명과 카테고리에 맞는 소분류, 옵션명을 파이프(|)로 연결하여 구성됩니다.
        대분류(Category)에 따라 미리 정의된 소분류, 옵션명을 사용하거나, 직접 입력할 수 있습니다.
        Args:
            category (str): 대분류 카테고리
        Returns:
            tags (str): 태그
        """
        tags = ''

        # 액상 카테고리
        if category == '액상':
            sub_categories = ['입호흡액상', '폐호흡액상', '기타액상']
            logger.info('--------------------------------')
            logger.info('액상 카테고리 소분류 목록:')
            for idx, sub_category in enumerate(sub_categories, 1):
                logger.info(f'{idx}. {sub_category}')
            logger.info('--------------------------------')
            sub_choice = input('소분류 번호를 입력해주세요: ')
            if sub_choice.isdigit():
                idx = int(sub_choice)
                if 1 <= idx <= len(sub_categories):
                    sub_category = sub_categories[idx - 1]
                else:
                    logger.info('올바른 소분류 번호를 입력해주세요.')
            else:
                logger.info('숫자만 입력 가능합니다.')


            # 액상 용량 선택
            volume_options = ['60ml', '30ml', '100ml', '직접입력']
            logger.info('--------------------------------')
            logger.info('액상 카테고리 옵션명 목록:')
            for idx, volume_option in enumerate(volume_options, 1):
                logger.info(f'{idx}. {volume_option}')
            logger.info('--------------------------------')
            volume_choice = input('옵션명을 입력해주세요: ')
            if volume_choice.isdigit():
                idx = int(volume_choice)
                if 1 <= idx <= len(volume_options):
                    volume_option = volume_options[idx - 1]
                else:
                    logger.info('올바른 옵션명 번호를 입력해주세요.')
            else:
                logger.info('숫자만 입력 가능합니다.')  

            # 액상 니코틴 함유량 선택
            if volume_option == '직접입력':
                volume_option = input('액상 용량을 입력해주세요: ')  
            
            nicotine_options = ['3mg', '6mg', '9mg', '무니코틴', '직접입력']
            logger.info('--------------------------------')
            logger.info('액상 카테고리 옵션명 목록:')
            for idx, nicotine_option in enumerate(nicotine_options, 1):
                logger.info(f'{idx}. {nicotine_option}')
            logger.info('--------------------------------')
            nicotine_choice = input('옵션명을 입력해주세요: ')
            if nicotine_choice.isdigit():
                idx = int(nicotine_choice)
                if 1 <= idx <= len(nicotine_options):
                    nicotine_option = nicotine_options[idx - 1]
                else:
                    logger.info('올바른 옵션명 번호를 입력해주세요.')
            else:
                logger.info('숫자만 입력 가능합니다.')

            if nicotine_option == '직접입력':
                nicotine_option = input('니코틴 함유량을 입력해주세요: ')

            if 'sub_category' in locals():
                tags += f'|{sub_category}'

            if 'volume_option' in locals():
                tags += f'|{volume_option}'

            if 'nicotine_option' in locals() and nicotine_option.strip():
                tags += f'|{nicotine_option}'
                
                
        # 기기 카테고리
        if category == '기기':
            sub_categories = ['입호흡기기', '폐호흡기기', 'AIO기기', '기타기기']
            logger.info('--------------------------------')
            logger.info('기기 카테고리 소분류 목록:')
            for idx, sub_category in enumerate(sub_categories, 1):
                logger.info(f'{idx}. {sub_category}')
            logger.info('--------------------------------')
            sub_choice = input('소분류 번호를 입력해주세요: ')
            if sub_choice.isdigit():
                idx = int(sub_choice)
                if 1 <= idx <= len(sub_categories):
                    sub_category = sub_categories[idx - 1]
                else:
                    logger.info('올바른 소분류 번호를 입력해주세요.')
            else:
                logger.info('숫자만 입력 가능합니다.')

            # 기기 옵션명
            sub_options = input('옵션명을 입력해주세요(생략 가능): ')

            if 'sub_category' in locals():
                tags += f'|{sub_category}'

            if 'sub_options' in locals() and sub_options.strip():
                tags += f'|{sub_options.strip()}'

        # 무화기 카테고리
        if category == '무화기':
            sub_categories = ['RDA', 'RTA', 'RDTA', '기성탱크', '팟탱크', 'AIO팟', '일회용무화기', '기타무화기']
            logger.info('--------------------------------')
            logger.info('무화기 카테고리 소분류 목록:')
            for idx, sub_category in enumerate(sub_categories, 1):
                logger.info(f'{idx}. {sub_category}')
            logger.info('--------------------------------')
            sub_choice = input('소분류 번호를 입력해주세요: ')
            if sub_choice.isdigit():
                idx = int(sub_choice)
                if 1 <= idx <= len(sub_categories):
                    sub_category = sub_categories[idx - 1]
                else:
                    logger.info('올바른 소분류 번호를 입력해주세요.')

            # 무화기 옵션명
            sub_options = ['입호흡무화기', '폐호흡무화기']
            logger.info('--------------------------------')
            logger.info('무화기 카테고리 옵션명 목록:')
            for idx, sub_option in enumerate(sub_options, 1):
                logger.info(f'{idx}. {sub_option}')
            logger.info('--------------------------------')
            sub_option_choice = input('옵션명을 입력해주세요: ')
            if sub_option_choice.isdigit():
                idx = int(sub_option_choice)
                if 1 <= idx <= len(sub_options):
                    sub_option = sub_options[idx - 1]
                else:
                    logger.info('올바른 옵션명 번호를 입력해주세요.')
            else:
                logger.info('숫자만 입력 가능합니다.')

            # 무화기 세부 옵션명
            second_sub_options = input('세부 옵션명을 입력해주세요(생략 가능): ')

            if 'sub_category' in locals():
                tags += f'|{sub_category}'

            if 'sub_option' in locals():
                tags += f'|{sub_option}'

            if 'second_sub_options' in locals() and second_sub_options.strip():
                tags += f'|{second_sub_options.strip()}'

        # 코일 카테고리
        if category == '코일':
            sub_option_choice = input('옵션명을 입력해주세요(생략 가능): ')

            if 'sub_option_choice' in locals() and sub_option_choice.strip():
                tags += f'|코일|{sub_option_choice.strip()}'

        # 팟 카테고리
        if category == '팟':
            sub_options = ['일체형팟', '공팟', '기타팟']
            logger.info('--------------------------------')
            logger.info('팟 카테고리 옵션명 목록:')
            for idx, sub_option in enumerate(sub_options, 1):
                logger.info(f'{idx}. {sub_option}')
            logger.info('--------------------------------')
            
            sub_option_choice = input('옵션명을 입력해주세요: ')
            if sub_option_choice.isdigit():
                idx = int(sub_option_choice)
                if 1 <= idx <= len(sub_options):
                    sub_option = sub_options[idx - 1]
                else:
                    logger.info('올바른 옵션명 번호를 입력해주세요.')   
            else:
                logger.info('숫자만 입력 가능합니다.')

            ohm_option = input('옴 옵션을 입력해주세요(생략 가능): ')

            if 'sub_option' in locals():
                tags += f'|{sub_option}'
            
            if 'ohm_option' in locals() and ohm_option.strip():
                tags += f'{ohm_option.strip()}'

        if category == '일회용기기':
            sub_options = ['일체형', '교체형', '무니코틴', '기타일회용기기']
            logger.info('--------------------------------')
            logger.info('일회용기기 카테고리 옵션명 목록:')
            for idx, sub_option in enumerate(sub_options, 1):
                logger.info(f'{idx}. {sub_option}')
            logger.info('--------------------------------')
            
            sub_option_choice = input('옵션명을 입력해주세요: ')
            if sub_option_choice.isdigit():
                idx = int(sub_option_choice)
                if 1 <= idx <= len(sub_options):
                    sub_option = sub_options[idx - 1]
                else:
                    logger.info('올바른 옵션명 번호를 입력해주세요.')   
            else:
                logger.info('숫자만 입력 가능합니다.')
            
            if sub_option == '교체형':
                detail_option = ['배터리', '카트리지']
                logger.info('--------------------------------')
                logger.info('교체형기기 카테고리 세부 옵션명 목록:')
                for idx, detail_option in enumerate(detail_option, 1):
                    logger.info(f'{idx}. {detail_option}')
                logger.info('--------------------------------')

                detail_option_choice = input('세부 옵션명을 입력해주세요: ')
                if detail_option_choice.isdigit():
                    idx = int(detail_option_choice)
                    if 1 <= idx <= len(detail_option):
                        detail_option = detail_option[idx - 1]
                    else:
                        logger.info('올바른 세부 옵션명 번호를 입력해주세요.')
                else:
                    logger.info('숫자만 입력 가능합니다.')
            
            detail_option = input('세부 옵션명을 입력해주세요(생략 가능): ')

            if 'sub_option' in locals():
                tags += f'|{sub_option}'

            if 'detail_option' in locals() and detail_option.strip():
                tags += f'|{detail_option.strip()}'


        if category == '악세사리':
            sub_options = ['경통', '드립팁', '캡', '케이스', '도어', '배터리', '충전기', '리빌드용품', '기타악세사리']
            logger.info('--------------------------------')
            logger.info('악세사리 카테고리 옵션명 목록:')
            for idx, sub_option in enumerate(sub_options, 1):
                logger.info(f'{idx}. {sub_option}')
            logger.info('--------------------------------')

            sub_option_choice = input('옵션명을 입력해주세요: ')
            if sub_option_choice.isdigit():
                idx = int(sub_option_choice)
                if 1 <= idx <= len(sub_options):
                    sub_option = sub_options[idx - 1]
                else:
                    logger.info('올바른 옵션명 번호를 입력해주세요.')
            else:
                logger.info('숫자만 입력 가능합니다.')

            sub_detail_option = input('세부 옵션명을 입력해주세요(생략 가능): ')

            if 'sub_option' in locals():
                tags += f'|{sub_option}'

            if 'sub_detail_option' in locals() and sub_detail_option.strip():
                tags += f'|{sub_detail_option.strip()}'

        if category == '기타':
            sub_option = '기타'

            sub_detail_option = input('세부 옵션명을 입력해주세요(생략 가능): ')

            if sub_option in locals():
                tags += f'|{sub_option}'

            if sub_detail_option in locals() and sub_detail_option.strip():
                tags += f'|{sub_detail_option.strip()}'

        return tags
