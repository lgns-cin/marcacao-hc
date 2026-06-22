import unicodedata
from typing import List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.exame import Exame
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
    db: AsyncSession,
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
        exame
        for exame in exames
        if str(exame.get("tipo_exame", "")).strip().lower() == "imagem"
    ]

    if not exames_imagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum exame de imagem encontrado para esta solicitação"
        )

    def normalize_name(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value or "")
        return "".join(
            char for char in normalized
            if unicodedata.category(char) != "Mn"
        ).strip().lower()

    nomes_exames = [str(exame.get("nome_exame", "")).strip() for exame in exames_imagem]
    nomes_normalizados = [normalize_name(nome) for nome in nomes_exames if nome]

    stmt_exames = select(Exame).where(func.lower(Exame.nome).in_(nomes_normalizados))
    result_exames = await db.execute(stmt_exames)
    exames_locais = result_exames.scalars().all()
    mapping_codigo = {
        normalize_name(exame.nome): exame.codigo
        for exame in exames_locais
        if exame.nome
    }

    if len(mapping_codigo) != len(set(nomes_normalizados)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alguns exames de imagem não estão cadastrados localmente"
        )

    exames_com_codigo = [
        {
            "codigo_exame": mapping_codigo[normalize_name(str(exame.get("nome_exame", "")))],
            "nome_exame": exame["nome_exame"],
            "tem_vagas": bool(exame["tem_vagas"]),
        }
        for exame in exames_imagem
    ]

    return {"exames": exames_com_codigo}
