"""add responsavel_username to exames_solicitados

Revision ID: 1e2e72bf23a3
Revises: e32148cd34a9
Create Date: 2026-06-25 12:19:22.396532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e2e72bf23a3'
down_revision: Union[str, Sequence[str], None] = 'e32148cd34a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('exames_solicitados', sa.Column('responsavel_username', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('exames_solicitados', 'responsavel_username')
