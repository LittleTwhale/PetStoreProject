"""移除库存分类的store_id字段，使分类对所有门店通用

Revision ID: a1b2c3d4e5f6
Revises: 8d85e8226903
Create Date: 2026-05-26 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '8d85e8226903'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """移除 inventory_categories 表的 store_id 列（使分类全局通用）"""
    with op.batch_alter_table('inventory_categories') as batch_op:
        # 1. 先删除外键约束
        batch_op.drop_constraint('inventory_categories_ibfk_1', type_='foreignkey')
        # 2. 再删除 store_id 列
        batch_op.drop_column('store_id')


def downgrade() -> None:
    """恢复 inventory_categories 表的 store_id 列"""
    with op.batch_alter_table('inventory_categories') as batch_op:
        # 1. 恢复列
        batch_op.add_column(
            sa.Column('store_id', sa.Integer(), nullable=True, comment='所属门店')
        )
        # 2. 恢复外键约束
        batch_op.create_foreign_key(
            'inventory_categories_ibfk_1',
            'stores',
            ['store_id'],
            ['id'],
            ondelete='CASCADE'
        )