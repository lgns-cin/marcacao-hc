from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship
from ..resources.database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    prontuario = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=True)
    telefone = Column(String)
    cidade = Column(String)
    estado = Column(String)
    data_nascimento = Column(Date, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    exames_solicitados = relationship(
        "ExameSolicitado", back_populates="paciente"
    )
