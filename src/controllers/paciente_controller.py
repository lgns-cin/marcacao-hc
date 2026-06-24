from typing import List, Dict, Any

from ..models.exame import Exame
from ..providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from ..providers.interfaces.aghu_provider_interface import AghuProviderInterface

async def listar_pacientes(
    provider: PacienteProviderInterface
) -> List[Dict[str, Any]]:
    return await provider.listar_pacientes()

async def obter_paciente_por_codigo(
    codigo: int,
    provider: PacienteProviderInterface
) -> Dict[str, Any]:
    return await provider.obter_paciente_por_codigo(codigo)
