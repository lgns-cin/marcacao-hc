from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os

from ..controllers import funcionario_controller
from ..dependencies import get_funcionario_provider
from ..providers.interfaces.funcionario_provider_interface import FuncionarioProviderInterface
from ..auth.auth import auth_handler

# --- PONTO ÚNICO DE CONFIGURAÇÃO PARA ESTE ROTEADOR ---
STRATEGY = os.getenv("FUNCIONARIO_STRATEGY", "MOCK")
# ----------------------------------------------------

router = APIRouter(
    prefix="/api/funcionario",
    tags=["Funcionario"],
    dependencies=[Depends(auth_handler.decode_token)]
)

class DevolverRequest(BaseModel):
    motivo: str

class ProblemaRequest(BaseModel):
    motivo: str

class FinalizarRequest(BaseModel):
    resultado: str  # "CONFIRMADO" ou "CANCELADO"

@router.get("/agendamentos", response_model=List[dict])
async def listar_agendamentos(
    provider: FuncionarioProviderInterface = Depends(get_funcionario_provider(STRATEGY))
):
    """Lista todos os agendamentos na fila geral."""
    return await funcionario_controller.listar_agendamentos(provider)

@router.post("/agendamentos/{id}/puxar", response_model=dict)
async def puxar_agendamento(
    id: int,
    current_user: dict = Depends(auth_handler.decode_token),
    provider: FuncionarioProviderInterface = Depends(get_funcionario_provider(STRATEGY))
):
    """Puxa um agendamento da fila geral para a área de trabalho do atendente."""
    atendente = current_user.get("username")
    if not atendente:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido no token")
    await funcionario_controller.puxar_agendamento(id, atendente, provider)
    return {}

@router.get("/minha-area", response_model=List[dict])
async def listar_minha_area(
    current_user: dict = Depends(auth_handler.decode_token),
    provider: FuncionarioProviderInterface = Depends(get_funcionario_provider(STRATEGY))
):
    """Lista todos os agendamentos sob responsabilidade do atendente autenticado."""
    atendente = current_user.get("username")
    if not atendente:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido no token")
    return await funcionario_controller.listar_minha_area(atendente, provider)

@router.post("/minha-area/{id}/aguardar-confirmacao", response_model=dict)
async def aguardar_confirmacao(
    id: int,
    current_user: dict = Depends(auth_handler.decode_token),
    provider: FuncionarioProviderInterface = Depends(get_funcionario_provider(STRATEGY))
):
    """Marca um agendamento como aguardando confirmação do paciente."""
    atendente = current_user.get("username")
    if not atendente:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido no token")
    await funcionario_controller.aguardar_confirmacao(id, atendente, provider)
    return {}

@router.post("/minha-area/{id}/devolver", response_model=dict)
async def devolver_a_fila(
    id: int,
    body: DevolverRequest,
    current_user: dict = Depends(auth_handler.decode_token),
    provider: FuncionarioProviderInterface = Depends(get_funcionario_provider(STRATEGY))
):
    """Devolve o agendamento à fila geral de atendimentos."""
    atendente = current_user.get("username")
    if not atendente:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido no token")
    await funcionario_controller.devolver_a_fila(id, atendente, body.motivo, provider)
    return {}

@router.post("/minha-area/{id}/reportar-problema", response_model=dict)
async def reportar_problema(
    id: int,
    body: ProblemaRequest,
    current_user: dict = Depends(auth_handler.decode_token),
    provider: FuncionarioProviderInterface = Depends(get_funcionario_provider(STRATEGY))
):
    """Reporta um problema ou inconsistência em um agendamento."""
    atendente = current_user.get("username")
    if not atendente:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido no token")
    await funcionario_controller.reportar_problema(id, atendente, body.motivo, provider)
    return {}

@router.post("/minha-area/{id}/finalizar", response_model=dict)
async def finalizar_agendamento(
    id: int,
    body: FinalizarRequest,
    current_user: dict = Depends(auth_handler.decode_token),
    provider: FuncionarioProviderInterface = Depends(get_funcionario_provider(STRATEGY))
):
    """Finaliza o agendamento marcando o resultado final (CONFIRMADO/CANCELADO)."""
    atendente = current_user.get("username")
    if not atendente:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido no token")
    await funcionario_controller.finalizar_agendamento(id, atendente, body.resultado, provider)
    return {}
