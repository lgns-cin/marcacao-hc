from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

from .resources.database import DatabaseManager, Base

# IMPORTAÇÃO DO MÓDULO DE INGESTÃO AUTOMÁTICA
from .settlement.ingestao import ingerir_dados_se_vazio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")

    # Initialize AGHU DB Manager and store in app.state
    aghu_dsn = os.getenv("POSTGRES_DSN")
    if aghu_dsn:
        app.state.aghu_db = DatabaseManager(aghu_dsn)
        print("AGHU PostgreSQL connection pool initialized.")
    else:
        print("WARNING: POSTGRES_DSN not found. Skipping AGHU DB initialization.")

    # Initialize App DB Manager (SQLite) and store in app.state
    app_dsn = os.getenv("SQLITE_DSN")
    if not app_dsn:
        raise ValueError("SQLITE_DSN not found in environment variables.")
    app.state.app_db = DatabaseManager(app_dsn)
    print("App SQLite connection pool initialized.")

    # Create tables for App DB (if they don't exist)
    async with app.state.app_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("App SQLite tables checked/created.")

    # GATILHO DE INGESTÃO DE DADOS (Executado apenas em dev)
    env = os.getenv("ENV")
    if env == "development" and app_dsn:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        await ingerir_dados_se_vazio(app_dsn, project_root)

    yield
    
    # Shutdown
    print("Shutting down...")
    if hasattr(app.state, "aghu_db"):
        await app.state.aghu_db.close_connection()
    if hasattr(app.state, "app_db"):
        await app.state.app_db.close_connection()

app = FastAPI(lifespan=lifespan)

# Verifica se os diretórios do frontend construído existem antes de montá-los
frontend_dist = os.path.join("src", "static", "dist")
frontend_assets = os.path.join(frontend_dist, "assets")

if os.path.exists(frontend_assets):
    app.mount("/assets", StaticFiles(directory=frontend_assets), name="assets")
    
if os.path.exists(frontend_dist):
    app.mount("/static", StaticFiles(directory=frontend_dist), name="static")
else:
    print("Aviso: Diretórios de build do frontend não encontrados. (Normal em ambiente de desenvolvimento)")

# Placeholder para incluir os roteadores da API
from .routers import paciente, auth, admin, aih, bpa, material
app.include_router(paciente.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(aih.router)
app.include_router(bpa.router)
app.include_router(material.router)

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail="API route not found")
    
    index_path = os.path.join("src", "static", "dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Frontend not built. Run 'npm run build' in frontend directory.")