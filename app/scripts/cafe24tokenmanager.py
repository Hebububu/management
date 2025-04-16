import requests, json
from datetime import datetime
from dotenv import load_dotenv
import os
import base64
from app.utils.logger import mainLogger

# 환경 변수 로드
load_dotenv()

# 로거 설정
logger = mainLogger()
class TokenManager:

    def __init__(self, config_prefix: str, code=None, mall_id=None, filename=None, redirect_uri=None):

        self.config_prefix = config_prefix

        self.mall_id = mall_id if mall_id else os.getenv(f'{self.config_prefix}_MALL')

        self.redirect_uri = redirect_uri if redirect_uri else f'https://{self.mall_id}.cafe24.com/order/basket.html'

        if code is None:
            self.get_auth_code()
            self.code = None
        else:
            self.code = code

        self.filename = filename if filename else f'{self.config_prefix}_tokens.json'

        self.base64encode_atr = self.encode_client()
        self.tokens = self.load_tokens()

    def get_auth_code(self):
        """
        최초 인증 코드를 받기 위한 함수입니다.
        """
        mall_id = self.mall_id
        client_id = os.getenv(f'{self.config_prefix}_CLIENT_ID')
        redirect_uri = self.redirect_uri
        state = 'app_install'
        scope = 'mall.read_application,mall.write_application,mall.read_product,mall.write_product,mall.read_store,mall.write_store'

        url = f'https://{mall_id}.cafe24api.com/api/v2/oauth/authorize?response_type=code&client_id={client_id}&state={state}&redirect_uri={redirect_uri}&scope={scope}'
        logger.info(f'인증 코드 발급용 url: {url}')

    def encode_client(self):
        """
        클라이언트 정보를 base64 인코딩합니다.
        """
        client_id = os.getenv(f'{self.config_prefix}_CLIENT_ID')
        client_secret = os.getenv(f'{self.config_prefix}_CLIENT_SECRET')

        code = f'{client_id}:{client_secret}'
        encoded_code = base64.b64encode(code.encode('utf-8'))
        base64_encode_str = encoded_code.decode('utf-8')

        logger.info(f'인코딩 된 클라이언트 정보: {base64_encode_str}')
        return base64_encode_str
    
    def initiate_token(self):
        """
        토큰을 발급받고 저장합니다.
        """
        code = self.code
        redirect_uri = self.redirect_uri
        mall_id = self.mall_id
        base64encode_atr = self.base64encode_atr
        filename = self.filename

        url = f'https://{mall_id}.cafe24api.com/api/v2/oauth/token'
        payload = f'grant_type=authorization_code&code={code}&redirect_uri={redirect_uri}'

        headers = {
            'Authorization' : f'Basic {base64encode_atr}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = requests.request("POST", url, data=payload, headers=headers)
            logger.info(f"토큰 발급 요청 완료\n {response}")

            tokens = response.json()
            access_token = tokens['access_token']
            logger.info(f'엑세스 토큰: {access_token}')
            
        except Exception as e:
            logger.info(f'토큰 발급 실패 {str(e)}')

        with open(filename,'w') as json_file:
            json.dump(tokens, json_file, indent=4)

        return access_token

    def load_tokens(self):
        """
        토큰 파일을 로드합니다.
        """
        try:
            with open(self.filename, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            logger.error(f'토큰 파일을 찾을 수 없습니다.')
        except json.JSONDecodeError:
            logger.error(f'올바른 json 파일 형식이 아닙니다.')

    def save_token(self):
        """
        토큰 파일을 저장, 업데이트합니다.
        """
        with open(self.filename, 'w') as json_file:
            json.dump(self.tokens, json_file, indent=4)

    def refresh_access_token(self):
        """
        리프레시 토큰을 기반으로 토큰을 재발급받습니다.
        """
        url = f'https://{self.mall_id}.cafe24api.com/api/v2/oauth/token'
        payload = f"grant_type=refresh_token&refresh_token={self.tokens['refresh_token']}"
        headers = {
            'Authorization': f'Basic {self.base64encode_atr}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(url,data=payload, headers=headers)
            response.raise_for_status()
            new_tokens = response.json()

            # 업데이트된 토큰 정보 저장
            self.tokens = new_tokens
            self.save_token()

            logger.info(f'재발급 된 엑세스 토큰 {new_tokens}')
            return new_tokens['access_token']

        except requests.RequestException as e:
            raise Exception(f'토큰 재발급에 실패했습니다.: {str(e)}')
        
    def is_valid_datetime(self, value):
        """
        입력값이 날짜 형식인지 확인하고 반환합니다.
        """
        try:
            if isinstance(value, datetime):
                return value
            return datetime.fromisoformat(value)
        except ValueError:
            return None
        
    def get_access_token(self):
        """
        유효한 엑세스 토큰을 반환하거나 새로 발급받습니다.
        """
        now = datetime.now()
        logger.info(f'현재 시각: {now}')

        # 기존 접속 토큰의 유효성 확인
        expires_at = self.is_valid_datetime(self.tokens.get('expires_at'))
        if expires_at and now < expires_at:
            logger.info(f'토큰이 유효합니다.')
            return self.tokens['access_token']

        # 리프레시 토큰 유효성 확인
        refresh_token_expires_at = self.is_valid_datetime(self.tokens.get('refresh_token_expires_at'))
        if refresh_token_expires_at and now < refresh_token_expires_at:
            logger.info('리프레시 토큰으로 재발급을 시도합니다.')
            return self.refresh_access_token()
        
        raise Exception('리프레시 토큰도 만료되었습니다. 신규 인증을 진행하세요.')

