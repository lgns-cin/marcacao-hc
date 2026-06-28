from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status

from ..enums import StatusAtribuicao, ResultadoAtribuicao
from ..providers.implementations.funcionario_local_provider import FuncionarioLocalProvider
from ..services.pontuacao import calcular_pontuacao

# Palavras-chave usadas para classificar a prioridade pela unidade solicitante
URGENCIA_ALTA = {"UTI", "OBSTETRICO", "EMERGENCIA", "MATERNIDADE", "ONCOLOGIA"}
URGENCIA_MEDIA = {"NEFROLOGIA", "CARDIOLOGIA", "PNEUMOLOGIA", "NEUROLOGIA"}


# Classifica a unidade solicitante em alta/media/baixa para exibição visual no card (campo "status" do AgendamentoItem).
# NÃO define a ordem da fila — a ordenação é feita pelo calcular_pontuacao() em src/services/pontuacao.py.
def _prioridade(unidade: str) -> str:
    u = (unidade or "").upper()
    if any(k in u for k in URGENCIA_ALTA):
        return "alta"
    if any(k in u for k in URGENCIA_MEDIA):
        return "media"
    return "baixa"


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
    nome = paciente.nome if paciente and paciente.nome else f"Paciente #{prontuario}"

    return {
        "id": row.solicitacao,
        "solicitacao": row.solicitacao,
        "prontuario": prontuario,
        "nome": nome,
        "exames": [exame_nome],
        "diasNaFila": dias_na_fila,
        "status": _prioridade(sol.unidade_solicitante if sol else ""),
        "unidadeSolicitante": sol.unidade_solicitante if sol else None,
        "dataRetorno": sol.data_retorno.isoformat() if sol and sol.data_retorno else None,
        "localizacao": localizacao,
        "idade": idade,
    }


# Retorna a fila geral: um card por exame, ordenados pelo algoritmo de pontuação
async def listar_agendamentos(provider: FuncionarioLocalProvider, limit: Optional[int] = None, busca: Optional[str] = None) -> List[dict]:
    rows = await provider.listar_pendentes(busca=busca)
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
    if limit is not None:
        items = items[:limit]
    return items


# Atribui um agendamento PENDENTE ao funcionário logado, mudando o status para EM_ANDAMENTO
async def puxar_agendamento(solicitacao_id: int, provider: FuncionarioLocalProvider, username: str, nome: Optional[str] = None) -> dict:
    funcionario = await provider.get_or_create_funcionario(username, nome)
    rows = await provider.buscar_por_solicitacao(
        solicitacao_id, funcionario_id=None, status=StatusAtribuicao.PENDENTE
    )
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado ou já atribuído")
    await provider.atribuir(rows, funcionario.id)
    return {"mensagem": "Agendamento atribuído com sucesso"}


# Retorna os agendamentos do funcionário logado em qualquer estado (EM_ANDAMENTO, AGUARDANDO_CONFIRMACAO, FINALIZADO)
async def listar_minha_area(provider: FuncionarioLocalProvider, username: str, nome: Optional[str] = None) -> List[dict]:
    funcionario = await provider.get_or_create_funcionario(username, nome)
    rows = await provider.listar_por_funcionario(funcionario.id)
    grupos = _agrupar_por_solicitacao(rows)
    items = []
    for grupo_rows in grupos.values():
        item = _build_item(grupo_rows)
        primeiro = grupo_rows[0]
        # Adiciona os campos extras do MinhaAreaItem: estado atual e resultado (se finalizado)
        item["estado"] = primeiro.status_atribuicao
        item["resultado"] = primeiro.resultado
        items.append(item)
    return items


# Avança o agendamento de EM_ANDAMENTO para AGUARDANDO_CONFIRMACAO
async def aguardar_confirmacao(solicitacao_id: int, provider: FuncionarioLocalProvider, username: str, nome: Optional[str] = None) -> dict:
    funcionario = await provider.get_or_create_funcionario(username, nome)
    # Só permite a transição se o agendamento estiver em EM_ANDAMENTO
    rows = await provider.buscar_por_solicitacao(solicitacao_id, funcionario.id, StatusAtribuicao.EM_ANDAMENTO)
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado em EM_ANDAMENTO")
    await provider.transicionar_status(rows, StatusAtribuicao.AGUARDANDO_CONFIRMACAO)
    return {"mensagem": "Agendamento movido para AGUARDANDO_CONFIRMACAO"}


# Remove o agendamento da área do funcionário e o devolve para a fila geral com status PENDENTE
async def devolver(solicitacao_id: int, motivo: str, provider: FuncionarioLocalProvider, username: str, nome: Optional[str] = None) -> dict:
    funcionario = await provider.get_or_create_funcionario(username, nome)
    rows = await provider.buscar_por_solicitacao(solicitacao_id, funcionario.id)
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado na sua área")
    await provider.devolver(rows, motivo)
    return {"mensagem": "Agendamento devolvido para a fila"}


# Finaliza o agendamento com PROBLEMA_REPORTADO, registrando motivo e detalhes para o administrador
async def reportar_problema(solicitacao_id: int, motivo: str, detalhes: Optional[str], provider: FuncionarioLocalProvider, username: str, nome: Optional[str] = None) -> dict:
    funcionario = await provider.get_or_create_funcionario(username, nome)
    rows = await provider.buscar_por_solicitacao(solicitacao_id, funcionario.id)
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado na sua área")
    await provider.transicionar_status(
        rows, StatusAtribuicao.FINALIZADO,
        resultado=ResultadoAtribuicao.PROBLEMA_REPORTADO,
        motivo=motivo, detalhes=detalhes
    )
    return {"mensagem": "Problema reportado e agendamento finalizado"}


# Encerra o ciclo do atendimento com resultado CONFIRMADO ou PROBLEMA_REPORTADO
async def finalizar(solicitacao_id: int, resultado: str, provider: FuncionarioLocalProvider, username: str, nome: Optional[str] = None) -> dict:
    # Valida se o resultado enviado é um dos valores permitidos pelo enum
    if resultado not in ResultadoAtribuicao._value2member_map_:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"resultado deve ser um de: {[r.value for r in ResultadoAtribuicao]}",
        )
    funcionario = await provider.get_or_create_funcionario(username, nome)
    rows = await provider.buscar_por_solicitacao(solicitacao_id, funcionario.id)
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado na sua área")
    await provider.transicionar_status(rows, StatusAtribuicao.FINALIZADO, resultado=ResultadoAtribuicao(resultado))
    return {"mensagem": f"Agendamento finalizado com resultado {resultado}"}
