from datetime import date
from typing import List

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Date, DateTime
from ..resources.database import Base


class Solicitacao(Base):
    __tablename__ = "solicitacoes"

    codigo = Column(Integer, primary_key=True, index=True)
    data_retorno = Column(Date)
    unidade_solicitante = Column(String)
    deleted_at = Column(DateTime, nullable=True)


class FormularioPacienteRequest(BaseModel):
    numero_prontuario: int
    numero_solicitacao: int
    telefone: str
    estado: str
    cidade: str
    exames: List[int]
