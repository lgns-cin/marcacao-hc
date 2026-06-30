from typing import Optional

from ..helpers.texto import normalizar

# Fonte única de verdade do mapeamento código do exame -> tipo (categoria).
# O AGHU/banco só guarda o código e o nome do exame; o "tipo" é uma categoria
# nossa, usada nos filtros e na agregação do ranking do dashboard.
#
# Para acrescentar um novo código ou tipo, basta editar este dicionário.
# Mantém paridade com o `EXAMES_IMAGEM` de forms_controller.py (21 códigos).
CATALOGO_EXAMES: dict[str, str] = {
    "TCABI": "Tomografia",
    "TCABC": "Tomografia",
    "TCAVT": "Tomografia",
    "TCTX1": "Tomografia",
    "RXMM1": "Mamografia",
    "RXAB6": "Raio-X",
    "RXPAP": "Raio-X",
    "RXTX1": "Raio-X",
    "RXTX4": "Raio-X",
    "EDA": "Endoscopia",
    "CLN": "Colonoscopia",
    "ECO": "Ecocardiograma",
    "USABT": "Ultrassonografia",
    "USTDO": "Ultrassonografia",
    "USIDA": "Ultrassonografia",
    "USIDV": "Ultrassonografia",
    "USIEA": "Ultrassonografia",
    "USIEV": "Ultrassonografia",
    "USGOD": "Ultrassonografia",
    "ERGO": "Ergometria",
    "ESPB": "Espirometria",
}


def tipo_do_exame(codigo: Optional[str]) -> Optional[str]:
    """Retorna o tipo (categoria) de um código de exame, ou None se desconhecido."""
    if not codigo:
        return None
    return CATALOGO_EXAMES.get(codigo.strip().upper())


def exame_e_do_tipo(codigo: Optional[str], tipos: set[str]) -> bool:
    """Indica se o exame pertence a algum dos tipos informados.

    A comparação ignora acentos e caixa para tolerar variações vindas do front
    (ex.: "raio-x" / "Raio-X").
    """
    tipo = tipo_do_exame(codigo)
    if tipo is None:
        return False
    return normalizar(tipo) in {normalizar(t) for t in tipos}
