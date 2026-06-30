from datetime import date
from typing import Iterable, Optional

from ..helpers.texto import normalizar
from .catalogo_exames import exame_e_do_tipo
from .regioes import regiao_de

# Faixas etárias aceitas pelo filtro. O front envia uma destas chaves e o
# backend calcula a idade do paciente para decidir se ele entra no recorte.
MENOR_IDADE = "menor_idade"  # 0 a 17 anos
ADULTO = "adulto"            # 18 a 59 anos
IDOSO = "idoso"              # 60 anos ou mais

FAIXAS_ETARIAS: tuple[str, ...] = (MENOR_IDADE, ADULTO, IDOSO)


def parse_lista(valor: Optional[str]) -> list[str]:
    """Converte um parâmetro separado por vírgula (ex.: "Agreste,Sertão") em lista.

    Tolera espaços e valores vazios: "Agreste, ,Sertão" -> ["Agreste", "Sertão"].
    """
    if not valor:
        return []
    return [item.strip() for item in valor.split(",") if item.strip()]


def calcular_idade(data_nascimento: Optional[date], hoje: Optional[date] = None) -> Optional[int]:
    """Idade em anos completos, ou None se não houver data de nascimento."""
    if data_nascimento is None:
        return None
    referencia = hoje or date.today()
    return referencia.year - data_nascimento.year - (
        (referencia.month, referencia.day) < (data_nascimento.month, data_nascimento.day)
    )


def classificar_faixa_etaria(
    data_nascimento: Optional[date], hoje: Optional[date] = None
) -> Optional[str]:
    """Classifica o paciente em menor_idade / adulto / idoso a partir da idade."""
    idade = calcular_idade(data_nascimento, hoje)
    if idade is None:
        return None
    if idade < 18:
        return MENOR_IDADE
    if idade < 60:
        return ADULTO
    return IDOSO


def _passa_regiao(row, regioes: set[str]) -> bool:
    paciente = row.paciente
    cidade = paciente.cidade if paciente else None
    estado = paciente.estado if paciente else None
    regiao = regiao_de(cidade, estado)
    if regiao is None:
        return False
    return normalizar(regiao) in regioes


def _passa_municipio(row, municipio_norm: str) -> bool:
    paciente = row.paciente
    cidade = normalizar(paciente.cidade) if paciente and paciente.cidade else ""
    # Aceita correspondência exata e prefixo (município "começa com" o texto).
    return cidade.startswith(municipio_norm)


def _passa_faixa_etaria(row, faixa: str, hoje: Optional[date]) -> bool:
    paciente = row.paciente
    nascimento = paciente.data_nascimento if paciente else None
    return classificar_faixa_etaria(nascimento, hoje) == faixa


def _passa_busca(row, termo_norm: str) -> bool:
    paciente = row.paciente
    cidade = paciente.cidade if paciente else None
    exame_nome = row.exame_rel.nome if row.exame_rel else None
    candidatos = (
        str(row.paciente_solicitante),
        row.exame,
        exame_nome,
        cidade,
    )
    return any(termo_norm in normalizar(c) for c in candidatos if c)


def aplicar_filtros(
    rows: Iterable,
    *,
    regioes: Optional[list[str]] = None,
    municipio: Optional[str] = None,
    tipos_exame: Optional[list[str]] = None,
    faixa_etaria: Optional[str] = None,
    busca: Optional[str] = None,
    hoje: Optional[date] = None,
) -> list:
    """Filtra registros de ExameSolicitado pelos critérios da fila/gestão.

    Cada filtro é opcional e combinado por E (AND). Listas (regiões, tipos de
    exame) combinam por OU (OR) internamente. Deve ser aplicado antes da
    pontuação/ordenação para que o `limit` recaia sobre o conjunto já filtrado.
    """
    regioes_norm = {normalizar(r) for r in regioes} if regioes else set()
    tipos_set = set(tipos_exame) if tipos_exame else set()
    municipio_norm = normalizar(municipio) if municipio else ""
    busca_norm = normalizar(busca) if busca else ""
    faixa = faixa_etaria or None

    resultado = []
    for row in rows:
        if regioes_norm and not _passa_regiao(row, regioes_norm):
            continue
        if municipio_norm and not _passa_municipio(row, municipio_norm):
            continue
        if tipos_set and not exame_e_do_tipo(row.exame, tipos_set):
            continue
        if faixa and not _passa_faixa_etaria(row, faixa, hoje):
            continue
        if busca_norm and not _passa_busca(row, busca_norm):
            continue
        resultado.append(row)
    return resultado
