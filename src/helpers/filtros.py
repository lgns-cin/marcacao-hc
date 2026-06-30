"""
Helpers de filtragem compartilhados entre FuncionarioController e AdminController.
"""

import unicodedata
from datetime import date
from typing import Optional

from ..resources.catalogo_exames import codigos_para_tipos
from ..resources.regioes_pe import municipio_para_regiao, normalizar


# Faixa etária

FAIXAS_ETARIAS = {
    "menor_idade": (0, 17),
    "adulto": (18, 59),
    "idoso": (60, 999),
}


def _calcular_idade(data_nascimento: date) -> int:
    hoje = date.today()
    return (
        hoje.year
        - data_nascimento.year
        - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
    )


def _na_faixa(data_nascimento, faixa: str) -> bool:
    """
    Retorna True se a data de nascimento informada pertence à faixa etária dada.
    Ausência de data_nascimento exclui o item quando uma faixa é especificada.
    """
    if not data_nascimento:
        return False
    limites = FAIXAS_ETARIAS.get(faixa)
    if limites is None:
        return True  # faixa desconhecida → não filtra
    idade = _calcular_idade(data_nascimento)
    return limites[0] <= idade <= limites[1]


# Município

def _no_municipio(cidade, municipio_normalizado: str) -> bool:
    """
    Retorna True se a cidade informada começa com o texto pedido
    (comparação sem acento, case-insensitive).
    """
    if not cidade:
        return False
    return normalizar(cidade).startswith(municipio_normalizado)


# Região

def _na_regiao(cidade, regioes: set[str]) -> bool:
    """
    Retorna True se a região inferida da cidade informada estiver
    no conjunto de regiões solicitado.
    """
    if not cidade:
        # Sem cidade → só inclui se 'Fora do Estado' foi solicitado
        return "Fora do Estado" in regioes
    regiao = municipio_para_regiao(cidade)
    return regiao in regioes


# Tipo de exame

def _no_tipo_exame(codigo_exame, codigos_permitidos: set[str]) -> bool:
    """Retorna True se o código de exame informado pertence ao conjunto solicitado."""
    return codigo_exame in codigos_permitidos


# Extração de dados

def _extrair_dados(item) -> dict:
    """
    Extrai cidade, data_nascimento e código do exame de um item,
    aceitando tanto objetos ExameSolicitado (ORM) quanto dicts já montados
    (que devem trazer os campos _cidade, _data_nascimento, _codigo_exame).
    """
    if isinstance(item, dict):
        return {
            "cidade": item.get("_cidade"),
            "data_nascimento": item.get("_data_nascimento"),
            "codigo_exame": item.get("_codigo_exame"),
        }
    paciente = item.paciente
    return {
        "cidade": paciente.cidade if paciente else None,
        "data_nascimento": paciente.data_nascimento if paciente else None,
        "codigo_exame": item.exame,
    }


# Função principal

def aplicar_filtros(
    items: list,
    *,
    regioes: Optional[list[str]] = None,
    municipio: Optional[str] = None,
    faixa_etaria: Optional[str] = None,
    tipos_exame: Optional[list[str]] = None,
) -> list:
    """
    Filtra uma lista de itens, tanto objetos ExameSolicitado (ORM) quanto
    dicts já montados via _build_item (com os campos _cidade, _data_nascimento
    e _codigo_exame), aplicando os critérios fornecidos.

    Cada critério não-nulo reduz o conjunto (AND entre critérios).
    Dentro de regioes e tipos_exame, múltiplos valores são OR.

    Parâmetros
    ----------
    items         : lista de ExameSolicitado (ORM) ou dicts com campos _cidade,
                     _data_nascimento, _codigo_exame
    regioes       : ex. ['Agreste', 'Sertão']
    municipio     : texto livre (ex. 'Reci') — busca por prefixo, sem acento
    faixa_etaria  : 'menor_idade' | 'adulto' | 'idoso'
    tipos_exame   : ex. ['Tomografia', 'Raio-X']
    """

    # Pré-computar valores normalizados / conjuntos para evitar recalcular por item

    regioes_set: Optional[set[str]] = set(regioes) if regioes else None

    municipio_norm: Optional[str] = normalizar(municipio) if municipio else None

    codigos_exame: Optional[set[str]] = (
        codigos_para_tipos(tipos_exame) if tipos_exame else None
    )

    resultado = []
    for item in items:
        dados = _extrair_dados(item)

        if regioes_set is not None:
            if not _na_regiao(dados["cidade"], regioes_set):
                continue

        if municipio_norm is not None:
            if not _no_municipio(dados["cidade"], municipio_norm):
                continue

        if faixa_etaria is not None:
            if not _na_faixa(dados["data_nascimento"], faixa_etaria):
                continue

        if codigos_exame is not None:
            if not _no_tipo_exame(dados["codigo_exame"], codigos_exame):
                continue

        resultado.append(item)

    return resultado