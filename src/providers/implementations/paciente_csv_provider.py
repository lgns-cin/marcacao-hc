import csv
from typing import List, Dict, Any
from fastapi import HTTPException, status

from ..interfaces.paciente_provider_interface import PacienteProviderInterface


class PacienteCsvProvider(PacienteProviderInterface):
    def __init__(
        self,
        csv_pacientes: str = 'data/pacientes.csv',
        csv_aghu: str = 'data/dataset_mock_exames.csv',
    ):
        self.csv_pacientes = csv_pacientes
        self.csv_aghu = csv_aghu
        self._check_file_exists(csv_pacientes)
        self._check_file_exists(csv_aghu)

    def _check_file_exists(self, path: str):
        try:
            with open(path, mode='r', encoding='utf-8') as f:
                pass
        except FileNotFoundError:
            raise RuntimeError(f"Arquivo CSV não encontrado em: {path}")

    def _ler_csv(self, path: str) -> List[Dict[str, str]]:
        """Lê todas as linhas de um CSV e retorna como lista de dicts."""
        try:
            with open(path, mode='r', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        except Exception as e:
            print(f"Erro ao ler CSV {path}: {e}")
            return []

    # métodos base

    async def listar_pacientes(self) -> List[Dict[str, Any]]:

        vistos = set()
        pacientes = []
        for row in self._ler_csv(self.csv_pacientes):
            try:
                prontuario = int(row.get('prontuario', -1))
                if prontuario not in vistos:
                    vistos.add(prontuario)
                    pacientes.append({
                        "prontuario": prontuario,
                        "telefone": row.get("telefone"),
                        "cidade": row.get("cidade"),
                        "estado": row.get("estado"),
                    })
            except ValueError:
                continue
        return pacientes

    async def obter_paciente_por_codigo(self, codigo: int) -> Dict[str, Any]:

        for row in self._ler_csv(self.csv_pacientes):
            try:
                if int(row.get('prontuario', -1)) == codigo:
                    return {
                        "prontuario": int(row["prontuario"]),
                        "telefone": row.get("telefone"),
                        "cidade": row.get("cidade"),
                        "estado": row.get("estado"),
                    }
            except ValueError:
                continue
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado",
        )

    # tool 1

    async def verificar_prontuario_existe(self, numero_prontuario: int) -> bool:

        for row in self._ler_csv(self.csv_aghu):
            try:
                if int(row.get('prontuario', -1)) == numero_prontuario:
                    return True
            except ValueError:
                continue
        return False

    # tool 2

    async def verificar_solicitacao_existe(
        self,
        numero_prontuario: int,
        numero_solicitacao: int,
    ) -> bool:

        for row in self._ler_csv(self.csv_aghu):
            try:
                mesmo_prontuario = int(row.get('prontuario', -1)) == numero_prontuario
                mesma_solicitacao = int(row.get('codigo_solicitacao', -1)) == numero_solicitacao
                if mesmo_prontuario and mesma_solicitacao:
                    return True
            except ValueError:
                continue
        return False

    # tool 3

    async def buscar_exames_solicitacao(
        self,
        numero_prontuario: int,
        numero_solicitacao: int,
    ) -> List[Dict[str, Any]]:

        if not await self.verificar_prontuario_existe(numero_prontuario):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prontuário não encontrado",
            )
        if not await self.verificar_solicitacao_existe(numero_prontuario, numero_solicitacao):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitação não encontrada para este prontuário",
            )

        exames = []
        for row in self._ler_csv(self.csv_aghu):
            try:
                mesmo_prontuario = int(row.get('prontuario', -1)) == numero_prontuario
                mesma_solicitacao = int(row.get('codigo_solicitacao', -1)) == numero_solicitacao
                if mesmo_prontuario and mesma_solicitacao:
                    exames.append({
                        "codigo_exame": row.get("codigo_exame"),
                        "nome_exame": row.get("nome_exame"),
                        "status_atribuicao": None,   # não existe no CSV
                        "funcionario_atribuido": row.get("id_funcionario"),
                    })
            except ValueError:
                continue
        return exames