from abc import ABC, abstractmethod
from typing import List, Dict, Any


class PacienteProviderInterface(ABC):
    """
    Interface estendida para provedores de dados de pacientes.

    Complementa a PacienteProviderInterface já existente no repositório,
    adicionando os métodos necessários para os endpoints da API definidos.
    """

    @abstractmethod
    async def listar_pacientes(self) -> List[Dict[str, Any]]:
        """
        Retorna uma lista com todos os pacientes ativos.

        Pacientes com deleted_at preenchido (deleção lógica) não devem
        ser incluídos. Cada item da lista contém:
            - prontuario: número do prontuário (chave primária)
            - telefone:   telefone de contato
            - cidade:     cidade de residência
            - estado:     estado de residência
        """
        pass

    @abstractmethod
    async def obter_paciente_por_codigo(self, codigo: int) -> Dict[str, Any]:
        """
        Retorna um único paciente pelo número do prontuário.

        Lança HTTPException 404 se o paciente não for encontrado ou
        estiver deletado logicamente.

        Parâmetros:
            codigo: número inteiro do prontuário do paciente.
        """
        pass

    @abstractmethod
    async def verificar_prontuario_existe(self, numero_prontuario: int) -> bool:
        """
        Verifica se um prontuário existe e está ativo.

        Retorna True se encontrado e não deletado logicamente.
        Retorna False caso contrário.

        Parâmetros:
            numero_prontuario: número inteiro do prontuário do paciente.
        """
        pass

    @abstractmethod
    async def verificar_solicitacao_existe(
        self,
        numero_prontuario: int,
        numero_solicitacao: int,
    ) -> bool:
        """
        Verifica se uma solicitação existe e está vinculada ao prontuário.

        A solicitação precisa estar associada ao paciente informado,
        não basta o código da solicitação existir isoladamente.
        Retorna True apenas se ambas as condições forem satisfeitas.

        Parâmetros:
            numero_prontuario:  número inteiro do prontuário do paciente.
            numero_solicitacao: número inteiro do código da solicitação.
        """
        pass

    @abstractmethod
    async def buscar_exames_solicitacao(
        self,
        numero_prontuario: int,
        numero_solicitacao: int,
    ) -> List[Dict[str, Any]]:
        """
        Retorna a lista de exames de uma solicitação vinculada ao prontuário.

        Valida internamente se o prontuário e a solicitação existem antes
        de realizar a busca, lançando HTTPException 404 se necessário.

        Cada item da lista contém:
            - codigo_exame:          código do exame
            - nome_exame:            nome do exame
            - status_atribuicao:     status atual de atribuição
            - funcionario_atribuido: id do funcionário atribuído (pode ser None)

        Parâmetros:
            numero_prontuario:  número inteiro do prontuário do paciente.
            numero_solicitacao: número inteiro do código da solicitação.
        """
        pass