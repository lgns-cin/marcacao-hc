from datetime import date
from typing import List, Optional, Literal

from fastapi import HTTPException, status

from ..enums import StatusAtribuicao, ResultadoAtribuicao
from ..providers.implementations.funcionario_local_provider import FuncionarioLocalProvider
from ..services.pontuacao import calcular_pontuacao
from ..services.filtros import aplicar_filtros, FAIXAS_ETARIAS

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


# Agrupa os registros de ExameSolicitado pelo código da solicitação
# Usado em minha-area onde todos os exames de uma solicitação formam um card
def _agrupar_por_solicitacao(rows) -> dict:
    grupos: dict = {}
    for row in rows:
        grupos.setdefault(row.solicitacao, []).append(row)
    return grupos


# Monta um AgendamentoItem a partir de um único registro de ExameSolicitado
# Cada exame é um card separado na fila
def _build_item(row) -> dict:
    paciente = row.paciente
    sol = row.solicitacao_rel

    dias_na_fila = (date.today() - row.data_solicitacao).days if row.data_solicitacao else 0

    # Um exame por card
    exame_nome = row.exame_rel.nome if row.exame_rel else row.exame

    localizacao = None
    if paciente and paciente.cidade:
        localizacao = f"{paciente.cidade}, {paciente.estado}" if paciente.estado else paciente.cidade

    # Idade como string; "Não informado" se data_nascimento não estiver disponível
    idade = "Não informado"
    if paciente and paciente.data_nascimento:
        hoje = date.today()
        anos = hoje.year - paciente.data_nascimento.year - (
            (hoje.month, hoje.day) < (paciente.data_nascimento.month, paciente.data_nascimento.day)
        )
        idade = f"{anos} anos"

    # nome do paciente vem do AGHU; usa prontuário como fallback
    prontuario = str(row.paciente_solicitante)
    nome = f"Paciente #{prontuario}"

    # consulta e formatação do telefone
    telefone = "Não informado"
    if paciente and paciente.telefone:
        telefone = str(paciente.telefone)
        ddd = telefone[0:2]
        telefone = f"({ddd}) {telefone[2:7]}-{telefone[7:]}"

    return {
        "id": row.id,
        "solicitacao": row.solicitacao,
        "prontuario": prontuario,
        "nome": nome,
        "telefone": telefone,
        "exame": exame_nome,
        "exameCodigo": row.exame,
        "diasNaFila": dias_na_fila,
        "unidadeSolicitante": sol.unidade_solicitante if sol else None,
        "dataRetorno": sol.data_retorno.isoformat() if sol and sol.data_retorno else None,
        "localizacao": localizacao,
        "idade": idade,
    }


# Retorna a fila geral: um card por exame, ordenados pelo algoritmo de pontuação
async def listar_agendamentos(
    provider: FuncionarioLocalProvider,
    limit: Optional[int] = None,
    regioes: Optional[list[str]] = None,
    municipio: Optional[str] = None,
    tipos_exame: Optional[list[str]] = None,
    faixa_etaria: Optional[str] = None,
    busca: Optional[str] = None,
) -> List[dict]:
    if faixa_etaria and faixa_etaria not in FAIXAS_ETARIAS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"faixa_etaria deve ser um de: {FAIXAS_ETARIAS}",
        )

    rows = await provider.listar_pendentes()
    rows = aplicar_filtros(
        rows,
        regioes=regioes,
        municipio=municipio,
        tipos_exame=tipos_exame,
        faixa_etaria=faixa_etaria,
        busca=busca,
    )

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
        items.append(item)

    items.sort(key=lambda x: x.pop("_pontuacao"), reverse=True)
    items = _aplicar_prioridade(items)

    if limit is not None:
        items = items[:limit]
        
    return items


# Atribui um agendamento PENDENTE ao funcionário logado, mudando o status para EM_ANDAMENTO
async def puxar_agendamento(
        solicitacao_id: int,
        exame_codigo: str,
        provider: FuncionarioLocalProvider,
        username: str,
        nome: Optional[str] = None
    ) -> dict:
    funcionario = await provider.get_or_create_funcionario(username, nome)
    rows = await provider.buscar_por_solicitacao(
        solicitacao_id, funcionario_id=None, status=StatusAtribuicao.PENDENTE, exame=exame_codigo
    )
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado ou já atribuído")
    await provider.atribuir(rows, funcionario.id)
    return {"mensagem": "Agendamento atribuído com sucesso"}


# Retorna os agendamentos do funcionário logado em qualquer estado (EM_ANDAMENTO, AGUARDANDO_CONFIRMACAO, FINALIZADO)
async def listar_minha_area(
    provider: FuncionarioLocalProvider,
    username: str,
    nome: Optional[str] = None,
    limit: Optional[int] = None,
    regioes: Optional[list[str]] = None,
    municipio: Optional[str] = None,
    tipos_exame: Optional[list[str]] = None,
    faixa_etaria: Optional[str] = None,
    busca: Optional[str] = None,
) -> List[dict]:
    if faixa_etaria and faixa_etaria not in FAIXAS_ETARIAS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"faixa_etaria deve ser um de: {FAIXAS_ETARIAS}",
        )

    funcionario = await provider.get_or_create_funcionario(username, nome)
    rows = await provider.listar_por_funcionario(funcionario.id)

    rows = aplicar_filtros(
        rows,
        regioes=regioes,
        municipio=municipio,
        tipos_exame=tipos_exame,
        faixa_etaria=faixa_etaria,
        busca=busca,
    )

    grupos = _agrupar_por_solicitacao(rows)
    items = []
    for grupo_rows in grupos.values():
        for exame_solicitado in grupo_rows:
            item = _build_item(exame_solicitado)
            # Adiciona os campos extras do MinhaAreaItem: estado atual e resultado (se finalizado)
            item["estado"] = exame_solicitado.status_atribuicao
            item["resultado"] = exame_solicitado.resultado
            items.append(item)

    if limit is not None:
        items = items[:limit]

    return items


# Avança o agendamento de EM_ANDAMENTO para AGUARDANDO_CONFIRMACAO
async def aguardar_confirmacao(
        solicitacao_id: int,
        exame_codigo: str,
        provider: FuncionarioLocalProvider,
        username: str,
        nome: Optional[str] = None
    ) -> dict:
    funcionario = await provider.get_or_create_funcionario(username, nome)
    # Só permite a transição se o agendamento estiver em EM_ANDAMENTO
    rows = await provider.buscar_por_solicitacao(solicitacao_id, funcionario.id, StatusAtribuicao.EM_ANDAMENTO, exame_codigo)
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado em EM_ANDAMENTO")
    await provider.transicionar_status(rows, StatusAtribuicao.AGUARDANDO_CONFIRMACAO)
    return {"mensagem": "Agendamento movido para AGUARDANDO_CONFIRMACAO"}


# Remove o agendamento da área do funcionário e o devolve para a fila geral com status PENDENTE
async def devolver(
        solicitacao_id: int,
        exame_codigo: str,
        motivo: str,
        provider: FuncionarioLocalProvider,
        username: str,
        nome: Optional[str] = None
    ) -> dict:
    funcionario = await provider.get_or_create_funcionario(username, nome)
    rows = await provider.buscar_por_solicitacao(solicitacao_id, funcionario.id, exame=exame_codigo)
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado na sua área")
    await provider.devolver(rows, motivo)
    return {"mensagem": "Agendamento devolvido para a fila"}


# Finaliza o agendamento com PROBLEMA_REPORTADO, registrando motivo e detalhes para o administrador
async def reportar_problema(
        solicitacao_id: int,
        exame_codigo: str,
        motivo: str,
        detalhes: Optional[str],
        provider: FuncionarioLocalProvider,
        username: str,
        nome: Optional[str] = None
    ) -> dict:
    funcionario = await provider.get_or_create_funcionario(username, nome)
    rows = await provider.buscar_por_solicitacao(solicitacao_id, funcionario.id, exame=exame_codigo)
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado na sua área")
    await provider.transicionar_status(
        rows, StatusAtribuicao.FINALIZADO,
        resultado=ResultadoAtribuicao.PROBLEMA_REPORTADO,
        motivo=motivo, detalhes=detalhes
    )
    return {"mensagem": "Problema reportado e agendamento finalizado"}


# Encerra o ciclo do atendimento com resultado CONFIRMADO ou PROBLEMA_REPORTADO
async def finalizar(
        solicitacao_id: int,
        exame_codigo: str,
        resultado: str,
        provider: FuncionarioLocalProvider,
        username: str,
        nome: Optional[str] = None
    ) -> dict:
    # Valida se o resultado enviado é um dos valores permitidos pelo enum
    if resultado not in ResultadoAtribuicao._value2member_map_:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"resultado deve ser um de: {[r.value for r in ResultadoAtribuicao]}",
        )
    funcionario = await provider.get_or_create_funcionario(username, nome)
    rows = await provider.buscar_por_solicitacao(solicitacao_id, funcionario.id, exame=exame_codigo)
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado na sua área")
    await provider.transicionar_status(rows, StatusAtribuicao.FINALIZADO, resultado=ResultadoAtribuicao(resultado))
    return {"mensagem": f"Agendamento finalizado com resultado {resultado}"}
