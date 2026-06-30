# Catálogo de mapeamento entre código de exame e tipo/categoria.

CODIGO_PARA_TIPO: dict[str, str] = {
    # Tomografia
    "TCABI": "Tomografia",
    "TCABC": "Tomografia",
    "TCAVT": "Tomografia",
    "TCTX1": "Tomografia",
    # Mamografia
    "RXMM1": "Mamografia",
    # Raio-X
    "RXAB6": "Raio-X",
    "RXPAP": "Raio-X",
    "RXTX1": "Raio-X",
    "RXTX4": "Raio-X",
    # Endoscopia
    "EDA": "Endoscopia",
    # Colonoscopia
    "CLN": "Colonoscopia",
    # Ecocardiograma
    "ECO": "Ecocardiograma",
    # Ultrassonografia
    "USABT": "Ultrassonografia",
    "USTDO": "Ultrassonografia",
    "USIDA": "Ultrassonografia",
    "USIDV": "Ultrassonografia",
    "USIEA": "Ultrassonografia",
    "USIEV": "Ultrassonografia",
    "USGOD": "Ultrassonografia",
    # Ergometria
    "ERGO": "Ergometria",
    # Espirometria
    "ESPB": "Espirometria",
}

# Índice inverso: tipo -> conjunto de códigos (construído uma vez em tempo de importação)
TIPO_PARA_CODIGOS: dict[str, set[str]] = {}
for _codigo, _tipo in CODIGO_PARA_TIPO.items():
    TIPO_PARA_CODIGOS.setdefault(_tipo, set()).add(_codigo)


def codigos_para_tipos(tipos: list[str]) -> set[str]:
    """
    Recebe uma lista de tipos (ex: ['Tomografia', 'Raio-X'])
    e retorna o conjunto de códigos correspondentes.
    Tipos desconhecidos são ignorados silenciosamente.
    """
    resultado: set[str] = set()
    for tipo in tipos:
        resultado.update(TIPO_PARA_CODIGOS.get(tipo, set()))
    return resultado