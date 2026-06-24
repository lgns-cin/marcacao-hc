from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from ..interfaces.paciente_provider_interface import PacienteProviderInterface
from ...models.paciente import Paciente
from ...models.exame import Exame
from ...models.exame_solicitado import ExameSolicitado


class PacientePostgresProvider(PacienteProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    # métodos base

    async def listar_pacientes(self) -> List[Dict[str, Any]]:
        result = await self.session.execute(
            select(Paciente).where(Paciente.deleted_at.is_(None))
        )
        pacientes = result.scalars().all()
        return [
            {
                "prontuario": p.prontuario,
                "telefone": p.telefone,
                "cidade": p.cidade,
                "estado": p.estado,
            }
            for p in pacientes
        ]

    async def obter_paciente_por_codigo(self, codigo: int) -> Dict[str, Any]:
        result = await self.session.execute(
            select(Paciente).where(
                Paciente.prontuario == codigo,
                Paciente.deleted_at.is_(None),
            )
        )
        paciente = result.scalars().first()
        if not paciente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente não encontrado",
            )
        return {
            "prontuario": paciente.prontuario,
            "telefone": paciente.telefone,
            "cidade": paciente.cidade,
            "estado": paciente.estado,
        }

    # tool 1

    async def verificar_prontuario(self, prontuario: int) -> bool:
        result = await self.session.execute(
            select(Paciente).where(
                Paciente.prontuario == prontuario,
                Paciente.deleted_at.is_(None),
            )
        )
        return result.scalars().first() is not None

    # tool 2

    async def verificar_solicitacao(
        self, codigo_solicitacao: int, prontuario: int
    ) -> bool:
        result = await self.session.execute(
            select(ExameSolicitado).where(
                ExameSolicitado.solicitacao == codigo_solicitacao,
                ExameSolicitado.paciente_solicitante == prontuario,
                ExameSolicitado.deleted_at.is_(None),
            )
        )
        return result.scalars().first() is not None

    # tool 3

    async def obter_exames_por_solicitacao(
        self, codigo_solicitacao: int, prontuario: int
    ) -> List[Dict[str, Any]]:
        if not await self.verificar_prontuario(prontuario):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prontuário não encontrado",
            )
        if not await self.verificar_solicitacao(codigo_solicitacao, prontuario):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitação não encontrada para este prontuário",
            )

        result = await self.session.execute(
            select(ExameSolicitado, Exame)
            .join(Exame, ExameSolicitado.exame == Exame.codigo)
            .where(
                ExameSolicitado.solicitacao == codigo_solicitacao,
                ExameSolicitado.paciente_solicitante == prontuario,
                ExameSolicitado.deleted_at.is_(None),
                Exame.deleted_at.is_(None),
            )
        )
        rows = result.all()
        return [
            {
                "codigo_exame": exame.codigo,
                "nome_exame": exame.nome,
                "status_atribuicao": es.status_atribuicao,
                "funcionario_atribuido": es.funcionario_atribuido,
            }
            for es, exame in rows
        ]