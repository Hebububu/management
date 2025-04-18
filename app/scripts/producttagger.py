import re
import json
import kiwipiepy

from app.utils.logger import mainLogger

logger = mainLogger()

class ProductTagger:
    """
    제품 자동 태깅 시스템 클래스입니다.

    product_name = '회사명'|'제품명'
    company = '회사명'
    category = '카테고리'
    tags = '소분류'|'소분류 하위 소분류'|'옵션명'(선택사항)
    라는 규칙으로 제품명과 태그를 입력하게끔 할 것임.
    """

    def __init__(self, user_dict_path: str = 'app/data/user_dict.txt'):
        """
        초기화 메서드입니다.
        """
        self.tagger = kiwipiepy.Kiwi()
        self.user_dict_path = user_dict_path
        self.load_user_dict()

    def load_user_dict(self):
        """
        사용자 사전을 로드합니다.
        형태소 분석기에 회사명, 카테고리 등의 사용자 정의 단어를 등록합니다.
        """
        try:
            # 사용자 사전 파일이 존재하는지 확인
            with open(self.user_dict_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 사용자 사전 등록
            for line in lines:
                line = line.strip()
                # 주석 라인 무시
                if line.startswith('#') or not line:
                    continue
                    
                # 형태소 분석기 사전에 추가
                try:
                    parts = line.split()
                    if len(parts) >= 2:
                        word = parts[0]
                        tag_info = parts[1]
                        score = -3.0  # 기본 점수
                        
                        # 점수가 명시되어 있는 경우 해당 점수 사용
                        if len(parts) >= 3:
                            try:
                                score = float(parts[2])
                            except ValueError:
                                pass
                        
                        # 이형태 처리: "이치스 이지스/NNP -3.0" 형태 처리
                        if '/' in tag_info:
                            orig_form, tag = tag_info.split('/')
                            self.tagger.add_user_word(word, tag, score=score, orig_form=orig_form)
                        else:
                            # 일반 형태: "고드름 NNP -3.0"
                            self.tagger.add_user_word(word, tag_info, score=score)
                except Exception as e:
                    logger.error(f"사전 단어 추가 실패: {line}, 오류: {str(e)}")
            
            logger.info(f"사용자 사전 로드 완료: {self.user_dict_path}")
        except FileNotFoundError:
            logger.warning(f"사용자 사전 파일을 찾을 수 없음: {self.user_dict_path}")
            # 사전 파일이 없어도 프로그램이 작동하도록 빈 디렉토리 생성
            import os
            os.makedirs(os.path.dirname(self.user_dict_path), exist_ok=True)
            with open(self.user_dict_path, 'w', encoding='utf-8') as f:
                f.write("# 사용자 정의 사전 파일\n")
                f.write("# 형식: '단어 태그 점수', '이형태 원래형태/태그 점수'\n")
                
            logger.info(f"빈 사용자 사전 파일 생성됨: {self.user_dict_path}")
        except Exception as e:
            logger.error(f"사용자 사전 로드 중 오류 발생: {str(e)}")
            # 치명적인 오류가 아니라면 계속 진행
            pass

    def extract_company(self, sale_name: str, data: dict, platform: str = None) -> str:
        """
        회사명을 추출합니다.

        네이버의 경우
        이미 product_manufacturer 필드에 회사명이 있어, data json 객체에 company 항목이 채워져 있음.
        네이버의 제품이 가장 많으니, 네이버의 제품 태깅 결과를 참조해서 company 항목을 채워 넣는 방식을 사용하는게 좋을 듯함.

        카페24의 경우 
        거의 모든 경우에 회사명이 제품명의 맨 앞에 와 있는 경우가 많음. 
        네이버의 제품 태깅 결과를 참조하여 회사명을 추출해 넣으면 좋을 것 같음. 

        다만 유의해야 하는 부분은, 카페24는 액상을 판매하고 있기에, 액상 제품의 경우 회사명이 굉장히 모호한 경우가 많음.
        빠른 개발을 위해서 유통사(도매몰) 명칭을 회사명으로 사용하기 보다는, 액상 제품명 자체를 company 항목에 넣는 방식으로 하는게 좋을 듯 함.
        
        예) product_name : 고드름 입호흡 액상 30ml 인 경우 
        company : 고드름

        Args:
            sale_name: 판매 제품명
            data: 제품 데이터 JSON 객체
            platform: 플랫폼 이름 (네이버, 카페24 등)
        
        Returns:
            추출된 회사명
        """
        # 이미 company가 data에 있는 경우 우선 사용
        if data and isinstance(data, dict) and 'company' in data:
            return data['company']
        
        # 네이버 커머스 플랫폼인 경우 데이터 구조에서 회사명 추출
        if platform and platform.lower() == 'naver' and data and isinstance(data, dict):
            # channelProducts 배열에서 정보 확인
            if 'channelProducts' in data and isinstance(data['channelProducts'], list) and data['channelProducts']:
                channel_product = data['channelProducts'][0]  # 첫 번째 채널 제품 사용
                
                # manufacturerName 필드가 있는 경우 사용
                if 'manufacturerName' in channel_product and channel_product['manufacturerName']:
                    return channel_product['manufacturerName']
                    
                # brandName 필드가 있는 경우 사용
                if 'brandName' in channel_product and channel_product['brandName']:
                    return channel_product['brandName']
                    
                # name에서 처음 부분 추출 시도
                if 'name' in channel_product and channel_product['name']:
                    name_parts = channel_product['name'].split()
                    if name_parts:
                        # 첫 단어 반환 (네이버 제품은 대부분 "회사명 제품명" 형태로 등록됨)
                        return name_parts[0]
        
        # 회사명 추출을 위한 형태소 분석 수행
        if not sale_name:
            return ""
        
        # 제품명 첫 단어를 회사명으로 간주 (팀내 공통 패턴)
        # 대부분의 전자담배 제품은 "회사명 제품명 옵션" 형태로 표기됨
        words = sale_name.split()
        if words:
            # 회사명 후보들 (공통적으로 사용되는 회사명들)
            common_companies = [
                '닷모드', '아스베이프', '스모크', '유웰', '부푸', '프리맥스', 
                '헬베이프', '베이포레소', '긱베이프', '로스트베이프', 
                '호라이즌', '아스파이어', '벱티오', '벱티오',
                'IPV', 'sx mini', '프리믹스'
            ]

            # 첫 단어가 회사명 리스트에 있는지 확인
            if words[0] in common_companies:
                return words[0]
                
            # 회사명이 합쳐서 표기되는 경우 처리
            for company in common_companies:
                if company.lower() in sale_name.lower():
                    return company
            
            # 그래도 찾지 못하면 첫 단어 반환
            return words[0]
        
        # 아무것도 추출하지 못했을 경우 빈 문자열 반환
        return ""

    def extract_category(self):
        """
        제품 카테고리를 추출합니다. 

        카테고리는 액상 / 기기 / 무화기 / 코일 / 팟 / 일회용기기 / 악세사리 / 기타 로 구분하기로 이미 약속했음.
        제품명의 기기, 코일, 팟, 등의 키워드를 찾아서 카테고리를 결정하는 방식으로 하되,
        네이버의 제품 태깅 결과를 참조하여 카테고리를 결정하는 방식으로 하는게 좋을 듯 함.
        """
    
    def extract_tags(self):
        """
        제품 태그를 추출합니다.

        태그의 경우 카테고리의 하위 소분류 + 옵션명(선택사항) 으로 구성할것임.
        각 소분류는 다음과 같음

        액상 - 입호흡액상 | 폐호흡액상 | 첨가제 | 기타액상

        기기 - 입호흡기기 | 폐호흡기기 | AIO기기 | 기타기기

        무화기 - RDA | RTA | RDTA | 기성탱크 | 팟탱크 | AIO팟 | 일회용 | 기타무화기
        무화기 옵션 - 입호흡 | 폐호흡

        코일 - (코일은 따로 소분류를 두지 않고 옵션을 선택사항으로 넣을 것)

        팟 - 일체형팟 | 공팟 | 기타팟

        일회용기기 - 일체형 | 교체형 | 무니코틴 | 기타일회용기기
        일회용기기 옵션 - {배터리 | 카트리지} <= 교체형인 경우에만 옵션으로 넣을 것

        악세사리 - 경통 | 드립팁 | 캡 | 케이스 | 도어 | 배터리 | 충전기 | 리빌드용품 | 기타악세사리

        기타 - (기타 역시도 따로 소분류를 두지 않고 옵션을 선택사항으로 넣을 것)
        """

    def extract_product_name(self):
        pass

    
        




