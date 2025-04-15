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
    def __init__(self, config_prefix=None):
        """
        네이버 토큰 매니저 초기화 함수
        """
        if config_prefix is None:
            logger.info('사용할 쇼핑몰을 선택하세요')
            logger.info('1. 49JD')
            logger.info('2. SIASIU')
            logger.info('3. RHINO')
            logger.info('4. RICHCP')
            choice = input('번호를 입력해주세요')
            if choice == '1':
                self.config_prefix = '49JD'
            elif choice == '2':
                self.config_prefix = 'SIASIU'
            elif choice == '3':
                self.config_prefix = 'RHINO'
            elif choice == '4':
                self.config_prefix = 'RICHCP'
            else:
                logger.error('잘못된 번호입니다.')
                exit()
        
        self.timestamp = str(int(time.time() * 1000))
        self.client_id = os.getenv(f'{self.config_prefix}_NAVER_CLIENT_ID')
        self.client_secret = os.getenv(f'{self.config_prefix}_NAVER_CLIENT_SECRET')
        self.client_id_timestamp = self.client_id + "_" + self.timestamp
        self.hashed_info = bcrypt.hashpw(self.client_id_timestamp.encode('utf-8'), self.client_secret.encode('utf-8'))
        self.signature = pybase64.b64encode(self.hashed_info).decode('utf-8')

        logger.info(f'생성된 네이버 토큰 전자서명: {self.signature}')

        self.access_token, self.expires_in = self.get_access_token()


    # 어차피 3시간마다 발급하면 되니까 굳이 재발급 로직은 필요 없을 듯 싶음.
    def get_access_token(self):
        """
        네이버 토큰 엑세스 토큰을 반환하는 함수입니다.
        Returns:
            access_token (str): 네이버 토큰 엑세스 토큰
            expires_in (int): 토큰 만료 시간
        """

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        data = {
            'client_id': self.client_id,
            'timestamp': self.timestamp,
            'client_secret_sign': self.signature,
            'grant_type': 'client_credentials'
        }

        query = urllib.parse.urlencode(data)
        url = f'https://api.commerce.naver.com/external/v1/oauth2/token?{query}'

        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            expires_in = data.get('expires_in')

            logger.info(f'네이버 토큰 발급 성공: {access_token}')
            logger.info(f'토큰 만료 시간: {expires_in}초')

            return access_token, expires_in
        else:
            logger.error(f'네이버 토큰 발급 실패: {response.text}')
            return None, None






