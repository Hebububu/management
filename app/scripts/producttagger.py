import re
import json


class ProductTagger:
    def __init__(self):

        # 이미 알려진 회사 / 브랜드명 (액상의 경우 액상명을 그대로 사용할 가능성이 높음. / 도매몰로 작성할 가능성도 염두.)

        # 카테고리별 키워드 

        ## 팟 - 팟과 코일 둘다 옴에 관련된 키워드가 나오는걸 염두해서 만들어야 할 것 같음. 

        # 용량 및 니코틴 정규식 

        # 색상 프리셋? (기기 옵션에 사용하면 좋을 거 같은데..)

    def tag_product(self, product):
        """제품에 태그를 등록하는 함수"""

    def extract_company(self, sale_name):
        """판매명에서 회사/브랜드명 추출 (하드코딩 방식)"""

    def extract_company_fuzzy(self, sale_name):
        """퍼지 매칭(유사도 기반으로) 회사/브랜드명 추출"""

    def extract_category(self, sale_name, data_json):
        """판매명과 데이터에서 카테고리 추출"""

    def extract_product_name(self, sale_name, company):
        """회사명을 알 때 제품명 추출"""

    def extract_tags(self, sale_name, data_json, company, category):
        """판매명과 데이터로부터 태그 추출"""

    