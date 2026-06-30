from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import select, func, case, or_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ....models.exame_solicitado import ExameSolicitado
from ....models.funcionario import Funcionario
from ....models.paciente import Paciente
from ....enums import StatusAtribuicao, ResultadoAtribuicao


def _filtro_temporal(data_inicio: Optional[date], data_fim: Optional[date]) -> list:
    conds = []
    if data_inicio:
        conds.append(ExameSolicitado.data_solicitacao >= data_inicio)
    if data_fim:
        conds.append(ExameSolicitado.data_solicitacao <= data_fim)
    return conds


class AdminLocalProvider:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def calcular_kpis(
        self,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
    ) -> list[dict]:
        temporal = _filtro_temporal(data_inicio, data_fim)

        # Total de exames não excluídos
        total_result = await self.session.execute(
            select(func.count(ExameSolicitado.id)).where(
                ExameSolicitado.deleted_at == None,
                *temporal,
            )
        )
        total = total_result.scalar() or 0

        # Contagens por resultado (entre os finalizados)
        finalizados_result = await self.session.execute(
            select(
                func.count(ExameSolicitado.id).label("total_finalizados"),
                func.sum(
                    case((ExameSolicitado.resultado == ResultadoAtribuicao.CONFIRMADO, 1), else_=0)
                ).label("confirmados"),
                func.sum(
                    case((ExameSolicitado.resultado == ResultadoAtribuicao.PROBLEMA_REPORTADO, 1), else_=0)
                ).label("problemas"),
            ).where(
                ExameSolicitado.status_atribuicao == StatusAtribuicao.FINALIZADO,
                ExameSolicitado.deleted_at == None,
                *temporal,
            )
        )
        fin = finalizados_result.one()
        total_finalizados = fin.total_finalizados or 0
        confirmados = fin.confirmados or 0
        problemas = fin.problemas or 0

        # Média de exames ativos por funcionário
        ativos_result = await self.session.execute(
            select(
                ExameSolicitado.funcionario_atribuido,
                func.count(ExameSolicitado.id).label("qtd"),
            ).where(
                ExameSolicitado.funcionario_atribuido != None,
                ExameSolicitado.status_atribuicao.in_([
                    StatusAtribuicao.EM_ANDAMENTO,
                    StatusAtribuicao.AGUARDANDO_CONFIRMACAO,
                ]),
                ExameSolicitado.deleted_at == None,
                *temporal,
            ).group_by(ExameSolicitado.funcionario_atribuido)
        )
        ativos_por_func = ativos_result.all()
        if ativos_por_func:
            media_cards = sum(r.qtd for r in ativos_por_func) / len(ativos_por_func)
        else:
            media_cards = 0.0

        # Tempo médio de atendimento em dias (data_conclusao - data_atribuicao)
        tempo_result = await self.session.execute(
            select(ExameSolicitado.data_atribuicao, ExameSolicitado.data_conclusao).where(
                ExameSolicitado.status_atribuicao == StatusAtribuicao.FINALIZADO,
                ExameSolicitado.data_atribuicao != None,
                ExameSolicitado.data_conclusao != None,
                ExameSolicitado.deleted_at == None,
                *temporal,
            )
        )
        tempos = tempo_result.all()
        if tempos:
            dias = [(r.data_conclusao - r.data_atribuicao).days for r in tempos]
            tempo_medio = sum(dias) / len(dias)
        else:
            tempo_medio = 0.0

        pct_problemas = (problemas / total_finalizados * 100) if total_finalizados else 0.0
        pct_concluidos = (confirmados / total * 100) if total else 0.0

        return [
            {"id": "media_cards_por_funcionario", "valor": round(media_cards, 1),"formato": "int"},
            {"id": "pct_problematicas", "valor": round(pct_problemas, 1),"formato": "porcentagem"},
            {"id": "pct_concluidas", "valor": round(pct_concluidos, 1),"formato": "porcentagem"},
            {"id": "tempo_medio_atendimento_dias", "valor": round(tempo_medio, 1),"formato": "int"},
        ]

    async def ranking_por_exame(
        self,
        limit: int = 10,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
    ) -> List[dict]:
        temporal = _filtro_temporal(data_inicio, data_fim)
        result = await self.session.execute(
            select(
                ExameSolicitado.exame,
                ExameSolicitado.status_atribuicao,
                func.count(ExameSolicitado.id).label("quantidade"),
            ).where(
                ExameSolicitado.deleted_at == None,
                *temporal,
            ).group_by(
                ExameSolicitado.exame,
                ExameSolicitado.status_atribuicao,
            )
        )
        rows = result.all()
        return _agregar_ranking(rows, chave="exame", limit=limit)

    async def ranking_por_municipio(
        self,
        limit: int = 10,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
    ) -> List[dict]:
        temporal = _filtro_temporal(data_inicio, data_fim)
        result = await self.session.execute(
            select(
                Paciente.cidade.label("municipio"),
                ExameSolicitado.status_atribuicao,
                func.count(ExameSolicitado.id).label("quantidade"),
            ).join(
                Paciente, ExameSolicitado.paciente_solicitante == Paciente.prontuario
            ).where(
                ExameSolicitado.deleted_at == None,
                Paciente.cidade != None,
                *temporal,
            ).group_by(
                Paciente.cidade,
                ExameSolicitado.status_atribuicao,
            )
        )
        rows = result.all()
        return _agregar_ranking(rows, chave="municipio", limit=limit)

    async def listar_pendencias(
        self,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        busca: Optional[str] = None,
    ) -> List[ExameSolicitado]:
        temporal = _filtro_temporal(data_inicio, data_fim)
        stmt = (
            select(ExameSolicitado)
            .options(
                selectinload(ExameSolicitado.paciente),
                selectinload(ExameSolicitado.solicitacao_rel),
                selectinload(ExameSolicitado.exame_rel),
                selectinload(ExameSolicitado.funcionario),
            )
        )

        conditions = [
            ExameSolicitado.status_atribuicao == StatusAtribuicao.FINALIZADO,
            ExameSolicitado.resultado == ResultadoAtribuicao.PROBLEMA_REPORTADO,
            ExameSolicitado.deleted_at == None,
            *temporal,
        ]

        if busca:
            stmt = stmt.join(ExameSolicitado.paciente)
            busca_str = f"%{busca}%"
            conditions.append(
                or_(
                    Paciente.nome.ilike(busca_str),
                    cast(Paciente.prontuario, String).ilike(busca_str)
                )
            )

        stmt = stmt.where(*conditions)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def listar_agendamentos(
        self,
        estado: str,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        busca: Optional[str] = None,
    ) -> List[ExameSolicitado]:
        temporal = _filtro_temporal(data_inicio, data_fim)
        stmt = select(ExameSolicitado).options(
            selectinload(ExameSolicitado.paciente),
            selectinload(ExameSolicitado.solicitacao_rel),
            selectinload(ExameSolicitado.exame_rel),
            selectinload(ExameSolicitado.funcionario),
        )

        conditions = []

        if estado == "em_andamento":
            conditions.extend([
                ExameSolicitado.status_atribuicao.in_([
                    StatusAtribuicao.EM_ANDAMENTO,
                    StatusAtribuicao.AGUARDANDO_CONFIRMACAO,
                ]),
                ExameSolicitado.deleted_at == None
            ])
        elif estado == "concluidos":
            conditions.extend([
                ExameSolicitado.status_atribuicao == StatusAtribuicao.FINALIZADO,
                ExameSolicitado.deleted_at == None
            ])
        elif estado == "excluidos":
            conditions.append(ExameSolicitado.deleted_at != None)

        conditions.extend(temporal)

        if busca:
            stmt = stmt.join(ExameSolicitado.paciente)
            busca_str = f"%{busca}%"
            conditions.append(
                or_(
                    Paciente.nome.ilike(busca_str),
                    cast(Paciente.prontuario, String).ilike(busca_str)
                )
            )

        stmt = stmt.where(*conditions)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def buscar_por_solicitacao(self, solicitacao_id: int, exame_codigo: str) -> List[ExameSolicitado]:
        result = await self.session.execute(
            select(ExameSolicitado).where(
                ExameSolicitado.solicitacao == solicitacao_id,
                ExameSolicitado.deleted_at == None,
                ExameSolicitado.exame == exame_codigo
            )
        )
        return result.scalars().all()

    async def buscar_funcionario_por_username(self, username: str) -> Optional[Funcionario]:
        result = await self.session.execute(
            select(Funcionario).where(Funcionario.username == username)
        )
        return result.scalar_one_or_none()

    async def reatribuir(self, rows: List[ExameSolicitado], novo_funcionario_id: int) -> None:
        for row in rows:
            row.funcionario_atribuido = novo_funcionario_id
            row.status_atribuicao = StatusAtribuicao.EM_ANDAMENTO
            row.data_atribuicao = date.today()
        await self.session.commit()

    async def devolver(self, rows: List[ExameSolicitado], motivo: str) -> None:
        for row in rows:
            row.funcionario_atribuido = None
            row.status_atribuicao = StatusAtribuicao.PENDENTE
            row.data_atribuicao = None
            row.motivo = motivo
        await self.session.commit()

    async def excluir(self, rows: List[ExameSolicitado]) -> None:
        agora = datetime.now()
        for row in rows:
            row.deleted_at = agora
        await self.session.commit()

    async def resolver_pendencia(self, rows: List[ExameSolicitado], observacao: Optional[str]) -> None:
        for row in rows:
            row.resultado = ResultadoAtribuicao.RESOLVIDO_ADMIN
            row.data_conclusao = date.today()
            if observacao:
                row.detalhes = observacao
        await self.session.commit()

    async def listar_funcionarios(self) -> List[Funcionario]:
        result = await self.session.execute(
            select(Funcionario).where(Funcionario.deleted_at == None)
        )
        return result.scalars().all()


def _agregar_ranking(rows, chave: str, limit: int) -> List[dict]:
    """Pivota linhas (chave, status, quantidade) em um dict por chave com breakdown de status."""
    
    # tipos de exame
    catalogo = {
        'TCABI': 'Tomografia', 'TCABC': 'Tomografia', 'TCAVT': 'Tomografia', 'TCTX1': 'Tomografia',
        'RXMM1': 'Mamografia',
        'RXAB6': 'Raio-X', 'RXPAP': 'Raio-X', 'RXTX1': 'Raio-X', 'RXTX4': 'Raio-X',
        'EDA': 'Endoscopia',
        'CLN': 'Colonoscopia',
        'ECO': 'Ecocardiograma',
        'USABT': 'Ultrassonografia', 'USTDO': 'Ultrassonografia', 'USIDA': 'Ultrassonografia',
        'USIDV': 'Ultrassonografia', 'USIEA': 'Ultrassonografia', 'USIEV': 'Ultrassonografia', 'USGOD': 'Ultrassonografia',
        'ERGO': 'Ergometria',
        'ESPB': 'Espirometria',    
    }
    
    agregado: dict = {}
    for row in rows:
        nome = getattr(row, chave)
        
        # Mapeia o código para a categoria se for ranking de exames
        if chave == "exame":
            nome = catalogo.get(nome, nome)
            
        if nome not in agregado:
            agregado[nome] = {"pendentes": 0, "em_agendamento": 0, "concluidos": 0, "total": 0}
        qtd = row.quantidade
        status = row.status_atribuicao
        if status == StatusAtribuicao.PENDENTE:
            agregado[nome]["pendentes"] += qtd
        elif status in (StatusAtribuicao.EM_ANDAMENTO, StatusAtribuicao.AGUARDANDO_CONFIRMACAO):
            agregado[nome]["em_agendamento"] += qtd
        elif status == StatusAtribuicao.FINALIZADO:
            agregado[nome]["concluidos"] += qtd
        agregado[nome]["total"] += qtd
    ranking = [
        {
            "categoria": nome,
            "pendentes": dados["pendentes"],
            "em_andamento": dados["em_agendamento"],
            "concluidos": dados["concluidos"],
            "total": dados["total"]
        }
        for nome, dados in agregado.items()
    ]
    ranking.sort(key=lambda x: x["total"], reverse=True)
    return ranking[:limit]
