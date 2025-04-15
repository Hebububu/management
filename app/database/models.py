from sqlalchemy import ForeignKey, Column, Integer, TEXT, TIMESTAMP, JSON, BOOLEAN, FLOAT, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
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
    category = Column(TEXT, nullable=True)
    company = Column(TEXT, nullable=True)
    sale_name = Column(TEXT, nullable=False)
    product_name = Column(TEXT, nullable=True)
    tags = Column(TEXT, nullable=True)
    data = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)

    margin = relationship('Margin', back_populates='product', uselist=False)

    __table_args__ = (UniqueConstraint(
        'platform',
        'seller_id',
        'company',
        'category',
        'product_name',
        'tags',
        name='uq_product'
        ),
    )

class Margin(Base):
    """
    마진 SQLAlchemy 모델입니다.
    """
    __tablename__ = "margin"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    platform = Column(TEXT, nullable=False) # 외부 키
    seller_id = Column(TEXT, nullable=False) # 외부 키
    company = Column(TEXT, nullable=False) # 외부 키
    product_name = Column(TEXT, nullable=False) # 외부 키 
    price = Column(Integer, nullable=False)
    cost = Column(Integer, nullable=False)
    marketplace_charge = Column(FLOAT, nullable=False)
    margin = Column(Integer, nullable=False)
    margin_rate = Column(Integer, nullable=False)
    gift = Column(Integer, nullable=False)
    delivery_fee = Column(Integer, nullable=False)
    post_fee = Column(Integer, nullable=False)
    category = Column(TEXT, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ['platform','seller_id','company','product_name','category'],
            ['product.platform','product.seller_id','product.company','product.product_name','product.category'],
            name='fk_margin_product'
        ),
    )

    product = relationship('Product', back_populates='margin', uselist=False)

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

    logs = relationship("Log", back_populates='user')

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

    __table_args__ = (
        ForeignKeyConstraint(
            ['user_id'],
            ['user.id'],
            name='fk_log_user'
        ),
    )
    user = relationship('User', back_populates='logs')

class Ob(Base):
    """
    출고 SQLAlchemy 모델입니다.
    """
    __tablename__ = 'ob'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    history_id = Column(Integer, ForeignKey('ob_history.id', name='fk_ob_history'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)

    history = relationship('ObHistory', back_populates='ob')

class ObHistory(Base):
    """
    출고 기록 SQLAlchemy 모델입니다.
    """
    __tablename__ = 'ob_history'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    platform = Column(TEXT, nullable=False)
    seller_id = Column(TEXT, nullable=False)
    product_id = Column(TEXT, nullable=False)
    compnay = Column(TEXT, nullable=False)
    product_name = Column(TEXT, nullable=False) 
    price = Column(Integer, nullable=False)
    category = Column(TEXT, nullable=False)
    amount = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)

    ob = relationship('Ob', back_populates='history')

class CrawledData(Base):
    """
    크롤링 데이터 SQLAlchemy 모델입니다.
    """
    __tablename__ = 'crawled_data'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    product_name = Column(TEXT, nullable=False)
    title = Column(TEXT, nullable=False)
    url = Column(TEXT, nullable=False)
    price = Column(Integer, nullable=False)
    discount_price = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)

    coupon = relationship('CrawledDataCoupon', back_populates='crawled_data', uselist=False)
    shipping = relationship('CrawledDataShipping', back_populates='crawled_data', uselist=False)
    point = relationship('CrawledDataPoint', back_populates='crawled_data', uselist=False)

class CrawledDataCoupon(Base):
    """
    크롤링 쿠폰 데이터 SQLAlchemy 모델입니다.
    """
    __tablename__ = 'crawled_data_coupon'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    crawled_data_id = Column(Integer, ForeignKey('crawled_data.id', name='fk_crawled_data_coupon'), nullable=False)
    is_available = Column(BOOLEAN, nullable=False)
    description = Column(TEXT, nullable=True)
    discount_price = Column(Integer, nullable=False) # 기본값 0 넣으면 될듯?

    crawled_data = relationship('CrawledData', back_populates='coupon', uselist=False)

class CrawledDataShipping(Base):
    """
    크롤링 배송비 데이터 SQLAlchemy 모델입니다.
    """
    __tablename__ = 'crawled_data_shipping'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    crawled_data_id = Column(Integer, ForeignKey('crawled_data.id', name='fk_crawled_data_shipping'), nullable=False) # 외부 키
    fee = Column(Integer, nullable=False) # 기본값 0 넣으면 될듯?
    company = Column(TEXT, nullable=False) # 기본값 없음 넣으면 될듯?
    condition = Column(TEXT, nullable=False)
    free_condition_amount = Column(Integer, nullable=False) # 기본값 0 넣으면 될듯?
    jeju_fee = Column(Integer, nullable=False) # 기본값 0 넣으면 될듯?
    island_fee = Column(Integer, nullable=False) # 기본값 0 넣으면 될듯?

    crawled_data = relationship('CrawledData', back_populates='shipping', uselist=False)

class CrawledDataPoint(Base):
    """
    크롤링 포인트 데이터 SQLAlchemy 모델입니다.
    """
    __tablename__ = 'crawled_data_point'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    crawled_data_id = Column(Integer, ForeignKey('crawled_data.id', name='fk_crawled_data_point'), nullable=False) # 외부 키
    text_point = Column(Integer, nullable=False) # 기본값
    photo_point = Column(Integer, nullable=False) # 기본값
    month_text_point = Column(Integer, nullable=False) # 기본값
    month_photo_point = Column(Integer, nullable=False) # 기본값
    notification_point = Column(Integer, nullable=False) # 기본값

    crawled_data = relationship('CrawledData', back_populates='point', uselist=False)


