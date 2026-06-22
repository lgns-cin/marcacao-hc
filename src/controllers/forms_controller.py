from datetime import date, timedelta
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.paciente import Paciente
from ..models.solicitacao import Solicitacao, FormularioPacienteRequest
from ..models.exame import Exame
from ..models.exame_solicitado import ExameSolicitado
from ..providers.interfaces.aghu_provider_interface import AghuProviderInterface


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

    # Dados fictícios para preencher a solicitação local
    data_retorno = date.today() + timedelta(days=30)
    unidade_solicitante = (
        "IMAGEM"
        if any(
            str(item.get("tipo_exame", "")).strip().lower() == "imagem"
            for item in exames_aghu
        )
        else "GERAL"
    )

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

    # Buscar exames no banco local para cada exame informado pelo usuário
    exames_confirmados: List[Exame] = []
    for exame_nome in payload.exames:
        exame_nome_limpo = exame_nome.strip()
        if not exame_nome_limpo:
            continue

        stmt_exame = select(Exame).where(func.lower(Exame.nome) == exame_nome_limpo.lower())
        result_exame = await db.execute(stmt_exame)
        exame_obj = result_exame.scalar_one_or_none()
        if exame_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exame '{exame_nome_limpo}' não encontrado no banco local"
            )
        exames_confirmados.append(exame_obj)

    # Evitar inserções duplicadas para o mesmo par solicitacao/exame
    stmt_existentes = select(ExameSolicitado.exame_codigo).where(
        ExameSolicitado.solicitacao_codigo == solicitacao.codigo
    )
    result_existentes = await db.execute(stmt_existentes)
    existentes = {row[0] for row in result_existentes.fetchall()}

    vinculos_existentes = set(existentes)
    novos_vinculos = set()

    for exame_obj in exames_confirmados:
        if exame_obj.codigo in vinculos_existentes or exame_obj.codigo in novos_vinculos:
            continue
        exame_solicitado = ExameSolicitado(
            solicitacao_codigo=solicitacao.codigo,
            exame_codigo=exame_obj.codigo,
            paciente_solicitante=payload.numero_prontuario,
            funcionario_atribuido=None,
            status_atribuicao="PENDENTE",
            data_atribuicao=None,
        )
        db.add(exame_solicitado)
        novos_vinculos.add(exame_obj.codigo)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return {
        "status": "sucesso",
        "mensagem": "Solicitação processada com sucesso"
    }
