from typing import Optional

from ..helpers.texto import normalizar

# Tabela de referência município -> região, gerada a partir das mesorregiões do
# IBGE de Pernambuco (UF 26). As mesorregiões do IBGE são renomeadas para os
# nomes amigáveis usados no front (ver frontend/src/shared/services/ibge.ts):
#
#   Metropolitana de Recife   -> Região Metropolitana
#   Agreste Pernambucano      -> Agreste
#   Mata Pernambucana         -> Zona da Mata
#   Sertão Pernambucano       -> Sertão
#   São Francisco Pernambucano-> São Francisco
#
# Assim evitamos consultar a API do IBGE a cada requisição (custoso) e mantemos
# a classificação de região idêntica à do front. As chaves estão normalizadas
# (sem acento, minúsculas) para a busca ser tolerante a variações de digitação.

REGIAO_METROPOLITANA = "Região Metropolitana"
AGRESTE = "Agreste"
ZONA_DA_MATA = "Zona da Mata"
SERTAO = "Sertão"
SAO_FRANCISCO = "São Francisco"
FORA_DO_ESTADO = "Fora do Estado"

REGIOES_VALIDAS: set[str] = {
    REGIAO_METROPOLITANA,
    AGRESTE,
    ZONA_DA_MATA,
    SERTAO,
    SAO_FRANCISCO,
    FORA_DO_ESTADO,
}

# Estados (UF) considerados "Pernambuco" para fins de classificação.
_ESTADOS_PE: set[str] = {normalizar("Pernambuco"), normalizar("PE")}

# 185 municípios de Pernambuco -> região (chave normalizada).
MUNICIPIO_REGIAO: dict[str, str] = {
    "abreu e lima": REGIAO_METROPOLITANA,
    "afogados da ingazeira": SERTAO,
    "afranio": SAO_FRANCISCO,
    "agrestina": AGRESTE,
    "alagoinha": AGRESTE,
    "alianca": ZONA_DA_MATA,
    "altinho": AGRESTE,
    "amaraji": ZONA_DA_MATA,
    "angelim": AGRESTE,
    "araripina": SERTAO,
    "aracoiaba": REGIAO_METROPOLITANA,
    "arcoverde": SERTAO,
    "barra de guabiraba": AGRESTE,
    "barreiros": ZONA_DA_MATA,
    "belo jardim": AGRESTE,
    "belem de maria": ZONA_DA_MATA,
    "belem do sao francisco": SAO_FRANCISCO,
    "betania": SERTAO,
    "bezerros": AGRESTE,
    "bodoco": SERTAO,
    "bom conselho": AGRESTE,
    "bom jardim": AGRESTE,
    "bonito": AGRESTE,
    "brejinho": SERTAO,
    "brejo da madre de deus": AGRESTE,
    "brejao": AGRESTE,
    "buenos aires": ZONA_DA_MATA,
    "buique": AGRESTE,
    "cabo de santo agostinho": REGIAO_METROPOLITANA,
    "cabrobo": SAO_FRANCISCO,
    "cachoeirinha": AGRESTE,
    "caetes": AGRESTE,
    "calumbi": SERTAO,
    "calcado": AGRESTE,
    "camaragibe": REGIAO_METROPOLITANA,
    "camocim de sao felix": AGRESTE,
    "camutanga": ZONA_DA_MATA,
    "canhotinho": AGRESTE,
    "capoeiras": AGRESTE,
    "carnaubeira da penha": SAO_FRANCISCO,
    "carnaiba": SERTAO,
    "carpina": ZONA_DA_MATA,
    "caruaru": AGRESTE,
    "casinhas": AGRESTE,
    "catende": ZONA_DA_MATA,
    "cedro": SERTAO,
    "cha grande": ZONA_DA_MATA,
    "cha de alegria": ZONA_DA_MATA,
    "condado": ZONA_DA_MATA,
    "correntes": AGRESTE,
    "cortes": ZONA_DA_MATA,
    "cumaru": AGRESTE,
    "cupira": AGRESTE,
    "custodia": SERTAO,
    "dormentes": SAO_FRANCISCO,
    "escada": ZONA_DA_MATA,
    "exu": SERTAO,
    "feira nova": AGRESTE,
    "fernando de noronha": REGIAO_METROPOLITANA,
    "ferreiros": ZONA_DA_MATA,
    "flores": SERTAO,
    "floresta": SAO_FRANCISCO,
    "frei miguelinho": AGRESTE,
    "gameleira": ZONA_DA_MATA,
    "garanhuns": AGRESTE,
    "gloria do goita": ZONA_DA_MATA,
    "goiana": ZONA_DA_MATA,
    "granito": SERTAO,
    "gravata": AGRESTE,
    "iati": AGRESTE,
    "ibimirim": SERTAO,
    "ibirajuba": AGRESTE,
    "igarassu": REGIAO_METROPOLITANA,
    "iguaracy": SERTAO,
    "ilha de itamaraca": REGIAO_METROPOLITANA,
    "inaja": SERTAO,
    "ingazeira": SERTAO,
    "ipojuca": REGIAO_METROPOLITANA,
    "ipubi": SERTAO,
    "itacuruba": SAO_FRANCISCO,
    "itambe": ZONA_DA_MATA,
    "itapetim": SERTAO,
    "itapissuma": REGIAO_METROPOLITANA,
    "itaquitinga": ZONA_DA_MATA,
    "itaiba": AGRESTE,
    "jaboatao dos guararapes": REGIAO_METROPOLITANA,
    "jaqueira": ZONA_DA_MATA,
    "jatauba": AGRESTE,
    "jatoba": SAO_FRANCISCO,
    "joaquim nabuco": ZONA_DA_MATA,
    "joao alfredo": AGRESTE,
    "jucati": AGRESTE,
    "jupi": AGRESTE,
    "jurema": AGRESTE,
    "lagoa grande": SAO_FRANCISCO,
    "lagoa de itaenga": ZONA_DA_MATA,
    "lagoa do carro": ZONA_DA_MATA,
    "lagoa do ouro": AGRESTE,
    "lagoa dos gatos": AGRESTE,
    "lajedo": AGRESTE,
    "limoeiro": AGRESTE,
    "macaparana": ZONA_DA_MATA,
    "machados": AGRESTE,
    "manari": SERTAO,
    "maraial": ZONA_DA_MATA,
    "mirandiba": SERTAO,
    "moreilandia": SERTAO,
    "moreno": REGIAO_METROPOLITANA,
    "nazare da mata": ZONA_DA_MATA,
    "olinda": REGIAO_METROPOLITANA,
    "orobo": AGRESTE,
    "oroco": SAO_FRANCISCO,
    "ouricuri": SERTAO,
    "palmares": ZONA_DA_MATA,
    "palmeirina": AGRESTE,
    "panelas": AGRESTE,
    "paranatama": AGRESTE,
    "parnamirim": SERTAO,
    "passira": AGRESTE,
    "paudalho": ZONA_DA_MATA,
    "paulista": REGIAO_METROPOLITANA,
    "pedra": AGRESTE,
    "pesqueira": AGRESTE,
    "petrolina": SAO_FRANCISCO,
    "petrolandia": SAO_FRANCISCO,
    "pombos": ZONA_DA_MATA,
    "pocao": AGRESTE,
    "primavera": ZONA_DA_MATA,
    "quipapa": ZONA_DA_MATA,
    "quixaba": SERTAO,
    "recife": REGIAO_METROPOLITANA,
    "riacho das almas": AGRESTE,
    "ribeirao": ZONA_DA_MATA,
    "rio formoso": ZONA_DA_MATA,
    "saire": AGRESTE,
    "salgadinho": AGRESTE,
    "salgueiro": SERTAO,
    "saloa": AGRESTE,
    "sanharo": AGRESTE,
    "santa cruz": SERTAO,
    "santa cruz da baixa verde": SERTAO,
    "santa cruz do capibaribe": AGRESTE,
    "santa filomena": SERTAO,
    "santa maria da boa vista": SAO_FRANCISCO,
    "santa maria do cambuca": AGRESTE,
    "santa terezinha": SERTAO,
    "serra talhada": SERTAO,
    "serrita": SERTAO,
    "sertania": SERTAO,
    "sirinhaem": ZONA_DA_MATA,
    "solidao": SERTAO,
    "surubim": AGRESTE,
    "sao benedito do sul": ZONA_DA_MATA,
    "sao bento do una": AGRESTE,
    "sao caitano": AGRESTE,
    "sao joaquim do monte": AGRESTE,
    "sao jose da coroa grande": ZONA_DA_MATA,
    "sao jose do belmonte": SERTAO,
    "sao jose do egito": SERTAO,
    "sao joao": AGRESTE,
    "sao lourenco da mata": REGIAO_METROPOLITANA,
    "sao vicente ferrer": AGRESTE,
    "tabira": SERTAO,
    "tacaimbo": AGRESTE,
    "tacaratu": SAO_FRANCISCO,
    "tamandare": ZONA_DA_MATA,
    "taquaritinga do norte": AGRESTE,
    "terezinha": AGRESTE,
    "terra nova": SAO_FRANCISCO,
    "timbauba": ZONA_DA_MATA,
    "toritama": AGRESTE,
    "tracunhaem": ZONA_DA_MATA,
    "trindade": SERTAO,
    "triunfo": SERTAO,
    "tupanatinga": AGRESTE,
    "tuparetama": SERTAO,
    "venturosa": AGRESTE,
    "verdejante": SERTAO,
    "vertente do lerio": AGRESTE,
    "vertentes": AGRESTE,
    "vicencia": ZONA_DA_MATA,
    "vitoria de santo antao": ZONA_DA_MATA,
    "xexeu": ZONA_DA_MATA,
    "agua preta": ZONA_DA_MATA,
    "aguas belas": AGRESTE,
}


def regiao_de(cidade: Optional[str], estado: Optional[str] = None) -> Optional[str]:
    """Infere a região de um paciente a partir do município (e do estado).

    - Se o estado for informado e não for Pernambuco, retorna "Fora do Estado".
    - Caso contrário, procura o município na tabela de referência. Município
      desconhecido (não pernambucano) também cai em "Fora do Estado".
    - Retorna None apenas quando não há município para classificar.
    """
    if estado and normalizar(estado) not in _ESTADOS_PE:
        return FORA_DO_ESTADO
    if not cidade:
        return None
    return MUNICIPIO_REGIAO.get(normalizar(cidade), FORA_DO_ESTADO)
