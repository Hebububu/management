"""first migration

Revision ID: 30e699fe3b88
Revises: 
Create Date: 2025-04-09 14:08:42.416378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30e699fe3b88'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('crawled_data',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('product_name', sa.TEXT(), nullable=False),
    sa.Column('title', sa.TEXT(), nullable=False),
    sa.Column('url', sa.TEXT(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('discount_price', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ob_history',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('platform', sa.TEXT(), nullable=False),
    sa.Column('seller_id', sa.TEXT(), nullable=False),
    sa.Column('product_id', sa.TEXT(), nullable=False),
    sa.Column('compnay', sa.TEXT(), nullable=False),
    sa.Column('product_name', sa.TEXT(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('category', sa.TEXT(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('platform', sa.TEXT(), nullable=False),
    sa.Column('seller_id', sa.TEXT(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('company', sa.TEXT(), nullable=False),
    sa.Column('sale_name', sa.TEXT(), nullable=False),
    sa.Column('product_name', sa.TEXT(), nullable=False),
    sa.Column('data', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('platform', 'seller_id', 'company', 'product_name', name='uq_product')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.TEXT(), nullable=False),
    sa.Column('email', sa.TEXT(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crawled_data_coupon',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('crawled_data_id', sa.Integer(), nullable=False),
    sa.Column('is_available', sa.BOOLEAN(), nullable=False),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('discount_price', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['crawled_data_id'], ['crawled_data.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crawled_data_point',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('crawled_data_id', sa.Integer(), nullable=False),
    sa.Column('text_point', sa.Integer(), nullable=False),
    sa.Column('photo_point', sa.Integer(), nullable=False),
    sa.Column('month_text_point', sa.Integer(), nullable=False),
    sa.Column('month_photo_point', sa.Integer(), nullable=False),
    sa.Column('notification_point', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['crawled_data_id'], ['crawled_data.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crawled_data_shipping',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('crawled_data_id', sa.Integer(), nullable=False),
    sa.Column('fee', sa.Integer(), nullable=False),
    sa.Column('company', sa.TEXT(), nullable=False),
    sa.Column('condition', sa.TEXT(), nullable=False),
    sa.Column('free_condition_amount', sa.Integer(), nullable=False),
    sa.Column('jeju_fee', sa.Integer(), nullable=False),
    sa.Column('island_fee', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['crawled_data_id'], ['crawled_data.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('log',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.TEXT(), nullable=False),
    sa.Column('source', sa.TEXT(), nullable=False),
    sa.Column('message', sa.TEXT(), nullable=False),
    sa.Column('ip_address', sa.TEXT(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('margin',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('platform', sa.TEXT(), nullable=False),
    sa.Column('seller_id', sa.TEXT(), nullable=False),
    sa.Column('company', sa.TEXT(), nullable=False),
    sa.Column('product_name', sa.TEXT(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('cost', sa.Integer(), nullable=False),
    sa.Column('marketplace_charge', sa.FLOAT(), nullable=False),
    sa.Column('margin', sa.Integer(), nullable=False),
    sa.Column('margin_rate', sa.Integer(), nullable=False),
    sa.Column('gift', sa.Integer(), nullable=False),
    sa.Column('delivery_fee', sa.Integer(), nullable=False),
    sa.Column('post_fee', sa.Integer(), nullable=False),
    sa.Column('category', sa.TEXT(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['platform', 'seller_id', 'company', 'product_name'], ['product.platform', 'product.seller_id', 'product.company', 'product.product_name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ob',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('history_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['history_id'], ['ob_history.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ob')
    op.drop_table('margin')
    op.drop_table('log')
    op.drop_table('crawled_data_shipping')
    op.drop_table('crawled_data_point')
    op.drop_table('crawled_data_coupon')
    op.drop_table('user')
    op.drop_table('product')
    op.drop_table('ob_history')
    op.drop_table('crawled_data')
    # ### end Alembic commands ###
