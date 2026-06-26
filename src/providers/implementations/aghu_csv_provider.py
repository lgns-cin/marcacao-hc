import csv
from pathlib import Path
from typing import List, Dict, Any

from ..interfaces.aghu_provider_interface import AghuProviderInterface


class AghuCsvProvider(AghuProviderInterface):
    def __init__(self, csv_path: str = "data/dataset_mock_aghu.csv"):
        self.csv_path = csv_path
        self.records: List[Dict[str, Any]] = []
        self._load_csv()

    def _load_csv(self) -> None:
        path = Path(self.csv_path)
        if not path.exists():
            raise RuntimeError(f"Arquivo AGHU mock não encontrado em: {self.csv_path}")

        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row["numero_prontuario"] = int(row.get("numero_prontuario", "-1"))
                except ValueError:
                    row["numero_prontuario"] = -1

                try:
                    row["numero_solicitacao"] = int(row.get("numero_solicitacao", "-1"))
                except ValueError:
                    row["numero_solicitacao"] = -1

                tem_vagas_raw = str(row.get("tem_vagas", "")).strip().lower()
                row["tem_vagas"] = tem_vagas_raw in ("1", "true", "t", "yes", "y", "sim")

                self.records.append(row)

    async def verificar_prontuario_existe(self, numero_prontuario: int) -> bool:
        return any(
            record.get("numero_prontuario") == numero_prontuario
            for record in self.records
        )

    async def verificar_solicitacao_existe(self, numero_solicitacao: int) -> bool:
        return any(
            record.get("numero_solicitacao") == numero_solicitacao
            for record in self.records
        )

    async def buscar_exames_solicitacao(
        self,
        numero_prontuario: int,
        numero_solicitacao: int,
    ) -> List[Dict[str, Any]]:
        return [
            record
            for record in self.records
            if record.get("numero_prontuario") == numero_prontuario
            and record.get("numero_solicitacao") == numero_solicitacao
        ]
