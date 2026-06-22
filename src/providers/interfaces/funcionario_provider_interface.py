from abc import ABC, abstractmethod
from typing import List, Dict, Any

class FuncionarioProviderInterface(ABC):
    """Interface (contrato) para provedores do módulo do funcionário."""

    @abstractmethod
    async def listar_agendamentos(self) -> List[Dict[str, Any]]:
        """Retorna os agendamentos disponíveis na fila geral (sem atendente)."""
        pass

    @abstractmethod
    async def puxar_agendamento(self, id: int, atendente: str) -> Dict[str, Any]:
        """Atribui o agendamento ao atendente. Se já atribuído, gera HTTPException 409."""
        pass

    @abstractmethod
    async def listar_minha_area(self, atendente: str) -> List[Dict[str, Any]]:
        """Retorna os agendamentos atribuídos ao atendente em qualquer estado."""
        pass

    @abstractmethod
    async def aguardar_confirmacao(self, id: int, atendente: str) -> Dict[str, Any]:
        """Marca o agendamento como aguardando confirmação."""
        pass

    @abstractmethod
    async def devolver_a_fila(self, id: int, atendente: str, motivo: str) -> Dict[str, Any]:
        """Devolve o agendamento para a fila geral."""
        pass

    @abstractmethod
    async def reportar_problema(self, id: int, atendente: str, motivo: str) -> Dict[str, Any]:
        """Registra um problema no agendamento, sem alterar o estado."""
        pass

    @abstractmethod
    async def finalizar_agendamento(self, id: int, atendente: str, resultado: str) -> Dict[str, Any]:
        """Finaliza o agendamento com o resultado CONFIRMADO ou CANCELADO."""
        pass
