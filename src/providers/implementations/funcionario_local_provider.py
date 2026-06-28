from datetime import date
from typing import List, Optional

from sqlalchemy import select, or_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ...models.paciente import Paciente

from ...models.exame_solicitado import ExameSolicitado
from ...models.funcionario import Funcionario
from ...enums import StatusAtribuicao, ResultadoAtribuicao


class FuncionarioLocalProvider:

    def __init__(self, session: AsyncSession):
        self.session = session

    # Busca o funcionário pelo username do AD. Se não existir, cria o registro.
    # Também salva o nome na primeira vez que estiver disponível.
    async def get_or_create_funcionario(self, username: str, nome: Optional[str] = None) -> Funcionario:
        result = await self.session.execute(
            select(Funcionario).where(Funcionario.username == username)
        )
        funcionario = result.scalar_one_or_none()
        if funcionario is None:
            funcionario = Funcionario(username=username, nome=nome, is_administrador=False)
            self.session.add(funcionario)
            await self.session.flush()
        elif nome and not funcionario.nome:
            # Preenche o nome se ainda não tinha sido salvo
            funcionario.nome = nome
            await self.session.flush()
        return funcionario

    # Retorna todos os exames sem funcionário atribuído e com status PENDENTE
    # Carrega paciente, solicitação e exame junto para evitar queries extras no controller
    async def listar_pendentes(self, busca: Optional[str] = None) -> List[ExameSolicitado]:
        stmt = (
            select(ExameSolicitado)
            .options(
                selectinload(ExameSolicitado.paciente),
                selectinload(ExameSolicitado.solicitacao_rel),
                selectinload(ExameSolicitado.exame_rel),
            )
        )

        conditions = [
            ExameSolicitado.funcionario_atribuido == None,
            ExameSolicitado.status_atribuicao == StatusAtribuicao.PENDENTE,
            ExameSolicitado.deleted_at == None,
        ]

        if busca:
            stmt = stmt.join(ExameSolicitado.paciente)
            busca_str = f"%{busca}%"
            conditions.append(
                or_(
                    Paciente.nome.ilike(busca_str),
                    cast(Paciente.prontuario, String).ilike(busca_str)
                )
            )

        stmt = stmt.where(*conditions)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # Retorna todos os exames atribuídos ao funcionário, em qualquer status
    async def listar_por_funcionario(self, funcionario_id: int) -> List[ExameSolicitado]:
        stmt = (
            select(ExameSolicitado)
            .options(
                selectinload(ExameSolicitado.paciente),
                selectinload(ExameSolicitado.solicitacao_rel),
                selectinload(ExameSolicitado.exame_rel),
            )
            .where(
                ExameSolicitado.funcionario_atribuido == funcionario_id,
                ExameSolicitado.deleted_at == None,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # Busca exames de uma solicitação com filtros opcionais de funcionário e status
    async def buscar_por_solicitacao(
        self,
        solicitacao_id: int,
        funcionario_id: Optional[int] = None,
        status: Optional[StatusAtribuicao] = None,
    ) -> List[ExameSolicitado]:
        conditions = [
            ExameSolicitado.solicitacao == solicitacao_id,
            ExameSolicitado.deleted_at == None,
        ]
        if funcionario_id is not None:
            conditions.append(ExameSolicitado.funcionario_atribuido == funcionario_id)
        if status is not None:
            conditions.append(ExameSolicitado.status_atribuicao == status)

        result = await self.session.execute(
            select(ExameSolicitado).where(*conditions)
        )
        return result.scalars().all()

    # Vincula os exames ao funcionário e marca como EM_ANDAMENTO
    async def atribuir(self, rows: List[ExameSolicitado], funcionario_id: int) -> None:
        for row in rows:
            row.funcionario_atribuido = funcionario_id
            row.status_atribuicao = StatusAtribuicao.EM_ANDAMENTO
            row.data_atribuicao = date.today()
        await self.session.commit()

    # Muda o status dos exames e opcionalmente salva resultado, motivo e detalhes
    async def transicionar_status(
        self,
        rows: List[ExameSolicitado],
        novo_status: StatusAtribuicao,
        resultado: Optional[ResultadoAtribuicao] = None,
        motivo: Optional[str] = None,
        detalhes: Optional[str] = None,
    ) -> None:
        for row in rows:
            row.status_atribuicao = novo_status
            row.data_atribuicao = date.today()
            if novo_status == StatusAtribuicao.FINALIZADO:
                row.data_conclusao = date.today()
            if resultado is not None:
                row.resultado = resultado
            if motivo is not None:
                row.motivo = motivo
            if detalhes is not None:
                row.detalhes = detalhes
        await self.session.commit()

    # Remove a atribuição do funcionário e devolve o exame para a fila com status PENDENTE
    async def devolver(self, rows: List[ExameSolicitado], motivo: str) -> None:
        for row in rows:
            row.funcionario_atribuido = None
            row.status_atribuicao = StatusAtribuicao.PENDENTE
            row.data_atribuicao = None
            row.motivo = motivo
        await self.session.commit()
