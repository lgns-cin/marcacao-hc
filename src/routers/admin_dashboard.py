from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..resources.database import get_app_db_session
from ..routers.admin import verify_admin_group
from ..providers.implementations.banco_local.admin_local_provider import AdminLocalProvider
from ..controllers import admin_controller

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])


def get_admin_provider(db: AsyncSession = Depends(get_app_db_session)) -> AdminLocalProvider:
    return AdminLocalProvider(db)


class ResolverPendenciaRequest(BaseModel):
    observacao: Optional[str] = None


class ReatribuirRequest(BaseModel):
    funcionario: str


class DevolverRequest(BaseModel):
    motivo: str


@router.get("/visao-geral")
async def visao_geral(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    return await admin_controller.listar_visao_geral(provider, data_inicio, data_fim)


@router.get("/dashboard/ranking-exames")
async def ranking_exames(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    return await admin_controller.ranking_por_exame(provider, data_inicio, data_fim)


@router.get("/dashboard/ranking-municipios")
async def ranking_municipios(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    return await admin_controller.ranking_por_municipio(provider, data_inicio, data_fim)


@router.get("/pendencias")
async def pendencias(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    limite: Optional[int] = None,
    regioes: Optional[str] = Query(default=None),
    municipio: Optional[str] = Query(default=None),
    faixa_etaria: Optional[str] = Query(default=None),
    tipos_exame: Optional[str] = Query(default=None),
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    return await admin_controller.listar_pendencias(
        provider, data_inicio, data_fim, limite,
        regioes=regioes.split(",") if regioes else None,
        municipio=municipio or None,
        faixa_etaria=faixa_etaria or None,
        tipos_exame=tipos_exame.split(",") if tipos_exame else None,
    )



@router.post("/pendencias/{solicitacao_id}/resolver")
async def resolver_pendencia(
    solicitacao_id: int,
    body: ResolverPendenciaRequest,
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    return await admin_controller.resolver_pendencia(solicitacao_id, body.observacao, provider)


@router.get("/agendamentos")
async def agendamentos(
    estado: str = "em_andamento",
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    limite: Optional[int] = None,
    regioes: Optional[str] = Query(default=None),
    municipio: Optional[str] = Query(default=None),
    faixa_etaria: Optional[str] = Query(default=None),
    tipos_exame: Optional[str] = Query(default=None),
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    return await admin_controller.listar_agendamentos(
        estado, provider, data_inicio, data_fim, limite,
        regioes=regioes.split(",") if regioes else None,
        municipio=municipio or None,
        faixa_etaria=faixa_etaria or None,
        tipos_exame=tipos_exame.split(",") if tipos_exame else None,
    )



@router.post("/agendamentos/{solicitacao_id}/reatribuir")
async def reatribuir(
    solicitacao_id: int,
    body: ReatribuirRequest,
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    return await admin_controller.reatribuir(solicitacao_id, body.funcionario, provider)


@router.post("/agendamentos/{solicitacao_id}/devolver")
async def devolver(
    solicitacao_id: int,
    body: DevolverRequest,
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    return await admin_controller.devolver_admin(solicitacao_id, body.motivo, provider)


@router.delete("/agendamentos/{solicitacao_id}")
async def excluir(
    solicitacao_id: int,
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    return await admin_controller.excluir(solicitacao_id, provider)


@router.get("/funcionarios")
async def funcionarios(
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    return await admin_controller.listar_funcionarios(provider)
