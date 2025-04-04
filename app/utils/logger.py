import logging
import os
from datetime import datetime

class mainLogger:
    """
    로거 메인 클래스입니다.
    """

    def __init__(self) -> None:
        """
        로거 설정
        - 로그 파일 생성
        - 로그 포맷 설정
        - 로거 반환
        """

        # 로그 디렉토리
        log_dir = "data/logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 로그 파일명
        log_file = os.path.join(log_dir, f"management_{datetime.now().strftime('%Y%m%d')}.log")

        # 로거 설정
        self.logger = logging.getLogger('Management')
        self.logger.setLevel(logging.INFO)

        # 파일 핸들러 설정
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 로그 포맷 설정
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 핸들러 추가
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)