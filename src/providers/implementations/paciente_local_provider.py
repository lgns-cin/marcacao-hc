from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from ...models.paciente import Paciente
from ...models.exame import Exame
from ...models.exame_solicitado import ExameSolicitado
from ...models.solicitacao import Solicitacao


class PacientePostgresProviderCompleto():

    def __init__(self, session: AsyncSession):
        self.session = session

    # métodos base

    async def listar_pacientes(self) -> List[Dict[str, Any]]:
        """Retorna todos os pacientes ativos (deleted_at IS NULL)."""
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
        """
        Retorna um paciente pelo prontuário.
        Lança HTTPException 404 se não encontrado ou deletado logicamente.
        """
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

    async def verificar_prontuario_existe(self, numero_prontuario: int) -> bool:
        """
        Verifica se o prontuário existe e está ativo no banco.
        Retorna True se encontrado, False caso contrário.
        """
        result = await self.session.execute(
            select(Paciente).where(
                Paciente.prontuario == numero_prontuario,
                Paciente.deleted_at.is_(None),
            )
        )
        return result.scalars().first() is not None 
    
    # tool 2

    async def verificar_solicitacao_existe(
        self,
        numero_prontuario: int,
        numero_solicitacao: int,
    ) -> bool:
        """
        Verifica se existe ao menos um ExameSolicitado com o código de
        solicitação informado vinculado ao prontuário do paciente.
        Retorna True se encontrado, False caso contrário.
        """
        result = await self.session.execute(
            select(ExameSolicitado).where(
                ExameSolicitado.solicitacao == numero_solicitacao,
                ExameSolicitado.paciente_solicitante == numero_prontuario,
                ExameSolicitado.deleted_at.is_(None),
            )
        )
        return result.scalars().first() is not None 
    
    # tool 3

    async def buscar_exames_solicitacao(
        self,
        numero_prontuario: int,
        numero_solicitacao: int,
    ) -> List[Dict[str, Any]]:
        """
        Retorna a lista completa de exames de uma solicitação vinculada
        ao prontuário, com todos os atributos necessários para o
        algoritmo de priorização.

        Faz JOIN entre ExameSolicitado, Exame e Solicitacao para reunir
        todos os campos. Filtra deleted_at IS NULL nas três tabelas.

        Reutiliza as tools 1 e 2 para validar antes de buscar, lançando
        HTTPException 404 com mensagem específica se alguma falhar.
        """
        if not await self.verificar_prontuario_existe(numero_prontuario):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prontuário não encontrado",
            )
        if not await self.verificar_solicitacao_existe(numero_prontuario, numero_solicitacao):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitação não encontrada para este prontuário",
            )

        result = await self.session.execute(
            select(ExameSolicitado, Exame, Solicitacao)
            .join(Exame, ExameSolicitado.exame == Exame.codigo)
            .join(Solicitacao, ExameSolicitado.solicitacao == Solicitacao.codigo)
            .where(
                ExameSolicitado.solicitacao == numero_solicitacao,
                ExameSolicitado.paciente_solicitante == numero_prontuario,
                ExameSolicitado.deleted_at.is_(None),
                Exame.deleted_at.is_(None),
                Solicitacao.deleted_at.is_(None),
            )
        )
        rows = result.all()
        return [
            {
                # de Exame
                "codigo_exame": exame.codigo,
                "nome_exame": exame.nome,
                # de Solicitacao
                "data_retorno": solicitacao.data_retorno,
                "unidade_solicitante": solicitacao.unidade_solicitante,
                # de ExameSolicitado
                "data_solicitacao": es.data_solicitacao,
                "status_atribuicao": es.status_atribuicao,
                "funcionario_atribuido": es.funcionario_atribuido,
                # calculado
                "tem_vagas": False,  # placeholder até implementar vagas
            }
            for es, exame, solicitacao in rows
        ]