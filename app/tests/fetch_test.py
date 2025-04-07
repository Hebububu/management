from app.scripts.cafe24tokenmanager import TokenManager
import requests
import json

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
    print(f'access_token = {access_token}')
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    all_products = []
    page = 1
    limit = 100  # 한 페이지당 조회할 상품 수
    while True:
        info = f'products?fields=product_no,product_code&page={page}&limit={limit}'
        url = f'https://richcp.cafe24api.com/api/v2/admin/{info}'
        response = requests.get(url, headers=headers)
        
        # 응답 본문이 비어 있거나 HTTP 에러이면 루프 종료
        if response.status_code != 200 or not response.text.strip():
            print(f"페이지 {page}에서 응답이 비어 있습니다. 종료합니다.")
            break
        
        try:
            data = response.json()  # 응답 JSON 파싱
        except json.JSONDecodeError:
            print(f"페이지 {page}에서 JSON 파싱 실패. 종료합니다.")
            break
        
        products = data.get('products', [])
        all_products.extend(products)
        print(f"페이지 {page} 조회, 제품 수: {len(products)}")
        
        # 만약 응답받은 상품 수가 limit보다 작다면 마지막 페이지로 판단
        if len(products) < limit:
            break
        page += 1

    pretty_json = json.dumps(all_products, indent=4, ensure_ascii=False)
    print(pretty_json)
    
    return all_products

get_all_products()