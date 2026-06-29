"""
Helpers de filtragem compartilhados entre FuncionarioController e AdminController.

Todos os filtros operam sobre objetos ExameSolicitado já carregados em memória
(com seus relacionamentos selectinload'd), portanto não há custo extra de query —
o custo é apenas de iteração Python, que é negligível para os volumes esperados.

Se no futuro o volume justificar, os filtros de município e faixa-etária podem ser
empurrados para o WHERE da query SQL sem mudar a assinatura desta API.
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


def _paciente_na_faixa(paciente, faixa: str) -> bool:
    """
    Retorna True se o paciente pertence à faixa etária informada.
    Pacientes sem data_nascimento são excluídos quando a faixa é especificada.
    """
    if not paciente or not paciente.data_nascimento:
        return False
    limites = FAIXAS_ETARIAS.get(faixa)
    if limites is None:
        return True  # faixa desconhecida → não filtra
    idade = _calcular_idade(paciente.data_nascimento)
    return limites[0] <= idade <= limites[1]


# Município

def _paciente_no_municipio(paciente, municipio_normalizado: str) -> bool:
    """
    Retorna True se a cidade do paciente começa com o texto informado
    (comparação sem acento, case-insensitive).
    """
    if not paciente or not paciente.cidade:
        return False
    return normalizar(paciente.cidade).startswith(municipio_normalizado)


# Região

def _paciente_na_regiao(paciente, regioes: set[str]) -> bool:
    """
    Retorna True se a região inferida do município do paciente estiver
    no conjunto de regiões solicitado.
    """
    if not paciente or not paciente.cidade:
        # Sem cidade → só inclui se 'Fora do Estado' foi solicitado
        return "Fora do Estado" in regioes
    regiao = municipio_para_regiao(paciente.cidade)
    return regiao in regioes


# Tipo de exame

def _row_no_tipo_exame(row, codigos_permitidos: set[str]) -> bool:
    """Retorna True se o código do exame do row pertence ao conjunto solicitado."""
    return row.exame in codigos_permitidos


# Função principal

def aplicar_filtros(
    rows: list,
    *,
    regioes: Optional[list[str]] = None,
    municipio: Optional[str] = None,
    faixa_etaria: Optional[str] = None,
    tipos_exame: Optional[list[str]] = None,
) -> list:
    """
    Filtra uma lista de objetos ExameSolicitado (com relacionamentos carregados)
    aplicando os critérios fornecidos.

    Cada critério não-nulo reduz o conjunto (AND entre critérios).
    Dentro de regioes e tipos_exame, múltiplos valores são OR.

    Parâmetros
    ----------
    rows          : lista de ExameSolicitado com .paciente e .exame carregados
    regioes       : ex. ['Agreste', 'Sertão']
    municipio     : texto livre (ex. 'Reci') — busca por prefixo, sem acento
    faixa_etaria  : 'menor_idade' | 'adulto' | 'idoso'
    tipos_exame   : ex. ['Tomografia', 'Raio-X']
    """

    # Pré-computar valores normalizados / conjuntos para evitar recalcular por row

    regioes_set: Optional[set[str]] = set(regioes) if regioes else None

    municipio_norm: Optional[str] = normalizar(municipio) if municipio else None

    codigos_exame: Optional[set[str]] = (
        codigos_para_tipos(tipos_exame) if tipos_exame else None
    )

    resultado = []
    for row in rows:
        paciente = row.paciente

        if regioes_set is not None:
            if not _paciente_na_regiao(paciente, regioes_set):
                continue

        if municipio_norm is not None:
            if not _paciente_no_municipio(paciente, municipio_norm):
                continue

        if faixa_etaria is not None:
            if not _paciente_na_faixa(paciente, faixa_etaria):
                continue

        if codigos_exame is not None:
            if not _row_no_tipo_exame(row, codigos_exame):
                continue

        resultado.append(row)

    return resultado