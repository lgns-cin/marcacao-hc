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


# Agrupa os registros de ExameSolicitado pelo código da solicitação,
# pois uma solicitação pode ter múltiplos exames e precisa aparecer como um card só
def _agrupar_por_solicitacao(rows) -> dict:
    grupos: dict = {}
    for row in rows:
        grupos.setdefault(row.solicitacao, []).append(row)
    return grupos


# Monta o dicionário AgendamentoItem a partir de um grupo de exames da mesma solicitação
def _build_item(rows: list) -> dict:
    first = rows[0]
    paciente = first.paciente
    sol = first.solicitacao_rel

    # Dias na fila: diferença entre hoje e a data de entrada mais antiga do grupo
    datas = [r.data_solicitacao for r in rows if r.data_solicitacao]
    dias_na_fila = (date.today() - min(datas)).days if datas else 0

    # Lista de nomes dos exames do grupo
    exames = [r.exame_rel.nome if r.exame_rel else r.exame for r in rows]

    localizacao = None
    if paciente and paciente.cidade:
        localizacao = f"{paciente.cidade}, {paciente.estado}" if paciente.estado else paciente.cidade

    # Idade calculada a partir de data_nascimento; None se não disponível
    idade = None
    if paciente and paciente.data_nascimento:
        hoje = date.today()
        idade = hoje.year - paciente.data_nascimento.year - (
            (hoje.month, hoje.day) < (paciente.data_nascimento.month, paciente.data_nascimento.day)
        )

    return {
        "id": first.solicitacao,
        "prontuario": str(first.paciente_solicitante),
        "nome": None,  # nome do paciente vem do AGHU, não disponível localmente
        "exames": exames,
        "diasNaFila": dias_na_fila,
        "status": _prioridade(sol.unidade_solicitante if sol else ""),
        "unidadeSolicitante": sol.unidade_solicitante if sol else None,
        "dataRetorno": sol.data_retorno.isoformat() if sol and sol.data_retorno else None,
        "localizacao": localizacao,
        "idade": idade,
    }


# Retorna a fila geral: todos os agendamentos com status PENDENTE, ordenados pelo algoritmo de pontuação
async def listar_agendamentos(provider: FuncionarioLocalProvider) -> List[dict]:
    rows = await provider.listar_pendentes()
    grupos = _agrupar_por_solicitacao(rows)
    items = []
    for grupo_rows in grupos.values():
        item = _build_item(grupo_rows)
        first = grupo_rows[0]
        sol = first.solicitacao_rel
        paciente = first.paciente
        # Calcula pontuação usando o serviço da Mirela para ordenar a fila
        item["_pontuacao"] = calcular_pontuacao(
            {"cidade": paciente.cidade if paciente else ""},
            {
                "data_retorno": sol.data_retorno.isoformat() if sol and sol.data_retorno else "",
                "unidade_solicitante": sol.unidade_solicitante if sol else "",
                "data_solicitacao": first.data_solicitacao.isoformat() if first.data_solicitacao else "",
            }
        )
        items.append(item)
    items.sort(key=lambda x: x.pop("_pontuacao"), reverse=True)
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
