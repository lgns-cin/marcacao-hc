import os
import pandas as pd
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.dialects.sqlite import insert

from src.resources.database import DatabaseManager
from src.models.paciente import Paciente
from src.models.exame import Exame
from src.models.funcionario import Funcionario
from src.models.solicitacao import Solicitacao
from src.models.exame_solicitado import ExameSolicitado

def chunk_list(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

async def ingerir_dados_se_vazio(db_url: str, project_root: str):
    sqlite_db_manager = DatabaseManager(db_url)

    # 1. Trava de Segurança
    async for session in sqlite_db_manager.get_session():
        resultado = await session.execute(select(func.count(Paciente.prontuario)))
        if resultado.scalar() > 0:
            print("[*] AppDB já populado. Ingestão ignorada.")
            return

    print("[*] AppDB vazio. Buscando arquivo dataset_mock_exames.csv...")

    # 2. Busca do arquivo
    caminho_csv = None
    for root, dirs, files in os.walk(project_root):
        if 'venv' in root or '.venv' in root or '__pycache__' in root:
            continue
        for file in files:
            if 'dataset_mock_exames' in file and file.endswith('.csv'):
                caminho_csv = os.path.join(root, file)
                break
        if caminho_csv:
            break

    if not caminho_csv:
        print("[!] ERRO: Arquivo 'dataset_mock_exames.csv' não encontrado. Abortando.")
        return

# 3. Leitura e Logs (Rastreamento)
    print(f"[*] Arquivo encontrado. Lendo: {caminho_csv}")
    df_raw = pd.read_csv(caminho_csv)
    print(f"[*] Total de linhas brutas no CSV: {len(df_raw)}")

    # --- INÍCIO DA NOVA LÓGICA DE FILTRAGEM ---
    # Substitua os códigos abaixo pelos códigos exatos que estão na sua imagem
    EXAMES_PERMITIDOS = [
        "CLN", "EDA", "ECO", "RXMM1", 
        "RXAB6", "RXPAP", "RXTX1", "RXTX4", "ERGO",
        "USABT", "USTDO", "USIDA", "USIDV", "USIEA", "USIEV", "USGOD",
        "TCABI", "TCABC", "TCAVT", "TCTX1", "ESPB"
    ]
    
    # Filtra o DataFrame para manter apenas as linhas que contêm os exames permitidos
    df_raw = df_raw[df_raw['codigo_exame'].isin(EXAMES_PERMITIDOS)]
    print(f"[*] Total de linhas após o filtro de exames: {len(df_raw)}")
    # --- FIM DA NOVA LÓGICA DE FILTRAGEM ---

    if 'data_retorno' in df_raw.columns:
        df_raw['data_retorno'] = pd.to_datetime(df_raw['data_retorno'], errors='coerce').dt.date

    hoje = datetime.now().date()

    # Mapeamento
    pacientes_records = df_raw[['prontuario', 'telefone', 'cidade', 'estado']].drop_duplicates(subset=['prontuario']).dropna(subset=['prontuario']).to_dict(orient='records')
    exames_records = df_raw[['codigo_exame', 'nome_exame']].drop_duplicates(subset=['codigo_exame']).dropna(subset=['codigo_exame']).rename(columns={'codigo_exame': 'codigo', 'nome_exame': 'nome'}).to_dict(orient='records')
    funcionarios_records = df_raw[['id_funcionario']].drop_duplicates(subset=['id_funcionario']).dropna(subset=['id_funcionario']).rename(columns={'id_funcionario': 'id'}).to_dict(orient='records')
    solicitacoes_records = df_raw[['codigo_solicitacao', 'data_retorno', 'unidade_solicitante']].drop_duplicates(subset=['codigo_solicitacao']).dropna(subset=['codigo_solicitacao']).rename(columns={'codigo_solicitacao': 'codigo'}).to_dict(orient='records')

    df_fatos = df_raw[['codigo_solicitacao', 'codigo_exame', 'prontuario', 'id_funcionario']].copy()
    df_fatos = df_fatos.dropna(subset=['codigo_solicitacao', 'codigo_exame', 'prontuario'])
    
    df_fatos['id_funcionario'] = None

    df_fatos = df_fatos.sample(frac=0.60, random_state=42)

    df_fatos = df_fatos.rename(columns={
        'codigo_solicitacao': 'solicitacao',
        'codigo_exame': 'exame',
        'prontuario': 'paciente_solicitante',
        'id_funcionario': 'funcionario_atribuido'
    })
    df_fatos['data_solicitacao'] = hoje
    df_fatos['status_atribuicao'] = 'PENDENTE'
    fatos_records = df_fatos.to_dict(orient='records')

    print(f"[*] Resumo dos dados a serem inseridos:")
    print(f"    - Pacientes: {len(pacientes_records)}")
    print(f"    - Exames: {len(exames_records)}")
    print(f"    - Funcionários: {len(funcionarios_records)}")
    print(f"    - Solicitações: {len(solicitacoes_records)}")
    print(f"    - Exames Solicitados (Associação): {len(fatos_records)}")

    if len(pacientes_records) == 0:
        print("[!] ERRO: O processamento resultou em 0 pacientes. Verifique o conteúdo do CSV.")
        return

    BATCH_SIZE = 200

    # 4. Inserção com Commit Explícito
    async for session in sqlite_db_manager.get_session():
        try:
            print("[*] Iniciando transação no banco de dados...")
            if pacientes_records:
                for batch in chunk_list(pacientes_records, BATCH_SIZE):
                    await session.execute(insert(Paciente).values(batch).on_conflict_do_nothing(index_elements=['prontuario']))
            if exames_records:
                for batch in chunk_list(exames_records, BATCH_SIZE):
                    await session.execute(insert(Exame).values(batch).on_conflict_do_nothing(index_elements=['codigo']))
            if funcionarios_records:
                for batch in chunk_list(funcionarios_records, BATCH_SIZE):
                    await session.execute(insert(Funcionario).values(batch).on_conflict_do_nothing(index_elements=['id']))
            if solicitacoes_records:
                for batch in chunk_list(solicitacoes_records, BATCH_SIZE):
                    await session.execute(insert(Solicitacao).values(batch).on_conflict_do_nothing(index_elements=['codigo']))
            if fatos_records:
                for batch in chunk_list(fatos_records, BATCH_SIZE):
                    await session.execute(insert(ExameSolicitado).values(batch))
            
            # COMANDO DE SALVAMENTO EXPLÍCITO
            await session.commit()
            print("[*] SUCESSO: O comando 'commit' foi executado. Os dados estão fisicamente salvos!")
        except Exception as e:
            await session.rollback()
            print(f"[!] ERRO CRÍTICO NA INSERÇÃO (Rollback executado): {e}")
            raise