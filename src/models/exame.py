from typing import List

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from ..resources.database import Base


class Exame(Base):
    __tablename__ = "exames"

    codigo = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    exames_solicitados = relationship(
        "ExameSolicitado", back_populates="exame_rel"
    )
    

class ExameDisponibilidadeResponse(BaseModel):
    codigo_exame: int
    nome_exame: str
    tem_vagas: bool


class SolicitacaoExamesResponse(BaseModel):
    exames: List[ExameDisponibilidadeResponse]
