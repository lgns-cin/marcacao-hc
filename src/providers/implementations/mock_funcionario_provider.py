from typing import List, Dict, Any
from fastapi import HTTPException, status
from ..interfaces.funcionario_provider_interface import FuncionarioProviderInterface
from ._mock_agendamentos_data import MOCK_AGENDAMENTOS as _MOCK_AGENDAMENTOS

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
