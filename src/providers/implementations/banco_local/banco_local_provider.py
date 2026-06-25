from datetime import date
from typing import Any, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ....models.paciente import Paciente
from ....models.solicitacao import Solicitacao
from ....models.exame import Exame
from ....models.exame_solicitado import ExameSolicitado


class BancoLocalPostgresProvider():

    def __init__(self, session: AsyncSession):
        self.session = session

    # leitura

    async def verificar_exame_na_fila(
        self,
        codigo_exame: str,
        numero_prontuario: int,
        numero_solicitacao: int,
    ) -> bool:
        """
        Verifica se o ExameSolicitado já existe no banco local para
        aquela combinação de prontuário, solicitação e exame.
        """
        result = await self.session.execute(
            select(ExameSolicitado).where(
                ExameSolicitado.exame == codigo_exame,
                ExameSolicitado.paciente_solicitante == numero_prontuario,
                ExameSolicitado.solicitacao == numero_solicitacao,
                ExameSolicitado.deleted_at.is_(None),
            )
        )
        return result.scalars().first() is not None

    async def listar_fila_geral(self) -> List[Dict[str, Any]]:
        """
        Retorna todos os exames com status PENDENTE do banco local

        Faz JOIN entre ExameSolicitado, Exame, Solicitacao e Paciente.
        """
        result = await self.session.execute(
            select(ExameSolicitado, Exame, Solicitacao, Paciente)
            .join(Exame, ExameSolicitado.exame == Exame.codigo)
            .join(Solicitacao, ExameSolicitado.solicitacao == Solicitacao.codigo)
            .join(Paciente, ExameSolicitado.paciente_solicitante == Paciente.prontuario)
            .where(
                ExameSolicitado.status_atribuicao == "PENDENTE",
                ExameSolicitado.deleted_at.is_(None),
                Exame.deleted_at.is_(None),
                Solicitacao.deleted_at.is_(None),
                Paciente.deleted_at.is_(None),
            )
        )
        rows = result.all()
        return [
            {
                # de ExameSolicitado
                "id": es.id,
                "data_solicitacao": es.data_solicitacao,
                "status_atribuicao": es.status_atribuicao,
                "funcionario_atribuido": es.funcionario_atribuido,
                # de Exame
                "codigo_exame": exame.codigo,
                "nome_exame": exame.nome,
                # de Solicitacao
                "numero_solicitacao": solicitacao.codigo,
                "data_retorno": solicitacao.data_retorno,
                "unidade_solicitante": solicitacao.unidade_solicitante,
                # de Paciente
                "numero_prontuario": paciente.prontuario,
                "cidade": paciente.cidade,
            }
            for es, exame, solicitacao, paciente in rows
        ]

    # escrita

    async def salvar_paciente(
        self,
        numero_prontuario: int,
        telefone: str,
        estado: str,
        cidade: str,
    ) -> None:
        """
        Upsert de paciente: atualiza se já existe, insere se não existe.
        """
        result = await self.session.execute(
            select(Paciente).where(Paciente.prontuario == numero_prontuario)
        )
        paciente = result.scalars().first()

        if paciente:
            paciente.telefone = telefone
            paciente.estado = estado
            paciente.cidade = cidade
        else:
            paciente = Paciente(
                prontuario=numero_prontuario,
                telefone=telefone,
                estado=estado,
                cidade=cidade,
                data_nascimento=None,
            )
            self.session.add(paciente)

        await self.session.flush()

    async def salvar_solicitacao(
        self,
        numero_solicitacao: int,
        data_retorno: Any,
        unidade_solicitante: str,
    ) -> None:
        """
        Insert de solicitação apenas se ainda não existir no banco local.
        """
        result = await self.session.execute(
            select(Solicitacao).where(Solicitacao.codigo == numero_solicitacao)
        )
        solicitacao = result.scalars().first()

        if not solicitacao:
            solicitacao = Solicitacao(
                codigo=numero_solicitacao,
                data_retorno=data_retorno,
                unidade_solicitante=unidade_solicitante,
            )
            self.session.add(solicitacao)

        await self.session.flush()

    async def salvar_exame(
        self,
        codigo_exame: str,
        nome_exame: str,
    ) -> None:
        """
        Insert de exame apenas se ainda não existir no banco local.
        """
        result = await self.session.execute(
            select(Exame).where(Exame.codigo == codigo_exame)
        )
        exame = result.scalars().first()

        if not exame:
            exame = Exame(
                codigo=codigo_exame,
                nome=nome_exame,
            )
            self.session.add(exame)

        await self.session.flush()

    async def salvar_exame_solicitado(
        self,
        numero_prontuario: int,
        numero_solicitacao: int,
        codigo_exame: str,
    ) -> None:
        """
        Insert de ExameSolicitado apenas se ainda não existir para
        essa combinação de prontuário, solicitação e exame.
        """
        result = await self.session.execute(
            select(ExameSolicitado).where(
                ExameSolicitado.exame == codigo_exame,
                ExameSolicitado.paciente_solicitante == numero_prontuario,
                ExameSolicitado.solicitacao == numero_solicitacao,
                ExameSolicitado.deleted_at.is_(None),
            )
        )
        exame_solicitado = result.scalars().first()

        if not exame_solicitado:
            exame_solicitado = ExameSolicitado(
                solicitacao=numero_solicitacao,
                exame=codigo_exame,
                paciente_solicitante=numero_prontuario,
                funcionario_atribuido=None,
                status_atribuicao="PENDENTE",
                data_atribuicao=None,
                data_solicitacao=date.today(),
                motivo=None,
                deleted_at=None,
                detalhes=None, 
                resultado=None,
                data_conclusao=None,
            )
            self.session.add(exame_solicitado)

        await self.session.flush()