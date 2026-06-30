from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..resources.database import get_app_db_session
from ..routers.admin import verify_admin_group
from ..providers.implementations.admin_local_provider import AdminLocalProvider
from ..controllers import admin_controller
from ..services.filtros import parse_lista

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
    limit: Optional[int] = None,
    regioes: Optional[str] = None,
    municipio: Optional[str] = None,
    tipos_exame: Optional[str] = None,
    faixa_etaria: Optional[str] = None,
    busca: Optional[str] = None,
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    lim = limit if limit is not None else limite
    return await admin_controller.listar_pendencias(
        provider,
        data_inicio,
        data_fim,
        limite=lim,
        regioes=parse_lista(regioes),
        municipio=municipio,
        tipos_exame=parse_lista(tipos_exame),
        faixa_etaria=faixa_etaria,
        busca=busca,
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
    limit: Optional[int] = None,
    regioes: Optional[str] = None,
    municipio: Optional[str] = None,
    tipos_exame: Optional[str] = None,
    faixa_etaria: Optional[str] = None,
    busca: Optional[str] = None,
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    lim = limit if limit is not None else limite
    return await admin_controller.listar_agendamentos(
        estado,
        provider,
        data_inicio,
        data_fim,
        limite=lim,
        regioes=parse_lista(regioes),
        municipio=municipio,
        tipos_exame=parse_lista(tipos_exame),
        faixa_etaria=faixa_etaria,
        busca=busca,
    )


@router.post("/agendamentos/{solicitacao_id}/{exame_codigo}/reatribuir")
async def reatribuir(
    solicitacao_id: int,
    exame_codigo: str,
    body: ReatribuirRequest,
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    return await admin_controller.reatribuir(solicitacao_id, exame_codigo, body.funcionario, provider)


@router.post("/agendamentos/{solicitacao_id}/{exame_codigo}/devolver")
async def devolver(
    solicitacao_id: int,
    exame_codigo: str,
    body: DevolverRequest,
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    return await admin_controller.devolver_admin(solicitacao_id, exame_codigo, body.motivo, provider)


@router.delete("/agendamentos/{solicitacao_id}/{exame_codigo}")
async def excluir(
    solicitacao_id: int,
    exame_codigo: str,
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    return await admin_controller.excluir(solicitacao_id, exame_codigo, provider)


@router.get("/funcionarios")
async def funcionarios(
    provider: AdminLocalProvider = Depends(get_admin_provider),
    _: dict = Depends(verify_admin_group),
):
    return await admin_controller.listar_funcionarios(provider)
