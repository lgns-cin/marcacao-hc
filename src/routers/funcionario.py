from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.auth import auth_handler
from ..resources.database import get_app_db_session
from ..controllers import funcionario_controller
from ..providers.implementations.funcionario_local_provider import FuncionarioLocalProvider

router = APIRouter(prefix="/api/funcionario", tags=["Funcionario"])


def get_funcionario_provider(db: AsyncSession = Depends(get_app_db_session)) -> FuncionarioLocalProvider:
    return FuncionarioLocalProvider(db)


def _extrair_nome(current_user: dict) -> Optional[str]:
    display_name = current_user.get("displayName")
    if isinstance(display_name, list) and display_name:
        return display_name[0]
    if isinstance(display_name, str):
        return display_name
    return None


class DevolverRequest(BaseModel):
    motivo: str


class ReportarProblemaRequest(BaseModel):
    motivo: str
    detalhes: Optional[str] = None


class FinalizarRequest(BaseModel):
    resultado: str


# Retorna todos os agendamentos com status PENDENTE, ou seja, ainda não assumidos por nenhum funcionário
# Parâmetro opcional ?limit=N para limitar a quantidade retornada
@router.get("/agendamentos")
async def listar_agendamentos(
    limit: Optional[int] = None,
    busca: Optional[str] = None,
    provider: FuncionarioLocalProvider = Depends(get_funcionario_provider),
    current_user: dict = Depends(auth_handler.decode_token),
):
    return await funcionario_controller.listar_agendamentos(provider, limit, busca=busca)


# Atribui um agendamento da fila ao funcionário logado, mudando o status para EM_ANDAMENTO
@router.post("/agendamentos/{solicitacao_id}/puxar")
async def puxar_agendamento(
    solicitacao_id: int,
    provider: FuncionarioLocalProvider = Depends(get_funcionario_provider),
    current_user: dict = Depends(auth_handler.decode_token),
):
    nome = _extrair_nome(current_user)
    return await funcionario_controller.puxar_agendamento(solicitacao_id, provider, current_user.get("sub"), nome)


# Retorna todos os agendamentos sob responsabilidade do funcionário logado, em qualquer estado
@router.get("/minha-area")
async def listar_minha_area(
    provider: FuncionarioLocalProvider = Depends(get_funcionario_provider),
    current_user: dict = Depends(auth_handler.decode_token),
):
    nome = _extrair_nome(current_user)
    return await funcionario_controller.listar_minha_area(provider, current_user.get("sub"), nome)


# Avança o agendamento de EM_ANDAMENTO para AGUARDANDO_CONFIRMACAO, indicando que o agendamento foi feito
@router.post("/minha-area/{solicitacao_id}/aguardar-confirmacao")
async def aguardar_confirmacao(
    solicitacao_id: int,
    provider: FuncionarioLocalProvider = Depends(get_funcionario_provider),
    current_user: dict = Depends(auth_handler.decode_token),
):
    nome = _extrair_nome(current_user)
    return await funcionario_controller.aguardar_confirmacao(solicitacao_id, provider, current_user.get("sub"), nome)


# Devolve o agendamento para a fila geral, tornando-o disponível para outro funcionário
@router.post("/minha-area/{solicitacao_id}/devolver")
async def devolver(
    solicitacao_id: int,
    body: DevolverRequest,
    provider: FuncionarioLocalProvider = Depends(get_funcionario_provider),
    current_user: dict = Depends(auth_handler.decode_token),
):
    nome = _extrair_nome(current_user)
    return await funcionario_controller.devolver(solicitacao_id, body.motivo, provider, current_user.get("sub"), nome)


# Finaliza o agendamento com PROBLEMA_REPORTADO, passando a responsabilidade para o administrador
@router.post("/minha-area/{solicitacao_id}/reportar-problema")
async def reportar_problema(
    solicitacao_id: int,
    body: ReportarProblemaRequest,
    provider: FuncionarioLocalProvider = Depends(get_funcionario_provider),
    current_user: dict = Depends(auth_handler.decode_token),
):
    nome = _extrair_nome(current_user)
    return await funcionario_controller.reportar_problema(solicitacao_id, body.motivo, body.detalhes, provider, current_user.get("sub"), nome)


# Encerra o ciclo do atendimento com resultado CONFIRMADO ou PROBLEMA_REPORTADO
@router.post("/minha-area/{solicitacao_id}/finalizar")
async def finalizar(
    solicitacao_id: int,
    body: FinalizarRequest,
    provider: FuncionarioLocalProvider = Depends(get_funcionario_provider),
    current_user: dict = Depends(auth_handler.decode_token),
):
    nome = _extrair_nome(current_user)
    return await funcionario_controller.finalizar(solicitacao_id, body.resultado, provider, current_user.get("sub"), nome)
