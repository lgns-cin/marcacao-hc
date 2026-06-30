import unicodedata
from typing import Optional


def normalizar(texto: Optional[str]) -> str:
    """Normaliza texto para comparações tolerantes a acentos e caixa.

    Remove acentos (NFKD), passa para minúsculas e tira espaços nas pontas.
    Usado nos filtros para que "São Caitano", "sao caitano" e "SAO CAITANO"
    sejam tratados como iguais.
    """
    if not texto:
        return ""
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return sem_acento.casefold().strip()
