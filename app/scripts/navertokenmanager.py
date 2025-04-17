import time
import requests
import bcrypt
import pybase64
import os
import urllib.parse
from app.utils.logger import mainLogger

logger = mainLogger()

class NaverTokenManager:
    """
    네이버 토큰 매니저 클래스입니다.
    """
    def __init__(self, config_prefix: str):
        """
        네이버 토큰 매니저 초기화 함수
        """
        self.config_prefix = config_prefix
        
        self.timestamp = str(int(time.time() * 1000))
        self.client_id = os.getenv(f'{self.config_prefix}_NAVER_CLIENT_ID')
        self.client_secret = os.getenv(f'{self.config_prefix}_NAVER_CLIENT_SECRET')
        self.client_id_timestamp = self.client_id + "_" + self.timestamp
        self.hashed_info = bcrypt.hashpw(self.client_id_timestamp.encode('utf-8'), self.client_secret.encode('utf-8'))
        self.signature = pybase64.b64encode(self.hashed_info).decode('utf-8')

        logger.info(f'생성된 네이버 토큰 전자서명: {self.signature}')


    # 어차피 3시간마다 발급하면 되니까 굳이 재발급 로직은 필요 없을 듯 싶음.
    def get_access_token(self):
        """
        네이버 토큰 엑세스 토큰을 반환하는 함수입니다.
        Returns:
            access_token (str): 네이버 토큰 엑세스 토큰
            expires_in (int): 토큰 만료 시간
        """

        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Accept': 'application/json'}

        payload = {'client_id': self.client_id,
                   'timestamp': self.timestamp,
                   'client_secret_sign': self.signature,
                   'grant_type': 'client_credentials',
                   'type': 'SELF'}
        
        url = f'https://api.commerce.naver.com/external/v1/oauth2/token'

        response = requests.request('POST', url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            logger.info(f'네이버 토큰 발급 성공: {access_token}')
            return access_token
        else:
            logger.error(f'네이버 토큰 발급 실패: {response.text}')
            return None






