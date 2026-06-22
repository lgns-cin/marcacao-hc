from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from ..resources.database import Base


class ExameSolicitado(Base):
    __tablename__ = "exames_solicitados"

    id = Column(Integer, primary_key=True, index=True)
    solicitacao = Column(Integer, ForeignKey("solicitacoes.codigo"), nullable=False)
    exame = Column(Integer, ForeignKey("exames.codigo"), nullable=False)
    paciente_solicitante = Column(Integer, ForeignKey("pacientes.prontuario"), nullable=False)
    funcionario_atribuido = Column(Integer, ForeignKey("funcionarios.id"), nullable=True)
    status_atribuicao = Column(String)
    data_atribuicao = Column(Date)
    deleted_at = Column(DateTime, nullable=True)
