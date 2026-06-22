from typing import List, Dict, Any
from ..providers.interfaces.funcionario_provider_interface import FuncionarioProviderInterface

async def listar_agendamentos(provider: FuncionarioProviderInterface) -> List[Dict[str, Any]]:
    return await provider.listar_agendamentos()

async def puxar_agendamento(id: int, atendente: str, provider: FuncionarioProviderInterface) -> Dict[str, Any]:
    return await provider.puxar_agendamento(id, atendente)

async def listar_minha_area(atendente: str, provider: FuncionarioProviderInterface) -> List[Dict[str, Any]]:
    return await provider.listar_minha_area(atendente)

async def aguardar_confirmacao(id: int, atendente: str, provider: FuncionarioProviderInterface) -> Dict[str, Any]:
    return await provider.aguardar_confirmacao(id, atendente)

async def devolver_a_fila(id: int, atendente: str, motivo: str, provider: FuncionarioProviderInterface) -> Dict[str, Any]:
    return await provider.devolver_a_fila(id, atendente, motivo)

async def reportar_problema(id: int, atendente: str, motivo: str, provider: FuncionarioProviderInterface) -> Dict[str, Any]:
    return await provider.reportar_problema(id, atendente, motivo)

async def finalizar_agendamento(id: int, atendente: str, resultado: str, provider: FuncionarioProviderInterface) -> Dict[str, Any]:
    return await provider.finalizar_agendamento(id, atendente, resultado)
