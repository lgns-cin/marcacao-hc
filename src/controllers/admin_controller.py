from services.pontuacao import calcular_pontuacao
from sqlalchemy.util.typing import Literal
from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status

from ..providers.implementations.admin_local_provider import AdminLocalProvider
from ..enums import StatusAtribuicao, ResultadoAtribuicao

ESTADOS_VALIDOS = ("em_andamento", "concluidos", "excluidos")


def _validar_periodo(data_inicio: Optional[date], data_fim: Optional[date]) -> None:
    if data_inicio and data_fim and data_inicio > data_fim:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="data_inicio não pode ser posterior a data_fim",
        )

def _status(idx: int, total: int) -> Literal["ALTA", "MÉDIA", "BAIXA"]:
    """Retorna o status do item da fila de agendamento de índice `idx` dado que a fila tem `total` posições."""

    if idx in range(0, total // 4): # 0 a 25% da lista
        return "ALTA"
    if idx in range(total // 4, 3 * total // 4): # 25% a 75% da lista
        return "MÉDIA"
    if idx in range(3 * total // 4, total): # 75% a 100% da lista
        return "BAIXA"

def _aplicar_prioridade(items: list[dict]) -> list[dict]:
    """Atribui o status de cada item da fila de agendamento com base na sua posição."""

    total = len(items)

    for i in range(0, total):
        items[i]["status"] = _status(i, total)
    return items

def _build_item(row) -> dict:
    paciente = row.paciente
    sol = row.solicitacao_rel

    dias_na_fila = (date.today() - row.data_solicitacao).days if row.data_solicitacao else 0
    exame_nome = row.exame_rel.nome if row.exame_rel else row.exame

    localizacao = None
    if paciente and paciente.cidade:
        localizacao = f"{paciente.cidade}, {paciente.estado}" if paciente.estado else paciente.cidade

    idade = "Não informado"
    if paciente and paciente.data_nascimento:
        hoje = date.today()
        anos = hoje.year - paciente.data_nascimento.year - (
            (hoje.month, hoje.day) < (paciente.data_nascimento.month, paciente.data_nascimento.day)
        )
        idade = f"{anos} anos"

    prontuario = str(row.paciente_solicitante)

    funcionario_username = None
    if row.funcionario:
        funcionario_username = row.funcionario.username

    return {
        "id": row.id,
        "solicitacao": row.solicitacao,
        "prontuario": prontuario,
        "nome": f"Paciente #{prontuario}",
        "telefone": paciente.telefone,
        "exames": [exame_nome],
        "diasNaFila": dias_na_fila,
        "unidadeSolicitante": sol.unidade_solicitante if sol else None,
        "dataRetorno": sol.data_retorno.isoformat() if sol and sol.data_retorno else None,
        "localizacao": localizacao,
        "idade": idade,
        "funcionarioAtribuido": funcionario_username,
    }

async def listar_visao_geral(
    provider: AdminLocalProvider,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> dict:
    _validar_periodo(data_inicio, data_fim)
    return await provider.calcular_kpis(data_inicio, data_fim)


async def ranking_por_exame(
    provider: AdminLocalProvider,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> List[dict]:
    _validar_periodo(data_inicio, data_fim)
    return await provider.ranking_por_exame(limit=10, data_inicio=data_inicio, data_fim=data_fim)


async def ranking_por_municipio(
    provider: AdminLocalProvider,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> List[dict]:
    _validar_periodo(data_inicio, data_fim)
    return await provider.ranking_por_municipio(limit=10, data_inicio=data_inicio, data_fim=data_fim)


async def listar_pendencias(
    provider: AdminLocalProvider,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    limite: Optional[int] = None,
) -> List[dict]:
    _validar_periodo(data_inicio, data_fim)
    rows = await provider.listar_pendencias(data_inicio, data_fim)

    # aplicar pontuacao e ordenar
    items = []
    for row in rows:
        item = _build_item(row)
        sol = row.solicitacao_rel
        paciente = row.paciente
        item["_pontuacao"] = calcular_pontuacao(
            {"cidade": paciente.cidade if paciente else ""},
            {
                "data_retorno": sol.data_retorno.isoformat() if sol and sol.data_retorno else "",
                "unidade_solicitante": sol.unidade_solicitante if sol else "",
                "data_solicitacao": row.data_solicitacao.isoformat() if row.data_solicitacao else "",
            }
        )
        item["estadoAtribuicao"] = row.status_atribuicao
        item["resultado"] = row.resultado
        item["motivo"] = row.motivo
        item["detalhes"] = row.detalhes
        items.append(item)
    
    items.sort(key=lambda x: x.pop("_pontuacao"), reverse=True)
    items = _aplicar_prioridade(items)

    if limite is not None:
        items = items[:limite]
    
    return items


async def listar_agendamentos(
    estado: str,
    provider: AdminLocalProvider,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    limite: Optional[int] = None,
) -> List[dict]:
    if estado not in ESTADOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"estado deve ser um de: {ESTADOS_VALIDOS}",
        )
    _validar_periodo(data_inicio, data_fim)
    rows = await provider.listar_agendamentos(estado, data_inicio, data_fim)

    # aplicar pontuacao e ordenar
    items = []
    for row in rows:
        item = _build_item(row)
        sol = row.solicitacao_rel
        paciente = row.paciente
        item["_pontuacao"] = calcular_pontuacao(
            {"cidade": paciente.cidade if paciente else ""},
            {
                "data_retorno": sol.data_retorno.isoformat() if sol and sol.data_retorno else "",
                "unidade_solicitante": sol.unidade_solicitante if sol else "",
                "data_solicitacao": row.data_solicitacao.isoformat() if row.data_solicitacao else "",
            }
        )
        item["estadoAtribuicao"] = row.status_atribuicao
        item["resultado"] = row.resultado
        item["motivo"] = row.motivo
        if estado == "excluidos":
            item["excluidoEm"] = row.deleted_at.isoformat() if row.deleted_at else None
        items.append(item)
    
    items.sort(key=lambda x: x.pop("_pontuacao"), reverse=True)
    items = _aplicar_prioridade(items)

    if limite is not None:
        items = items[:limite]
    
    return items


async def reatribuir(solicitacao_id: int, username_novo: str, provider: AdminLocalProvider) -> dict:
    funcionario = await provider.buscar_funcionario_por_username(username_novo)
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funcionário '{username_novo}' não encontrado",
        )
    rows = await provider.buscar_por_solicitacao(solicitacao_id)
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )
    await provider.reatribuir(rows, funcionario.id)
    return {"mensagem": f"Agendamento reatribuído para {username_novo}"}


async def devolver_admin(solicitacao_id: int, motivo: str, provider: AdminLocalProvider) -> dict:
    rows = await provider.buscar_por_solicitacao(solicitacao_id)
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )
    await provider.devolver(rows, motivo)
    return {"mensagem": "Agendamento devolvido para a fila"}


async def excluir(solicitacao_id: int, provider: AdminLocalProvider) -> dict:
    rows = await provider.buscar_por_solicitacao(solicitacao_id)
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )
    await provider.excluir(rows)
    return {"mensagem": "Agendamento excluído"}


async def listar_funcionarios(provider: AdminLocalProvider) -> List[dict]:
    funcionarios = await provider.listar_funcionarios()
    return [{"username": f.username, "nome": f.nome} for f in funcionarios]


async def resolver_pendencia(solicitacao_id: int, observacao: Optional[str], provider: AdminLocalProvider) -> dict:
    rows = await provider.buscar_por_solicitacao(solicitacao_id)
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pendência não encontrada")
    pendentes = [r for r in rows if r.resultado == ResultadoAtribuicao.PROBLEMA_REPORTADO]
    if not pendentes:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nenhum item com PROBLEMA_REPORTADO nessa solicitação")
    await provider.resolver_pendencia(pendentes, observacao)
    return {"mensagem": "Pendência resolvida"}
