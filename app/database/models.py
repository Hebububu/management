from sqlalchemy import Column, Integer, TEXT, TIMESTAMP, JSON, BOOLEAN
from app.database.databasesetup import Base

class Product(Base):
    """
    제품 SQLAlchemy 모델입니다.
    """
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    platform = Column(TEXT, nullable=False)
    seller_id = Column(TEXT, nullable=False)
    product_id = Column(Integer, nullable=False)
    sale_name = Column(TEXT, nullable=False)
    product_name = Column(TEXT, nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)

class Margin(Base):
    """
    마진 SQLAlchemy 모델입니다.
    """
    __tablename__ = "margin"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    platform = Column(TEXT, nullable=False) # 외부 키
    seller_id = Column(TEXT, nullable=False) # 외부 키
    product_name = Column(TEXT, nullable=False) # 외부 키 
    price = Column(Integer, nullable=False)
    cost = Column(Integer, nullable=False)
    category = Column(TEXT, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)

class User(Base):
    """
    사용자 SQLAlchemy 모델입니다.
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(TEXT, nullable=False)
    email = Column(TEXT, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)

class Log(Base):
    """
    로그 SQLAlchemy 모델입니다.
    """
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, nullable=False) # 외부 키
    type = Column(TEXT, nullable=False)
    source = Column(TEXT, nullable=False)
    message = Column(TEXT, nullable=False)
    ip_address = Column(TEXT, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)

class Ob(Base):
    """
    출고 SQLAlchemy 모델입니다.
    """
    __tablename__ = 'ob'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    history_id = Column(Integer, nullable=False, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)

class ObHistory(Base):
    """
    출고 기록 SQLAlchemy 모델입니다.
    """
    __tablename__ = 'ob_history'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    platform = Column(TEXT, nullable=False)
    seller_id = Column(TEXT, nullable=False)
    product_id = Column(TEXT, nullable=False)
    product_name = Column(TEXT, nullable=False) 
    price = Column(Integer, nullable=False)
    category = Column(TEXT, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)

class CrawledData(Base):
    """
    크롤링 데이터 SQLAlchemy 모델입니다.
    """
    __tablename__ = 'crawled_data'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    product_name = Column(TEXT, nullable=False) # 외부 키
    title = Column(TEXT, nullable=False)
    url = Column(TEXT, nullable=False)
    price = Column(Integer, nullable=False)
    discount_price = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)

class CrawledDataCoupon(Base):
    """
    크롤링 쿠폰 데이터 SQLAlchemy 모델입니다.
    """
    __tablename__ = 'crawled_data_coupon'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    crawled_data_id = Column(Integer, nullable=False) # 외부 키
    is_available = Column(BOOLEAN, nullable=False)
    description = Column(TEXT, nullable=True)
    discount_price = Column(Integer, nullable=False) # 기본값 0 넣으면 될듯?

class CrawledDataShipping(Base):
    """
    크롤링 배송비 데이터 SQLAlchemy 모델입니다.
    """
    __tablename__ = 'crawled_data_shipping'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    crawled_data_id = Column(Integer, nullable=False) # 외부 키
    fee = Column(Integer, nullable=False) # 기본값 0 넣으면 될듯?
    company = Column(TEXT, nullable=False) # 기본값 없음 넣으면 될듯?
    condition = Column(TEXT, nullable=False)
    free_condition_amount = Column(Integer, nullable=False) # 기본값 0 넣으면 될듯?
    jeju_fee = Column(Integer, nullable=False) # 기본값 0 넣으면 될듯?
    island_fee = Column(Integer, nullable=False) # 기본값 0 넣으면 될듯?

class CrawledDataPoint(Base):
    """
    크롤링 포인트 데이터 SQLAlchemy 모델입니다.
    """
    __tablename__ = 'crawled_data_point'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    crawled_data_id = Column(Integer, nullable=False) # 외부 키
    text_point = Column(Integer, nullable=False) # 기본값
    photo_point = Column(Integer, nullable=False) # 기본값
    month_text_point = Column(Integer, nullable=False) # 기본값
    month_photo_point = Column(Integer, nullable=False) # 기본값
    notification_point = Column(Integer, nullable=False) # 기본값


