from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship

from ..resources.database import Base


class ExameSolicitado(Base):
    __tablename__ = "exames_solicitados"

    id = Column(Integer, primary_key=True, index=True)
    solicitacao_codigo = Column(Integer, ForeignKey("solicitacoes.codigo"), nullable=False)
    exame_codigo = Column(Integer, ForeignKey("exames.codigo"), nullable=False)
    paciente_solicitante = Column(Integer, ForeignKey("pacientes.prontuario"), nullable=False)
    funcionario_atribuido = Column(Integer, ForeignKey("funcionarios.id"), nullable=True)
    status_atribuicao = Column(String, default="PENDENTE", nullable=False)
    data_atribuicao = Column(DateTime, nullable=True)

    solicitacao = relationship("Solicitacao")
    exame = relationship("Exame")
    paciente = relationship("Paciente")
    funcionario = relationship("Funcionario")
