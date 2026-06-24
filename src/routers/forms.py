from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..controllers import forms_controller
from ..resources.postgres import get_postgres_session
from ..providers.interfaces.aghu_provider_interface import AghuProviderInterface
from ..dependencies import get_aghu_provider
from ..models.solicitacao import FormularioPacienteRequest
from ..auth.auth import auth_handler

router = APIRouter(
    prefix="/forms",
    tags=["Forms"],
    dependencies=[Depends(auth_handler.decode_token)]
router = APIRouter(
    prefix="/forms",
    tags=["Forms"]
)

@router.get("/validar_paciente/{numero_prontuario}", response_model=bool)
async def validar_prontuario(
    numero_prontuario: int,
    provider: AghuProviderInterface = Depends(get_aghu_provider("csv"))
):
    """Valida se um prontuário existe no AGHU mock."""
    return await forms_controller.validar_prontuario(numero_prontuario, provider)

@router.get("/validar_solicitacao/{numero_prontuario}/{numero_solicitacao}", response_model=dict)
async def consultar_exames_solicitacao(
    numero_prontuario: int,
    numero_solicitacao: int,
    db: AsyncSession = Depends(get_postgres_session),
    provider: AghuProviderInterface = Depends(get_aghu_provider("csv"))
):
    """Consulta exames de imagem de uma solicitação vinculada a um prontuário AGHU mock."""
    return await forms_controller.consultar_exames_solicitacao(
        numero_prontuario,
        numero_solicitacao,
        db,
        provider
    )

@router.post("/enviar", response_model=dict)
async def enviar_formulario_paciente(
    payload: FormularioPacienteRequest,
    db: AsyncSession = Depends(get_postgres_session),
    aghu_provider: AghuProviderInterface = Depends(get_aghu_provider("csv"))
):
    """Recebe os dados do formulário do paciente e persiste a solicitação localmente no banco de dados."""
    return await forms_controller.processar_formulario_paciente(
        payload,
        db,
        aghu_provider
    )
