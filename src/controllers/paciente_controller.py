from typing import List, Dict, Any

from fastapi import HTTPException, status

from ..providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from ..providers.interfaces.aghu_provider_interface import AghuProviderInterface

async def listar_pacientes(
    provider: PacienteProviderInterface
) -> List[Dict[str, Any]]:
    return await provider.listar_pacientes()

async def obter_paciente_por_codigo(
    codigo: int,
    provider: PacienteProviderInterface
) -> Dict[str, Any]:
    return await provider.obter_paciente_por_codigo(codigo)


async def validar_prontuario(
    numero_prontuario: int,
    provider: AghuProviderInterface
) -> Dict[str, Any]:
    existe = await provider.verificar_prontuario_existe(numero_prontuario)
    if not existe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prontuário não encontrado no AGHU"
        )
    return {"prontuario": numero_prontuario, "exists": True}


async def consultar_exames_solicitacao(
    numero_prontuario: int,
    numero_solicitacao: int,
    provider: AghuProviderInterface
) -> Dict[str, Any]:
    exames = await provider.buscar_exames_solicitacao(
        numero_prontuario,
        numero_solicitacao
    )
    if not exames:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada ou não pertence a este prontuário"
        )

    exames_imagem = [
        {
            "nome_exame": exame["nome_exame"],
            "tem_vagas": bool(exame["tem_vagas"]),
        }
        for exame in exames
        if str(exame.get("tipo_exame", "")).strip().lower() == "imagem"
    ]

    if not exames_imagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum exame de imagem encontrado para esta solicitação"
        )

    return {"exames": exames_imagem}
