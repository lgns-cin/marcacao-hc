from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os

from ..controllers import admin_dashboard_controller
from ..dependencies import get_admin_provider
from ..providers.interfaces.admin_provider_interface import AdminProviderInterface
from .admin import verify_admin_group

# --- PONTO ÚNICO DE CONFIGURAÇÃO PARA ESTE ROTEADOR ---
STRATEGY = os.getenv("ADMIN_STRATEGY", "MOCK")
# ----------------------------------------------------

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin Dashboard"],
    dependencies=[Depends(verify_admin_group)],
)


class ReatribuirRequest(BaseModel):
    funcionario: str


class DevolverRequest(BaseModel):
    motivo: str


@router.get("/visao-geral", response_model=Dict[str, Any])
async def visao_geral(
    provider: AdminProviderInterface = Depends(get_admin_provider(STRATEGY)),
):
    """Retorna os KPIs e gráficos da Central Administrativa."""
    return await admin_dashboard_controller.obter_visao_geral(provider)


@router.get("/pendencias", response_model=List[Dict[str, Any]])
async def pendencias(
    provider: AdminProviderInterface = Depends(get_admin_provider(STRATEGY)),
):
    """Lista os agendamentos que exigem intervenção administrativa."""
    return await admin_dashboard_controller.listar_pendencias(provider)


@router.post("/pendencias/{id}/resolver", response_model=Dict[str, Any])
async def resolver_pendencia(
    id: int,
    provider: AdminProviderInterface = Depends(get_admin_provider(STRATEGY)),
):
    """Marca uma pendência como resolvida."""
    return await admin_dashboard_controller.resolver_pendencia(id, provider)


@router.get("/agendamentos", response_model=List[Dict[str, Any]])
async def agendamentos(
    estado: Optional[str] = Query(default=None, pattern="^(em_andamento|concluido)$"),
    provider: AdminProviderInterface = Depends(get_admin_provider(STRATEGY)),
):
    """Lista agendamentos atribuídos, filtrando por estado (em_andamento/concluido)."""
    return await admin_dashboard_controller.listar_agendamentos(estado, provider)


@router.post("/agendamentos/{id}/reatribuir", response_model=Dict[str, Any])
async def reatribuir_agendamento(
    id: int,
    body: ReatribuirRequest,
    provider: AdminProviderInterface = Depends(get_admin_provider(STRATEGY)),
):
    """Reatribui um agendamento a outro funcionário."""
    return await admin_dashboard_controller.reatribuir_agendamento(id, body.funcionario, provider)


@router.post("/agendamentos/{id}/devolver", response_model=Dict[str, Any])
async def devolver_a_fila(
    id: int,
    body: DevolverRequest,
    provider: AdminProviderInterface = Depends(get_admin_provider(STRATEGY)),
):
    """Devolve um agendamento à fila geral em nome da administração."""
    return await admin_dashboard_controller.devolver_a_fila(id, body.motivo, provider)


@router.get("/funcionarios", response_model=List[Dict[str, str]])
async def funcionarios(
    provider: AdminProviderInterface = Depends(get_admin_provider(STRATEGY)),
):
    """Lista os funcionários disponíveis para reatribuição."""
    return await admin_dashboard_controller.listar_funcionarios(provider)
