from typing import List, Dict, Any
from fastapi import HTTPException, status
from ..interfaces.funcionario_provider_interface import FuncionarioProviderInterface

# Estado mockado em memória persistente durante a execução da aplicação
_MOCK_AGENDAMENTOS = [
    {
        "id": 1,
        "nome": "Maria Silva Souza",
        "prontuario": "123456-7",
        "exames": ["Ecocardiograma Transtorácico", "Eletrocardiograma (ECG)"],
        "diasNaFila": 15,
        "status": "ALTA",
        "unidadeExecutora": "Unidade de Cardiologia",
        "unidadeSolicitante": "Ambulatório de Cardiologia Geral",
        "dataRetorno": "28/06/2026",
        "localizacao": "Recife",
        "regiao": "I Regional de Saúde",
        "idade": 72,
        "atendente": None,
        "estado": None,
        "resultado": None,
        "problema_motivo": None
    },
    {
        "id": 2,
        "nome": "Pedro Henrique Ramos",
        "prontuario": "765432-1",
        "exames": ["Ultrassonografia Abdominal Total"],
        "diasNaFila": 5,
        "status": "MÉDIA",
        "unidadeExecutora": "Unidade de Diagnóstico por Imagem",
        "unidadeSolicitante": "Pediatria - Ambulatório",
        "dataRetorno": "05/07/2026",
        "localizacao": "Olinda",
        "regiao": "I Regional de Saúde",
        "idade": 8,
        "atendente": None,
        "estado": None,
        "resultado": None,
        "problema_motivo": None
    },
    {
        "id": 3,
        "nome": "Ana Paula Medeiros",
        "prontuario": "246813-5",
        "exames": ["Hemograma Completo", "Glicemia de Jejum", "Creatinina"],
        "diasNaFila": 2,
        "status": "BAIXA",
        "unidadeExecutora": "Laboratório de Análises Clínicas",
        "unidadeSolicitante": "Ambulatório de Clínica Médica",
        "dataRetorno": "12/07/2026",
        "localizacao": "Caruaru",
        "regiao": "IV Regional de Saúde",
        "idade": 34,
        "atendente": None,
        "estado": None,
        "resultado": None,
        "problema_motivo": None
    },
    {
        "id": 4,
        "nome": "José Carlos Oliveira",
        "prontuario": "135792-4",
        "exames": ["Ressonância Magnética de Crânio"],
        "diasNaFila": 30,
        "status": "BAIXA",
        "unidadeExecutora": "Unidade de Diagnóstico por Imagem",
        "unidadeSolicitante": "Neurologia - Ambulatório",
        "dataRetorno": "10/07/2026",
        "localizacao": "Petrolina",
        "regiao": "VIII Regional de Saúde",
        "idade": 67,
        "atendente": None,
        "estado": None,
        "resultado": None,
        "problema_motivo": None
    },
    {
        "id": 5,
        "nome": "Juliana Santos Lima",
        "prontuario": "987654-3",
        "exames": ["Mamografia Bilateral"],
        "diasNaFila": 8,
        "status": "ALTA",
        "unidadeExecutora": "Centro de Oncologia - Imagem",
        "unidadeSolicitante": "Mastologia - Ambulatório",
        "dataRetorno": "01/07/2026",
        "localizacao": "Jaboatão dos Guararapes",
        "regiao": "I Regional de Saúde",
        "idade": 45,
        "atendente": None,
        "estado": None,
        "resultado": None,
        "problema_motivo": None
    },
    {
        "id": 6,
        "nome": "Lucas Cavalcanti Farias",
        "prontuario": "543210-9",
        "exames": ["Raio-X de Tórax (PA e Perfil)"],
        "diasNaFila": 12,
        "status": "MÉDIA",
        "unidadeExecutora": "Radiologia Geral",
        "unidadeSolicitante": "Pneumologia Geral",
        "dataRetorno": "03/07/2026",
        "localizacao": "Paulista",
        "regiao": "I Regional de Saúde",
        "idade": 16,
        "atendente": None,
        "estado": None,
        "resultado": None,
        "problema_motivo": None
    }
]

class MockFuncionarioProvider(FuncionarioProviderInterface):
    async def listar_agendamentos(self) -> List[Dict[str, Any]]:
        # Apenas os que não possuem atendente
        return [dict(item) for item in _MOCK_AGENDAMENTOS if item["atendente"] is None]

    async def puxar_agendamento(self, id: int, atendente: str) -> Dict[str, Any]:
        for item in _MOCK_AGENDAMENTOS:
            if item["id"] == id:
                if item["atendente"] is not None:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Este paciente já foi atribuído a outro atendente."
                    )
                item["atendente"] = atendente
                item["estado"] = "EM_ANDAMENTO"
                return dict(item)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado."
        )

    async def listar_minha_area(self, atendente: str) -> List[Dict[str, Any]]:
        # Apenas os atribuídos a este atendente
        return [dict(item) for item in _MOCK_AGENDAMENTOS if item["atendente"] == atendente]

    async def aguardar_confirmacao(self, id: int, atendente: str) -> Dict[str, Any]:
        for item in _MOCK_AGENDAMENTOS:
            if item["id"] == id:
                if item["atendente"] != atendente:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Este agendamento não está atribuído a você."
                    )
                item["estado"] = "AGUARDANDO_CONFIRMACAO"
                return dict(item)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado."
        )

    async def devolver_a_fila(self, id: int, atendente: str, motivo: str) -> Dict[str, Any]:
        for item in _MOCK_AGENDAMENTOS:
            if item["id"] == id:
                if item["atendente"] != atendente:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Este agendamento não está atribuído a você."
                    )
                item["atendente"] = None
                item["estado"] = None
                item["resultado"] = None
                item["problema_motivo"] = None
                # Log opcional para auditoria local
                print(f"Agendamento {id} devolvido à fila pelo atendente {atendente}. Motivo: {motivo}")
                return dict(item)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado."
        )

    async def reportar_problema(self, id: int, atendente: str, motivo: str) -> Dict[str, Any]:
        for item in _MOCK_AGENDAMENTOS:
            if item["id"] == id:
                if item["atendente"] != atendente:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Este agendamento não está atribuído a você."
                    )
                item["problema_motivo"] = motivo
                print(f"Problema reportado no agendamento {id} pelo atendente {atendente}. Motivo: {motivo}")
                return dict(item)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado."
        )

    async def finalizar_agendamento(self, id: int, atendente: str, resultado: str) -> Dict[str, Any]:
        for item in _MOCK_AGENDAMENTOS:
            if item["id"] == id:
                if item["atendente"] != atendente:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Este agendamento não está atribuído a você."
                    )
                if resultado not in ["CONFIRMADO", "CANCELADO"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Resultado inválido. Deve ser CONFIRMADO ou CANCELADO."
                    )
                item["estado"] = "FINALIZADO"
                item["resultado"] = resultado
                return dict(item)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado."
        )
