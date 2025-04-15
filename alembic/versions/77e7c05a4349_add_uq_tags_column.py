"""add uq tags column

Revision ID: 77e7c05a4349
Revises: 03eb5917cd2b
Create Date: 2025-04-15 14:19:39.299116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77e7c05a4349'
down_revision: Union[str, None] = '03eb5917cd2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 직접 SQL 구문을 사용하여 cascade 옵션과 함께 제약 조건 삭제
    op.execute("ALTER TABLE product DROP CONSTRAINT uq_product CASCADE")
    op.create_unique_constraint('uq_product', 'product', ['platform', 'seller_id', 'company', 'category', 'product_name', 'tags'])


def downgrade() -> None:
    """Downgrade schema."""
    # 직접 SQL 구문을 사용하여 cascade 옵션과 함께 제약 조건 삭제
    op.execute("ALTER TABLE product DROP CONSTRAINT uq_product CASCADE")
    op.create_unique_constraint('uq_product', 'product', ['platform', 'seller_id', 'company', 'category', 'product_name'])