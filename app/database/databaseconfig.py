import os
from dotenv import load_dotenv
from app.utils.logger import mainLogger

# 환경 변수 로드
load_dotenv()

# 로거 설정
logger = mainLogger()

# 데이터베이스 설정
class DatabaseConfig:
    """
    기본 데이터베이스 설정 클래스입니다.
    """
    instance = None

    # PGSQL 설정
    PG_HOST = os.getenv("PG_HOST")
    PG_PORT = os.getenv("PG_PORT")
    PG_DB = os.getenv("PG_DB")
    PG_USER = os.getenv("PG_USER")
    PG_PASSWORD = os.getenv("PG_PASSWORD")

    @classmethod
    def get_connection_str(cls):
        """
        SQLAlchemy 연결용 문자열을 생성하는 메소드입니다.
            Returns: pgsql 연결 문자열
        """
        return f"postgresql+psycopg2://{cls.PG_USER}:{cls.PG_PASSWORD}@{cls.PG_HOST}:{cls.PG_PORT}/{cls.PG_DB}"
    
    @classmethod
    def initialize(cls):
        """
        데이터베이스 설정 초기화 메소드입니다.
        """
        if cls.instance is None:
            # PostgreSQL 연결 정보 로깅
            logger.info(f'PostgreSQL 연결 정보 - 호스트: {cls.PG_HOST}, 포트: {cls.PG_PORT}, DB: {cls.PG_DB}')
            logger.info(f'연결 문자열: {cls.get_connection_str()}')
            cls.instance = True
            logger.info('PostgreSQL 데이터베이스 설정이 초기화되었습니다.')