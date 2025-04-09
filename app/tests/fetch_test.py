from app.scripts.cafe24tokenmanager import TokenManager
from app.utils.logger import mainLogger
import requests
import json
import os

logger = mainLogger()

def call_request(info='products/count'):

    token = TokenManager()
    access_token = token.get_access_token()

    print(f'access_token = {access_token}')

    url = f'https://richcp.cafe24api.com/api/v2/admin/{info}'
    headers = {
        'Authorization' : f'Bearer {access_token}',
        'Content-Type' : 'application/json'
    }

    response = requests.request('GET', url, headers=headers)
    response_dict = response.json()

    print(response_dict)

def get_all_products():
    token = TokenManager()
    access_token = token.get_access_token()

    logger.info(f"엑세스 토큰: {access_token}")

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    all_products = []
    since_product_no = 1
    limit = 100

    while True:
        info = f'products?fields=product_no,product_code&since_product_no={since_product_no}&limit={limit}'
        url = f'https://richcp.cafe24api.com/api/v2/admin/{info}'
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

        logger.info(f'{since_product_no} 조회, 상품 수: {num_products}')

        if num_products < limit:
            break

        since_product_no += limit

    pretty_json = json.dumps(all_products, indent=4, ensure_ascii=False)
    filename = 'products_output.json'

    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(all_products, json_file, indent=4)

    return all_products

get_all_products()
