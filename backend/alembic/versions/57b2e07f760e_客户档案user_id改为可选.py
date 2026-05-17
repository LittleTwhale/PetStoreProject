"""客户档案user_id改为可选

Revision ID: 57b2e07f760e
Revises: 518374ae002d
Create Date: 2026-05-17 21:56:45.944156

变更说明：
  - 将 customer_profiles.user_id 改为允许为空（NULL），以便创建无账户的顾客档案
  - 将外键删除策略从 CASCADE 改为 SET NULL（删除用户时保留客户档案）

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57b2e07f760e'
down_revision: Union[str, Sequence[str], None] = '518374ae002d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _get_fk_name(conn, table: str, column: str) -> str | None:
    """查询指定列上的外键约束名"""
    result = conn.execute(sa.text("""
        SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = :table
          AND COLUMN_NAME = :column
          AND REFERENCED_TABLE_NAME IS NOT NULL
    """), {"table": table, "column": column})
    return result.scalar()


def _drop_fk_if_exists(conn, table: str, column: str):
    """动态查找并删除指定列上的外键约束"""
    fk_name = _get_fk_name(conn, table, column)
    if fk_name:
        conn.execute(sa.text(f"ALTER TABLE {table} DROP FOREIGN KEY {fk_name}"))


def upgrade() -> None:
    """升级：将 user_id 改为可选，外键改为 SET NULL"""
    conn = op.get_bind()

    # 1. 删除旧的 CASCADE 外键约束
    _drop_fk_if_exists(conn, 'customer_profiles', 'user_id')

    # 2. 修改列：允许为空
    op.alter_column('customer_profiles', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=True,
                    comment='关联基础用户（可选，未注册顾客可为空）')

    # 3. 重新添加外键，删除策略改为 SET NULL
    op.create_foreign_key(
        None,  # 约束名由数据库自动生成
        'customer_profiles',
        'users',
        ['user_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """降级：恢复 user_id 为必填，外键改回 CASCADE"""
    conn = op.get_bind()

    # 1. 删除当前的 SET NULL 外键约束
    _drop_fk_if_exists(conn, 'customer_profiles', 'user_id')

    # 2. 将 NULL 值设为 0 以避免 NOT NULL 冲突（生产环境无此数据，防御性处理）
    op.execute("UPDATE customer_profiles SET user_id = 0 WHERE user_id IS NULL")

    # 3. 恢复列：不允许为空
    op.alter_column('customer_profiles', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=False,
                    comment='关联基础用户')

    # 4. 重新添加外键，删除策略改回 CASCADE
    op.create_foreign_key(
        None,
        'customer_profiles',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )
