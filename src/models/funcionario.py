from sqlalchemy import Column, Integer, Boolean, DateTime, String
from sqlalchemy.orm import relationship
from ..resources.database import Base


class Funcionario(Base):
    __tablename__ = "funcionarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=True)
    nome = Column(String, nullable=True)
    is_administrador = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)

    exames_solicitados = relationship(
        "ExameSolicitado", back_populates="funcionario"
    )
