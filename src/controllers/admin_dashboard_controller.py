from typing import List, Dict, Any, Optional
from ..providers.interfaces.admin_provider_interface import AdminProviderInterface


async def obter_visao_geral(provider: AdminProviderInterface) -> Dict[str, Any]:
    return await provider.obter_visao_geral()


async def listar_pendencias(provider: AdminProviderInterface) -> List[Dict[str, Any]]:
    return await provider.listar_pendencias()


async def resolver_pendencia(id: int, provider: AdminProviderInterface) -> Dict[str, Any]:
    return await provider.resolver_pendencia(id)


async def listar_agendamentos(estado: Optional[str], provider: AdminProviderInterface) -> List[Dict[str, Any]]:
    return await provider.listar_agendamentos(estado)


async def reatribuir_agendamento(id: int, funcionario: str, provider: AdminProviderInterface) -> Dict[str, Any]:
    return await provider.reatribuir_agendamento(id, funcionario)


async def devolver_a_fila(id: int, motivo: str, provider: AdminProviderInterface) -> Dict[str, Any]:
    return await provider.devolver_a_fila(id, motivo)


async def listar_funcionarios(provider: AdminProviderInterface) -> List[Dict[str, str]]:
    return await provider.listar_funcionarios()
