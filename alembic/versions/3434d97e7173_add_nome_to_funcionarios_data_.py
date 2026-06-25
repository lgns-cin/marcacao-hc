"""add nome to funcionarios, data_nascimento to pacientes, data_conclusao to exames_solicitados

Revision ID: 3434d97e7173
Revises: c4624fd6bdb7
Create Date: 2026-06-25 13:32:13.173954

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3434d97e7173'
down_revision: Union[str, Sequence[str], None] = 'c4624fd6bdb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # data_conclusao: data em que o atendimento foi finalizado pelo funcionário
    op.add_column('exames_solicitados', sa.Column('data_conclusao', sa.Date(), nullable=True))
    # nome: nome de exibição do funcionário vindo do AD, preenchido na primeira ação no sistema
    op.add_column('funcionarios', sa.Column('nome', sa.String(), nullable=True))
    # data_nascimento: necessária para calcular a idade do paciente exibida no card
    op.add_column('pacientes', sa.Column('data_nascimento', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('pacientes', 'data_nascimento')
    op.drop_column('funcionarios', 'nome')
    op.drop_column('exames_solicitados', 'data_conclusao')
