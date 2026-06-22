from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status

from ..interfaces.admin_provider_interface import AdminProviderInterface
from ._mock_agendamentos_data import MOCK_AGENDAMENTOS, MOCK_FUNCIONARIOS, nome_funcionario

# Limiar de dias em andamento sem progresso para considerar um agendamento "Parado"
DIAS_PARADO_LIMIAR = 15


def _situacao(item: Dict[str, Any]) -> Optional[str]:
    if item.get("problema_motivo"):
        return "BLOQUEADO"
    if item.get("estado") == "EM_ANDAMENTO" and item.get("diasNaFila", 0) > DIAS_PARADO_LIMIAR:
        return "PARADO"
    return None


class MockAdminProvider(AdminProviderInterface):
    async def obter_visao_geral(self) -> Dict[str, Any]:
        total_cards = len(MOCK_AGENDAMENTOS)
        atribuidos = [item for item in MOCK_AGENDAMENTOS if item["atendente"] is not None]
        quantidade_funcionarios = len(MOCK_FUNCIONARIOS)
        media_card_funcionario = round(len(atribuidos) / quantidade_funcionarios, 1) if quantidade_funcionarios else 0

        kpis = [
            {
                "id": "media_card_funcionario",
                "label": "Média de Card por Funcionário",
                "valor": media_card_funcionario,
                "categoria": "principal",
            },
            {
                "id": "media_exames_agendados",
                "label": "Média de Exames Agendados",
                "valor": 4.0,
                "tendencia": 5,
                "categoria": "principal",
            },
            {
                "id": "quantidade_funcionarios",
                "label": "Quantidade de Funcionários",
                "valor": quantidade_funcionarios,
                "categoria": "principal",
            },
            {
                "id": "total_cards",
                "label": "Total de Cards",
                "valor": total_cards,
                "categoria": "principal",
            },
            {
                "id": "tempo_medio_atendimento",
                "label": "Tempo médio de atendimento",
                "valor": 3.8,
                "sufixo": "dias",
                "categoria": "extra",
            },
            {
                "id": "solicitacoes_atendidas",
                "label": "Solicitações atendidas",
                "valor": 367,
                "categoria": "extra",
            },
            {
                "id": "pacientes_devolvidos_fila",
                "label": "Pacientes devolvidos à fila",
                "valor": 55,
                "tendencia": 15,
                "categoria": "extra",
            },
        ]

        graficos = [
            {
                "id": "por_tipo_exame",
                "titulo": "Por tipo de exame",
                "subtitulo": "Acompanhe a distribuição dos exames por tipo",
                "tipo": "barras_horizontais",
                "categoria": "principal",
                "dados": [
                    {"categoria": "Colonoscopia", "agendados": 8, "emAndamento": 2, "aAgendar": 0},
                    {"categoria": "Endoscopia", "agendados": 4, "emAndamento": 6, "aAgendar": 1},
                    {"categoria": "Ultrassonografia", "agendados": 3, "emAndamento": 0, "aAgendar": 2},
                    {"categoria": "Mamografia", "agendados": 1, "emAndamento": 1, "aAgendar": 0},
                    {"categoria": "Espirometria", "agendados": 0, "emAndamento": 1, "aAgendar": 0},
                ],
            },
            {
                "id": "por_localidade",
                "titulo": "Por localidade",
                "subtitulo": "Entenda como os exames se distribuem por localidade",
                "tipo": "barras_horizontais",
                "categoria": "principal",
                "dados": [
                    {"categoria": "Olinda", "agendados": 0, "emAndamento": 8, "aAgendar": 2},
                    {"categoria": "Recife", "agendados": 4, "emAndamento": 0, "aAgendar": 5},
                    {"categoria": "Jaboatão dos Guararapes", "agendados": 0, "emAndamento": 2, "aAgendar": 1},
                    {"categoria": "Caruaru", "agendados": 1, "emAndamento": 1, "aAgendar": 0},
                    {"categoria": "Petrolina", "agendados": 1, "emAndamento": 0, "aAgendar": 0},
                ],
            },
            {
                "id": "motivos_devolucao",
                "titulo": "Pacientes devolvidos à fila",
                "subtitulo": "Quantitativo por motivo de devolução",
                "tipo": "barras_verticais",
                "categoria": "extra",
                "dados": [
                    {"motivo": "Falha em contato com o paciente", "quantidade": 99},
                    {"motivo": "Pendência Operacional", "quantidade": 74},
                    {"motivo": "Reagendamento", "quantidade": 95},
                    {"motivo": "Outros", "quantidade": 24},
                ],
            },
        ]

        return {"kpis": kpis, "graficos": graficos}

    async def listar_pendencias(self) -> List[Dict[str, Any]]:
        pendencias = []
        for item in MOCK_AGENDAMENTOS:
            situacao = _situacao(item)
            if situacao:
                pendencia = dict(item)
                pendencia["situacao"] = situacao
                pendencia["responsavel"] = nome_funcionario(item["atendente"])
                pendencias.append(pendencia)
        return pendencias

    async def resolver_pendencia(self, id: int) -> Dict[str, Any]:
        for item in MOCK_AGENDAMENTOS:
            if item["id"] == id:
                if not item.get("problema_motivo"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Este agendamento não possui um problema pendente de resolução.",
                    )
                item["problema_motivo"] = None
                item["problema_detalhes"] = None
                return dict(item)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado.")

    async def listar_agendamentos(self, estado: Optional[str] = None) -> List[Dict[str, Any]]:
        estados_em_andamento = {"EM_ANDAMENTO", "AGUARDANDO_CONFIRMACAO"}

        def corresponde(item: Dict[str, Any]) -> bool:
            if item["atendente"] is None:
                return False
            if estado == "em_andamento":
                return item["estado"] in estados_em_andamento
            if estado == "concluido":
                return item["estado"] == "FINALIZADO"
            return True

        resultado = []
        for item in MOCK_AGENDAMENTOS:
            if corresponde(item):
                agendamento = dict(item)
                agendamento["responsavel"] = nome_funcionario(item["atendente"])
                resultado.append(agendamento)
        return resultado

    async def reatribuir_agendamento(self, id: int, funcionario: str) -> Dict[str, Any]:
        if not any(f["username"] == funcionario for f in MOCK_FUNCIONARIOS):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Funcionário inválido.")

        for item in MOCK_AGENDAMENTOS:
            if item["id"] == id:
                item["atendente"] = funcionario
                item["estado"] = item["estado"] or "EM_ANDAMENTO"
                return dict(item)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado.")

    async def devolver_a_fila(self, id: int, motivo: str) -> Dict[str, Any]:
        for item in MOCK_AGENDAMENTOS:
            if item["id"] == id:
                item["atendente"] = None
                item["estado"] = None
                item["resultado"] = None
                item["problema_motivo"] = None
                item["problema_detalhes"] = None
                print(f"[admin] Agendamento {id} devolvido à fila pela administração. Motivo: {motivo}")
                return dict(item)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado.")

    async def listar_funcionarios(self) -> List[Dict[str, str]]:
        return [dict(f) for f in MOCK_FUNCIONARIOS]
