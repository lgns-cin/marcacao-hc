from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class AdminProviderInterface(ABC):
    """Interface (contrato) para provedores do módulo administrativo."""

    @abstractmethod
    async def obter_visao_geral(self) -> Dict[str, Any]:
        """Retorna os KPIs e os dados dos gráficos da Central Administrativa."""
        pass

    @abstractmethod
    async def listar_pendencias(self) -> List[Dict[str, Any]]:
        """Retorna os agendamentos que exigem intervenção (bloqueados ou parados)."""
        pass

    @abstractmethod
    async def resolver_pendencia(self, id: int) -> Dict[str, Any]:
        """Marca uma pendência (problema reportado) como resolvida."""
        pass

    @abstractmethod
    async def listar_agendamentos(self, estado: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista agendamentos atribuídos, filtrando por 'em_andamento' ou 'concluido'."""
        pass

    @abstractmethod
    async def reatribuir_agendamento(self, id: int, funcionario: str) -> Dict[str, Any]:
        """Reatribui um agendamento a outro funcionário."""
        pass

    @abstractmethod
    async def devolver_a_fila(self, id: int, motivo: str) -> Dict[str, Any]:
        """Devolve um agendamento à fila geral, em nome da administração."""
        pass

    @abstractmethod
    async def listar_funcionarios(self) -> List[Dict[str, str]]:
        """Lista os funcionários disponíveis para reatribuição."""
        pass
