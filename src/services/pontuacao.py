"""
src/services/pontuacao.py

Módulo de priorização de solicitações de exame — CORTEx-HC.

Responsabilidade: receber dicionários com dados da solicitação e retornar uma pontuação numérica (0-100+). Não acessa banco, não faz chamadas HTTP. É chamado pelo controller após os providers buscarem os dados.

Contrato de entrada esperado pelo controller (dicionário plano):

    solicitacao = {
        "cidade": str,                 # ex: "Petrolina"
        "data_retorno": str | date,    # ex: "2026-07-10" (ISO 8601) ou objeto date
        "unidade_solicitante": str,    # ex: "UTI ADULTO"
        "data_solicitacao": str | date # ex: "2026-06-01" (ISO 8601) ou objeto date
    }
"""

from datetime import date, datetime

# ---------------------------------------------------------------------------
# Pesos 
# ---------------------------------------------------------------------------

PESO_DATA_RETORNO      = 40
PESO_URGENCIA          = 35
PESO_LOCALIDADE        = 15
BONUS_MAXIMO_ESPERA    = 20   # pontos extras máximos por tempo de espera
PESO_IDADE             = 10

DIAS_ESPERA_MAXIMO     = 60   # dias para atingir o bônus máximo


# ---------------------------------------------------------------------------
# Mapa de urgência por unidade solicitante
# Fonte: validado com Tati (HC-UFPE) em reunião de 12/06/2026.
# Unidades não listadas recebem valor padrão (DEFAULT_URGENCIA).
# Atualizar conforme formalização com a equipe clínica.
# ---------------------------------------------------------------------------

MAPA_URGENCIA: dict[str, float] = {
    "UTI ADULTO":                  1.0,
    "UTI PEDIÁTRICA":              1.0,
    "CENTRO OBSTÉTRICO":           0.9,
    "PRONTO-SOCORRO":              0.9,
    "EMERGÊNCIA":                  0.9,
    "VASCULAR":                    0.8,
    "ONCOLOGIA":                   0.8,
    "NEFROLOGIA (AMBULATÓRIO)":    0.7,
    "CARDIOLOGIA (AMBULATÓRIO)":   0.65,
    "PNEUMOLOGIA (AMBULATÓRIO)":   0.55,
    "GINECOLOGIA (AMBULATÓRIO)":   0.5,
    "ORTOPEDIA (AMBULATÓRIO)":     0.5,
}

DEFAULT_URGENCIA = 0.4  # unidades não mapeadas


# ---------------------------------------------------------------------------
# Municípios de Pernambuco por faixa de distância ao HC-UFPE (Recife)
# ---------------------------------------------------------------------------

MUNICIPIOS_REGIAO_METROPOLITANA = {
    "recife", "olinda", "virória de santo antão", "jaboatão", "jaboatão dos guararapes",
    "paulista", "camaragibe", "são lourenço da mata", "abreu e lima",
    "igarassu", "cabo de santo agostinho", "moreno", "ipojuca"
}

MUNICIPIOS_INTERIOR_PROXIMO = {
    "ipojuca", "caruaru", "carpina", "feira nova", "gravatá", "limoeiro"
}

MUNICIPIOS_INTERIOR_DISTANTE = {
    "petrolina", "araripina", "ouricuri", "salgueiro", "serra talhada",
    "floresta", "santa maria da boa vista", "lagoa grande", "orocó",
}

# Scores de localidade: quanto mais difícil chegar, menor a prioridade, para ficar para depois
SCORE_REGIAO_METROPOLITANA = 1.0
SCORE_INTERIOR_PROXIMO     = 0.6
SCORE_INTERIOR_DISTANTE    = 0.2

SCORE_DEFAULT = 0.4

# ---------------------------------------------------------------------------
# Transformacao da string para data
# ---------------------------------------------------------------------------

def _parse_date(valor) -> date:
    """Converte string ISO 8601 para objeto date, ou retorna o próprio date se já for um."""
    # Se o Provider já entregou um objeto date (ou datetime), devolvemos direto
    if isinstance(valor, date):
        # Apenas uma segurança: se for datetime (com hora), extraímos só a data
        if isinstance(valor, datetime):
            return valor.date()
        return valor

    # Se for string (como nos seus testes originais ou no CSV), mantém a sua lógica original
    return datetime.strptime(str(valor)[:10], "%Y-%m-%d").date()

# ---------------------------------------------------------------------------
# Funções auxiliares de score (cada uma retorna valor entre 0.0 e 1.0)
# ---------------------------------------------------------------------------

def score_data_retorno(data_retorno_str: str, hoje: date | None = None) -> float:
    """
    Quanto mais próxima a data de retorno, maior o score.
    - 0 dias restantes (atrasado ou hoje) → 1.0
    - 90 dias ou mais                     → 0.0
    """
    if hoje is None:
        hoje = date.today() # biblioteca padrão do Python que retorna a data atual do servidor

    try:
        data_retorno = _parse_date(data_retorno_str)
    except (ValueError, TypeError):
        return 0.0

    dias_restantes = (data_retorno - hoje).days
    if dias_restantes <= 0:
        return 1.0
    return max(0.0, 1.0 - (dias_restantes / 90))


def score_urgencia(unidade_solicitante: str) -> float:
    """
    Score baseado na unidade que originou a solicitação.
    !!!!!!!!!!!! Unidades não mapeadas recebem DEFAULT_URGENCIA.
    """
    if not unidade_solicitante:
        return DEFAULT_URGENCIA
    chave = unidade_solicitante.strip().upper()
    return MAPA_URGENCIA.get(chave, DEFAULT_URGENCIA)


def score_localidade(cidade: str) -> float:
    """
    Pacientes de municípios distantes têm maior dificuldade de deslocamento,
    portanto recebem score menos alto para evitar perda de vagas pela falta de planejamento.
    """
    if not cidade:
        return SCORE_INTERIOR_PROXIMO

    cidade_normalizada = cidade.strip().lower()

    if cidade_normalizada in MUNICIPIOS_REGIAO_METROPOLITANA:
        return SCORE_REGIAO_METROPOLITANA
    if cidade_normalizada in MUNICIPIOS_INTERIOR_DISTANTE:
        return SCORE_INTERIOR_DISTANTE
    if cidade_normalizada in MUNICIPIOS_INTERIOR_PROXIMO:
        return SCORE_INTERIOR_PROXIMO
    return SCORE_DEFAULT

PESO_IDADE = 10 

def score_idade(data_nascimento_str: str, hoje: date | None = None) -> float:
    """
    Pacientes mais velhos recebem prioridade maior.
    A pontuação cresce proporcionalmente até os 80 anos (onde atinge 1.0).
    """
    if not data_nascimento_str:
        return 0.0

    if hoje is None:
        hoje = date.today()

    try:
        data_nasc = _parse_date(data_nascimento_str)
    except (ValueError, TypeError):
        return 0.0

    # Calcula a idade exata
    idade = hoje.year - data_nasc.year - (
        (hoje.month, hoje.day) < (data_nasc.month, data_nasc.day)
    )

    if idade < 0: return 0.0
    if idade >= 80: return 1.0
    
    return round(idade / 80.0, 2)

def bonus_tempo_espera(data_solicitacao: str, hoje: date | None = None) -> float:
    """
    Bônus adicional (não normalizado) que cresce com o tempo de espera.
    Evita que um paciente fique indefinidamente despriorizado.

    Retorna entre 0 e BONUS_MAXIMO_ESPERA pontos.
    """
    if hoje is None:
        hoje = date.today()

    try:
        data_entrada = _parse_date(data_solicitacao)
    except (ValueError, TypeError):
        return 0.0

    dias_esperando = (hoje - data_entrada).days
    proporcao = min(1.0, dias_esperando / DIAS_ESPERA_MAXIMO)
    return proporcao * BONUS_MAXIMO_ESPERA


# ---------------------------------------------------------------------------
# Função principal de pontuação
# ---------------------------------------------------------------------------

def calcular_pontuacao(paciente: dict, solicitacao: dict) -> float:
    """
    Calcula a pontuação de prioridade de uma solicitação.
    Recebe dois dicionários separados para manter compatibilidade com o Controller.

    Quanto maior o valor retornado, maior a prioridade na fila.
    Pontuação base: 0-100. Bônus de tempo de espera pode ultrapassar 100.

    Args:
        paciente:    dict com "cidade" e "data_nascimento"
        solicitacao: dict com "data_retorno", "unidade_solicitante", "data_solicitacao"

    Returns:
        float com a pontuação final.
    """
    hoje = date.today()

    score_base = (
        score_data_retorno(solicitacao.get("data_retorno", ""), hoje)   * PESO_DATA_RETORNO +
        score_urgencia(solicitacao.get("unidade_solicitante", ""))      * PESO_URGENCIA +
        score_localidade(paciente.get("cidade", ""))                    * PESO_LOCALIDADE +
        score_idade(paciente.get("data_nascimento", ""), hoje)          * PESO_IDADE
    )

    bonus = bonus_tempo_espera(solicitacao.get("data_solicitacao", ""), hoje)

    return round(score_base + bonus, 2)


# ---------------------------------------------------------------------------
# Ordenação da fila
# ---------------------------------------------------------------------------

def ordenar_fila(solicitacoes: list[dict]) -> list[dict]:
    """
    Recebe lista de solicitações pendentes, calcula a pontuação de cada uma
    e retorna a lista ordenada por prioridade (maior pontuação primeiro).

    Exemplo de item esperado na lista:
        {
            "id": 42,
            "data_retorno": "2026-07-10",
            "unidade_solicitante": "UTI ADULTO",
            "data_solicitacao": "2026-06-01",
            "paciente": {
                "cidade": "Petrolina",
                "data_nascimento": "1950-05-20"
            }
        }
    """
    for s in solicitacoes:
        # Extrai o dicionário do paciente de dentro do item, ou cria um vazio caso não exista
        paciente_dict = s.get("paciente", {})
        
        # Passa os dois dicionários separados, respeitando a assinatura da calcular_pontuacao
        s["pontuacao"] = calcular_pontuacao(paciente_dict, s)

    return sorted(solicitacoes, key=lambda x: x["pontuacao"], reverse=True)