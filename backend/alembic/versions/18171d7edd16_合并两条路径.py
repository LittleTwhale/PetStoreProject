"""合并两条路径

Revision ID: 18171d7edd16
Revises: 57b2e07f760e, a1b2c3d4e5f6
Create Date: 2026-05-26 21:48:48.542241

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '18171d7edd16'
down_revision: Union[str, Sequence[str], None] = ('57b2e07f760e', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
