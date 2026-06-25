"""add resultado to exames_solicitados

Revision ID: c4624fd6bdb7
Revises: 27eb6105aafb
Create Date: 2026-06-25 13:10:35.871525

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4624fd6bdb7'
down_revision: Union[str, Sequence[str], None] = '27eb6105aafb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # resultado: registra o desfecho do atendimento — CONFIRMADO ou PROBLEMA_REPORTADO — preenchido ao finalizar
    op.add_column('exames_solicitados', sa.Column('resultado', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('exames_solicitados', 'resultado')
