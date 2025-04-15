# -*- coding: utf-8 -*-
"""
이 테스트 코드는 데이터베이스에 저장된 제품 데이터 중
category, company, product_name, tags 값이 null인 제품을 불러와
각 제품별로 카테고리 선택, 태그 정의, 관리상품명, 회사명을 입력받아
업데이트를 진행하는 예시 코드입니다.
"""

# 필요한 모듈 임포트
from app.scripts.cafe24datamanager import Cafe24DataManager
from app.database.crud.product_crud import ProductCRUD
from app.database.models import Product
from app.utils.logger import mainLogger

# 로거 설정
logger = mainLogger()

# Cafe24DataManager와 ProductCRUD 인스턴스 생성
cafe24 = Cafe24DataManager()
crud = ProductCRUD()

def update_missing_products():
    # 데이터베이스 세션 생성 - 제품 데이터를 불러오기 위함
    session = crud.db.get_session()
    # category, company, product_name, tags가 모두 null인 제품들을 검색
    missing_products = session.query(Product).filter(
        Product.category == None,
        Product.company == None,
        Product.product_name == None,
        Product.tags == None
    ).all()
    session.close()
    
    if not missing_products:
        logger.info("업데이트할 제품 데이터가 없습니다.")
        return
    
    # 각 제품에 대해 순차적으로 업데이트 진행
    for product in missing_products:
        logger.info(f"제품 ID {product.seller_id} / {product.sale_name} 업데이트 시작")
        
        # 업데이트할 관리상품명 입력
        logger.info(f'판매상품명 : {product.sale_name}')
        product_name = input("업데이트할 제품명(관리상품명)을 입력해주세요: ")
        # 업데이트할 회사명 입력
        logger.info(f'판매상품명 : {product.sale_name}')
        company = input("업데이트할 회사명을 입력해주세요: ")
        # 카테고리 선택 (사용자 입력 필요)
        logger.info(f'판매상품명 : {product.sale_name}')
        category = cafe24.select_category()  # 기존의 카테고리 선택 함수 사용
        # 선택된 카테고리를 기반으로 태그 정의 (사용자 입력 필요)
        logger.info(f'판매상품명 : {product.sale_name}')
        tags = cafe24.define_tags(category)
        
        update_data = {
            'category': category,
            'tags': tags,
            'product_name': product_name,
            'company': company
        }
        
        # 업데이트 진행
        try:
            result = crud.update_product(product.product_id, product.platform, product.seller_id, update_data)
            if result:
                logger.info(f"제품 ID {product.product_id} 업데이트 성공")
            else:
                logger.info(f"제품 ID {product.product_id} 업데이트 실패")
        except Exception as e:
            logger.error(f"제품 ID {product.product_id} 업데이트 중 오류 발생: {e}")
    
    logger.info("모든 제품 업데이트 완료.")

if __name__ == '__main__':
    update_missing_products()