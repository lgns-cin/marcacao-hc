import unicodedata
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.paciente import Paciente
from ..models.solicitacao import Solicitacao, FormularioPacienteRequest
from ..models.exame import Exame
from ..models.exame_solicitado import ExameSolicitado
from ..providers.interfaces.aghu_provider_interface import AghuProviderInterface

EXAMES_IMAGEM = {
    "CLN", "EDA", "ECO", "RXMM1", 
    "RXAB6", "RXPAP", "RXTX1", "RXTX4", "ERGO",
    "USABT", "USTDO", "USIDA", "USIDV", "USIEA", "USIEV", "USGOD",
    "TCABI", "TCABC", "TCAVT", "TCTX1", "ESPB",
}


def _normalize_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    return "".join(
        char for char in normalized if unicodedata.category(char) != "Mn"
    ).strip().lower()


async def validar_prontuario(
    numero_prontuario: int,
    provider: AghuProviderInterface
) -> bool:
    existe = await provider.verificar_prontuario_existe(numero_prontuario)
    if not existe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prontuário não encontrado no AGHU"
        )
    return True


async def consultar_exames_solicitacao(
    numero_prontuario: int,
    numero_solicitacao: int,
    db: AsyncSession,
    provider: AghuProviderInterface
) -> Dict[str, Any]:
    existe_solic = await provider.verificar_solicitacao_existe(
        numero_solicitacao
    )

    if not existe_solic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada no AGHU"
        )

    exames = await provider.buscar_exames_solicitacao(
        numero_prontuario,
        numero_solicitacao
    )

    if not exames:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Solicitação não pertence a este prontuário"
        )

    exames_imagem = [
        exame
        for exame in exames
        if str(exame.get("codigo_exame", "")).strip().upper() in EXAMES_IMAGEM
    ]

    if not exames_imagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum exame de imagem encontrado para esta solicitação"
        )

    nomes_exames = [str(exame.get("nome_exame", "")).strip() for exame in exames_imagem]
    nomes_normalizados = [
        _normalize_name(nome)
        for nome in nomes_exames
        if nome
    ]

    stmt_exames = select(Exame).where(func.lower(Exame.nome).in_(nomes_normalizados))
    result_exames = await db.execute(stmt_exames)
    exames_locais = result_exames.scalars().all()
    mapping_codigo = {
        _normalize_name(exame.nome): exame.codigo
        for exame in exames_locais
        if exame.nome
    }

    nomes_faltando = [
        nome_norm
        for nome_norm in nomes_normalizados
        if nome_norm not in mapping_codigo
    ]

    # Se e o nome faz parte dos exames aceitos (imagem), adicionamos no bd local
    if nomes_faltando:
        for exame in exames_imagem:
            nome_exame = str(exame.get("nome_exame", "")).strip()
            nome_norm = _normalize_name(nome_exame)
            if nome_norm not in nomes_faltando:
                continue

            codigo_exame = str(exame.get("codigo_exame", "")).strip()
            if not codigo_exame:
                continue

            novo_exame = Exame(codigo=codigo_exame, nome=nome_exame)
            db.add(novo_exame)
            mapping_codigo[nome_norm] = codigo_exame
            nomes_faltando.remove(nome_norm)

        await db.flush()

    stmt_vagas = select(ExameSolicitado.exame).where(
        ExameSolicitado.solicitacao == numero_solicitacao,
        ExameSolicitado.paciente_solicitante == numero_prontuario,
    )
    result_vagas = await db.execute(stmt_vagas)
    exames_na_fila = {row[0] for row in result_vagas.fetchall()}

    exames_com_status = []
    for exame in exames_imagem:
        codigo_exame = mapping_codigo[_normalize_name(str(exame.get("nome_exame", "")))]
        tem_vagas = bool(exame.get("tem_vagas", False))
        if codigo_exame in exames_na_fila:
            status_vaga = "DUPLICADO"
        elif tem_vagas:
            status_vaga = "DISPONÍVEL"
        else:
            status_vaga = "INDISPONÍVEL"
        

        exames_com_status.append({
            "codigo_exame": codigo_exame,
            "nome_exame": exame.get("nome_exame"),
            "status_vaga": status_vaga,
        })

    return {"exames": exames_com_status}


async def processar_formulario_paciente(
    payload: FormularioPacienteRequest,
    db: AsyncSession,
    aghu_provider: AghuProviderInterface
) -> dict:
    # Upsert do paciente local
    stmt_paciente = select(Paciente).where(Paciente.prontuario == payload.numero_prontuario)
    result_paciente = await db.execute(stmt_paciente)
    paciente = result_paciente.scalar_one_or_none()

    if paciente is None:
        paciente = Paciente(
            prontuario=payload.numero_prontuario,
            telefone=payload.telefone,
            cidade=payload.cidade,
            estado=payload.estado,
        )
        db.add(paciente)
    else:
        paciente.telefone = payload.telefone
        paciente.cidade = payload.cidade
        paciente.estado = payload.estado

    # Buscar dados da solicitação no AGHU
    exames_aghu = await aghu_provider.buscar_exames_solicitacao(
        payload.numero_prontuario,
        payload.numero_solicitacao
    )

    data_retorno: Optional[date] = None
    unidade_solicitante: Optional[str] = None
    if exames_aghu:
        primeiro_exame = exames_aghu[0]
        raw_data_retorno = primeiro_exame.get("data_retorno")

        if isinstance(raw_data_retorno, date):
            data_retorno = raw_data_retorno
        elif isinstance(raw_data_retorno, str):
            try:
                data_retorno = date.fromisoformat(raw_data_retorno)
            except ValueError:
                data_retorno = None

        unidade_solicitante = str(primeiro_exame.get("unidade_solicitante") or "").strip() or None

    if data_retorno is None:
        data_retorno = date.today() + timedelta(days=30)

    if not unidade_solicitante:
        unidade_solicitante = "NÃO INFORMADO"

    stmt_solicitacao = select(Solicitacao).where(Solicitacao.codigo == payload.numero_solicitacao)
    result_solicitacao = await db.execute(stmt_solicitacao)
    solicitacao = result_solicitacao.scalar_one_or_none()

    if solicitacao is None:
        solicitacao = Solicitacao(
            codigo=payload.numero_solicitacao,
            data_retorno=data_retorno,
            unidade_solicitante=unidade_solicitante,
        )
        db.add(solicitacao)
    else:
        solicitacao.data_retorno = data_retorno
        solicitacao.unidade_solicitante = unidade_solicitante

    # Persistir paciente e solicitação antes de criar vínculos
    await db.flush()

    exames_confirmados: List[Exame] = []
    if payload.exames:
        payload_exame_codigos = [str(codigo) for codigo in payload.exames]
        stmt_exames = select(Exame).where(Exame.codigo.in_(payload_exame_codigos))
        result_exames = await db.execute(stmt_exames)
        exames_confirmados = result_exames.scalars().all()

        existentes_por_codigo = {str(exame.codigo): exame for exame in exames_confirmados}
        missing_codigos = [str(codigo) for codigo in payload.exames if str(codigo) not in existentes_por_codigo]

        for missing_codigo in missing_codigos:
            exame_nome = None
            for item in exames_aghu:
                if str(item.get("codigo_exame", "")).strip() == missing_codigo:
                    exame_nome = item.get("nome_exame")
                    break

            if exame_nome is None and len(exames_aghu) == 1:
                exame_nome = exames_aghu[0].get("nome_exame")

            exame_nome = str(exame_nome or f"Exame {missing_codigo}").strip()
            novo_exame = Exame(codigo=missing_codigo, nome=exame_nome)
            db.add(novo_exame)
            exames_confirmados.append(novo_exame)

    stmt_existentes = select(ExameSolicitado.exame).where(
        ExameSolicitado.solicitacao == solicitacao.codigo
    )
    result_existentes = await db.execute(stmt_existentes)
    existentes = {str(row[0]) for row in result_existentes.fetchall()}

    vinculos_existentes = set(existentes)
    novos_vinculos = set()

    for exame_obj in exames_confirmados:
        exame_codigo = str(exame_obj.codigo)
        if exame_codigo in vinculos_existentes or exame_codigo in novos_vinculos:
            continue
        exame_solicitado = ExameSolicitado(
            solicitacao=solicitacao.codigo,
            exame=exame_codigo,
            paciente_solicitante=payload.numero_prontuario,
            funcionario_atribuido=None,
            status_atribuicao="PENDENTE",
            data_atribuicao=None,
        )
        db.add(exame_solicitado)
        novos_vinculos.add(exame_codigo)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return {
        "status": "sucesso",
        "mensagem": "Solicitação processada com sucesso"
    }
