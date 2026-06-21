from fastapi import APIRouter, Depends
from typing import List

from ..controllers import paciente_controller
from ..dependencies import get_paciente_provider, get_aghu_provider
from ..models.exame import ExameDisponibilidadeResponse, SolicitacaoExamesResponse
from ..providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from ..providers.interfaces.aghu_provider_interface import AghuProviderInterface

from ..auth.auth import auth_handler

# --- PONTO ÚNICO DE CONFIGURAÇÃO PARA ESTE ROTEADOR ---
# Para usar o banco de dados em produção, altere esta linha para "postgres"
STRATEGY = "csv"
# ----------------------------------------------------

router = APIRouter(
    prefix="/api/pacientes",
    tags=["Pacientes"],
    dependencies=[Depends(auth_handler.decode_token)]
)

@router.get("", response_model=List[dict])
async def listar_pacientes(
    # A mágica acontece aqui:
    # 1. get_paciente_provider(STRATEGY) retorna a função _get_paciente_csv_provider
    # 2. FastAPI efetivamente executa Depends(_get_paciente_csv_provider)
    provider: PacienteProviderInterface = Depends(get_paciente_provider(STRATEGY))
):
    """Lista todos os pacientes da fonte de dados configurada no roteador."""
    return await paciente_controller.listar_pacientes(provider)

@router.get("/{codigo}", response_model=dict)
async def obter_paciente(
    codigo: int,
    provider: PacienteProviderInterface = Depends(get_paciente_provider(STRATEGY))
):
    """Obtém um paciente pelo código a partir da fonte de dados configurada no roteador."""
    return await paciente_controller.obter_paciente_por_codigo(codigo, provider)


@router.get("/forms/validar_paciente/{numero_prontuario}", response_model=dict)
async def validar_prontuario(
    numero_prontuario: int,
    provider: AghuProviderInterface = Depends(get_aghu_provider("csv"))
):
    """Valida se um prontuário existe no AGHU mock."""
    return await paciente_controller.validar_prontuario(numero_prontuario, provider)


@router.get("/forms/validar_solicitacao/{numero_prontuario}/{numero_solicitacao}", response_model=SolicitacaoExamesResponse)
async def consultar_exames_solicitacao(
    numero_prontuario: int,
    numero_solicitacao: int,
    provider: AghuProviderInterface = Depends(get_aghu_provider("csv"))
):
    """Consulta exames de imagem de uma solicitação vinculada a um prontuário AGHU mock."""
    return await paciente_controller.consultar_exames_solicitacao(
        numero_prontuario,
        numero_solicitacao,
        provider
    )
