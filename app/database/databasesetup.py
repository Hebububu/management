from app.utils.logger import mainLogger

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.database.databaseconfig import DatabaseConfig

# 로거 설정
logger = mainLogger()

# 기본 모델 클래스
Base = declarative_base()

# 데이터베이스 셋업
class DatabaseSetup:
    engine = None
    session = None
    
    def __init__(self) -> None:
        """
        데이터베이스 셋업을 초기화하는 메소드입니다.
        """
        try:
            self.engine = create_engine(
                DatabaseConfig.get_connection_str(),
            )
            logger.info('데이터베이스 엔진 생성 완료')
        
        except Exception as e:
            logger.error(f'엔진 생성 실패: {str(e)}')
            raise
            
        try:
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            logger.info('세션 팩토리 생성 완료')

        except Exception as e:
            logger.error(f'세션 생성 실패: {str(e)}')
            raise

    def get_session(self):
        """
        새로운 데이터베이스 세션을 반환합니다.
        """
        return self.SessionLocal()


        