from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from ..resources.database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    prontuario = Column(Integer, primary_key=True, index=True)
    telefone = Column(String)
    cidade = Column(String)
    estado = Column(String)
    deleted_at = Column(DateTime, nullable=True)

    exames_solicitados = relationship(
        "ExameSolicitado", back_populates="paciente"
    )
