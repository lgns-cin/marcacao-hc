from abc import ABC, abstractmethod
from typing import List, Dict, Any


class AghuProviderInterface(ABC):
    """Interface para provedores que simulam a API AGHU."""

    @abstractmethod
    async def verificar_prontuario_existe(self, numero_prontuario: int) -> bool:
        """Verifica se o prontuário existe no AGHU mock."""
        pass

    @abstractmethod
    async def buscar_exames_solicitacao(
        self,
        numero_prontuario: int,
        numero_solicitacao: int
    ) -> List[Dict[str, Any]]:
        """Busca os exames de uma solicitação para um prontuário."""
        pass
