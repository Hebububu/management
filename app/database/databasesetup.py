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

        # SQLAlchemy 엔진 생성
        if self.engine is None:
            engine = create_engine(DatabaseConfig.get_connection_str(), connect_args={'check_same_thread': False})
            return engine
        
        # 세션 생성
        if self.session is None:
            session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)


        