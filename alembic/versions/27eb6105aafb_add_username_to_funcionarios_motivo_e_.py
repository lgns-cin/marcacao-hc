"""add username to funcionarios, motivo e detalhes to exames_solicitados

Revision ID: 27eb6105aafb
Revises: e32148cd34a9
Create Date: 2026-06-25 12:49:01.100908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27eb6105aafb'
down_revision: Union[str, Sequence[str], None] = 'e32148cd34a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # motivo: texto obrigatório nos endpoints /devolver e /reportar-problema
    op.add_column('exames_solicitados', sa.Column('motivo', sa.String(), nullable=True))
    # detalhes: campo opcional adicional no endpoint /reportar-problema
    op.add_column('exames_solicitados', sa.Column('detalhes', sa.String(), nullable=True))
    # username: login do AD do funcionário — chave que liga o JWT ao registro no banco
    op.add_column('funcionarios', sa.Column('username', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('funcionarios', 'username')
    op.drop_column('exames_solicitados', 'detalhes')
    op.drop_column('exames_solicitados', 'motivo')
