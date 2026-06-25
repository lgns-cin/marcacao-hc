from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.exame_solicitado import ExameSolicitado

URGENCIA_ALTA = {"UTI", "OBSTETRICO", "EMERGENCIA", "MATERNIDADE", "ONCOLOGIA"}
URGENCIA_MEDIA = {"NEFROLOGIA", "CARDIOLOGIA", "PNEUMOLOGIA", "NEUROLOGIA"}


def _prioridade(unidade: str) -> str:
    u = (unidade or "").upper()
    if any(k in u for k in URGENCIA_ALTA):
        return "alta"
    if any(k in u for k in URGENCIA_MEDIA):
        return "media"
    return "baixa"


def _estado_de_status(status_atribuicao: str) -> str:
    if status_atribuicao in ("FINALIZADO_CONFIRMADO", "FINALIZADO_PROBLEMA_REPORTADO"):
        return "FINALIZADO"
    return status_atribuicao or "EM_ANDAMENTO"


def _resultado_de_status(status_atribuicao: str) -> Optional[str]:
    if status_atribuicao == "FINALIZADO_CONFIRMADO":
        return "CONFIRMADO"
    if status_atribuicao == "FINALIZADO_PROBLEMA_REPORTADO":
        return "PROBLEMA_REPORTADO"
    return None


async def _carregar_grupos(db: AsyncSession, solicitacao_ids: list) -> dict:
    stmt = (
        select(ExameSolicitado)
        .options(
            selectinload(ExameSolicitado.paciente),
            selectinload(ExameSolicitado.solicitacao_rel),
            selectinload(ExameSolicitado.exame_rel),
        )
        .where(
            ExameSolicitado.solicitacao.in_(solicitacao_ids),
            ExameSolicitado.deleted_at == None,
        )
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()

    grupos: dict = {}
    for row in rows:
        grupos.setdefault(row.solicitacao, []).append(row)
    return grupos


def _build_item(rows: list) -> dict:
    first = rows[0]
    paciente = first.paciente
    sol = first.solicitacao_rel

    dias_na_fila = 0
    datas = [r.data_solicitacao for r in rows if r.data_solicitacao]
    if datas:
        dias_na_fila = (date.today() - min(datas)).days

    exames = [r.exame_rel.nome if r.exame_rel else r.exame for r in rows]

    localizacao = None
    if paciente and paciente.cidade:
        localizacao = f"{paciente.cidade}, {paciente.estado}" if paciente.estado else paciente.cidade

    return {
        "id": first.solicitacao,
        "prontuario": str(first.paciente_solicitante),
        "nome": None,
        "exames": exames,
        "diasNaFila": dias_na_fila,
        "status": _prioridade(sol.unidade_solicitante if sol else ""),
        "unidadeSolicitante": sol.unidade_solicitante if sol else None,
        "dataRetorno": sol.data_retorno.isoformat() if sol and sol.data_retorno else None,
        "localizacao": localizacao,
        "idade": None,
    }


async def listar_agendamentos(db: AsyncSession) -> List[dict]:
    stmt = (
        select(ExameSolicitado.solicitacao)
        .where(
            ExameSolicitado.responsavel_username == None,
            ExameSolicitado.status_atribuicao == "PENDENTE",
            ExameSolicitado.deleted_at == None,
        )
        .distinct()
    )
    result = await db.execute(stmt)
    solicitacao_ids = [row[0] for row in result.fetchall()]

    if not solicitacao_ids:
        return []

    grupos = await _carregar_grupos(db, solicitacao_ids)
    return [_build_item(rows) for rows in grupos.values()]


async def puxar_agendamento(solicitacao_id: int, db: AsyncSession, username: str) -> dict:
    stmt = select(ExameSolicitado).where(
        ExameSolicitado.solicitacao == solicitacao_id,
        ExameSolicitado.responsavel_username == None,
        ExameSolicitado.status_atribuicao == "PENDENTE",
        ExameSolicitado.deleted_at == None,
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado ou já atribuído a outro atendente",
        )

    for row in rows:
        row.responsavel_username = username
        row.status_atribuicao = "EM_ANDAMENTO"
        row.data_atribuicao = date.today()

    await db.commit()
    return {"mensagem": "Agendamento atribuído com sucesso"}


async def listar_minha_area(db: AsyncSession, username: str) -> List[dict]:
    stmt = (
        select(ExameSolicitado.solicitacao)
        .where(
            ExameSolicitado.responsavel_username == username,
            ExameSolicitado.deleted_at == None,
        )
        .distinct()
    )
    result = await db.execute(stmt)
    solicitacao_ids = [row[0] for row in result.fetchall()]

    if not solicitacao_ids:
        return []

    grupos = await _carregar_grupos(db, solicitacao_ids)
    items = []
    for rows in grupos.values():
        item = _build_item(rows)
        status_atual = rows[0].status_atribuicao
        item["estado"] = _estado_de_status(status_atual)
        item["resultado"] = _resultado_de_status(status_atual)
        items.append(item)
    return items


async def aguardar_confirmacao(solicitacao_id: int, db: AsyncSession, username: str) -> dict:
    stmt = select(ExameSolicitado).where(
        ExameSolicitado.solicitacao == solicitacao_id,
        ExameSolicitado.responsavel_username == username,
        ExameSolicitado.status_atribuicao == "EM_ANDAMENTO",
        ExameSolicitado.deleted_at == None,
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado em EM_ANDAMENTO na sua área",
        )

    for row in rows:
        row.status_atribuicao = "AGUARDANDO_CONFIRMACAO"

    await db.commit()
    return {"mensagem": "Agendamento movido para AGUARDANDO_CONFIRMACAO"}


async def finalizar(solicitacao_id: int, resultado: str, db: AsyncSession, username: str) -> dict:
    RESULTADOS_VALIDOS = {"CONFIRMADO", "PROBLEMA_REPORTADO"}
    if resultado not in RESULTADOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"resultado deve ser 'CONFIRMADO' ou 'PROBLEMA_REPORTADO'",
        )

    stmt = select(ExameSolicitado).where(
        ExameSolicitado.solicitacao == solicitacao_id,
        ExameSolicitado.responsavel_username == username,
        ExameSolicitado.deleted_at == None,
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado na sua área",
        )

    for row in rows:
        row.status_atribuicao = f"FINALIZADO_{resultado}"

    await db.commit()
    return {"mensagem": f"Agendamento finalizado com resultado {resultado}"}
