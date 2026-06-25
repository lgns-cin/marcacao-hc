from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.auth import auth_handler
from ..resources.database import get_app_db_session
from ..controllers import funcionario_controller

router = APIRouter(prefix="/api/funcionario", tags=["Funcionario"])


class FinalizarRequest(BaseModel):
    resultado: str


@router.get("/agendamentos")
async def listar_agendamentos(
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token),
):
    return await funcionario_controller.listar_agendamentos(db)


@router.post("/agendamentos/{solicitacao_id}/puxar")
async def puxar_agendamento(
    solicitacao_id: int,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token),
):
    username = current_user.get("sub")
    return await funcionario_controller.puxar_agendamento(solicitacao_id, db, username)


@router.get("/minha-area")
async def listar_minha_area(
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token),
):
    username = current_user.get("sub")
    return await funcionario_controller.listar_minha_area(db, username)


@router.post("/minha-area/{solicitacao_id}/aguardar-confirmacao")
async def aguardar_confirmacao(
    solicitacao_id: int,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token),
):
    username = current_user.get("sub")
    return await funcionario_controller.aguardar_confirmacao(solicitacao_id, db, username)


@router.post("/minha-area/{solicitacao_id}/finalizar")
async def finalizar(
    solicitacao_id: int,
    body: FinalizarRequest,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token),
):
    username = current_user.get("sub")
    return await funcionario_controller.finalizar(solicitacao_id, body.resultado, db, username)
