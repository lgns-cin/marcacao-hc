# CLAUDE.md

## Projeto

Sistema de marcação de exames de imagem do HC-UFPE. Recebe solicitações de exame via formulário, valida contra o AGHU, aplica algoritmo de pontuação para ordenar a fila por prioridade, e exibe para os funcionários da Central de Marcação.

## Fonte de verdade

Antes de implementar qualquer funcionalidade, consultar os documentos de spec em `docs/spec/`:

- `01-visão.md` — problema, escopo, stakeholders
- `02-requisitos.md` — requisitos funcionais e não funcionais (RF101-RF307, RNF101-RNF301)
- `03-casos-de-uso.md` — fluxos de uso
- `04-modelo-de-dados.md` — modelo ER (Paciente, Solicitacao, Exame, Funcionario, ExameSolicitado)
- `05-interfaces.md` — protótipos e integrações
- `06-arquitetura.md` — stack, LGPD, RBAC
- `07-glossário.md` — termos (AGHU, TISS, AD, HIS)
- `SPEC.md` — contrato de desenvolvimento e task breakdown

Também consultar `GEMINI.md` na raiz para a estrutura de diretórios e arquitetura em camadas.

## Stack

- **Backend:** Python 3.13, FastAPI, Uvicorn
- **ORM:** SQLAlchemy 2.0 (async) + Alembic para migrations
- **Banco local:** SQLite via aiosqlite (dev), Postgres via asyncpg (AGHU)
- **Auth:** LDAP/Active Directory + JWT (PyJWT)
- **Frontend:** Vue 3, TypeScript, Vite, Tailwind CSS

## Arquitetura

Fluxo obrigatório: **SQL → Resource → Provider → Controller → Router**

```
src/
├── main.py                  # App FastAPI + lifespan
├── routers/                 # Rotas HTTP (define URLs)
├── controllers/             # Logica de negocio
├── providers/
│   ├── interfaces/          # Contratos (ABC)
│   └── implementations/    # CSV ou Postgres
├── services/                # Algoritmos puros (pontuacao)
├── models/                  # SQLAlchemy models (banco local)
├── resources/
│   ├── database.py          # DatabaseManager, Base, sessions
│   └── postgres.py          # Conexao AGHU
├── helpers/                 # Utilitarios
└── auth/                    # Autenticacao AD + JWT
```

## Providers e estrategia de dados

O sistema usa o pattern Strategy para chavear entre fontes de dados:
- `PACIENTE_PROVIDER_TYPE=CSV` — lê de `data/*.csv` (desenvolvimento)
- `PACIENTE_PROVIDER_TYPE=POSTGRES` — lê do banco AGHU (produção)

A fabrica está em `src/dependencies.py`. Cada provider implementa uma interface de `src/providers/interfaces/`.

## Modelo de dados (banco local)

Definido em `docs/spec/04-modelo-de-dados.md`. Entidades:
- **Paciente** (PK: prontuario) — telefone, cidade, estado
- **Solicitacao** (PK: codigo) — data_retorno, unidade_solicitante
- **Exame** (PK: codigo) — nome
- **Funcionario** (PK: id)
- **ExameSolicitado** (tabela associativa) — liga Solicitacao + Exame + Paciente + Funcionario

## Regras obrigatorias

- Usar ORM (SQLAlchemy), nunca SQL direto na aplicacao
- Soft delete (`deleted_at`) — proibido DELETE fisico
- Dados sensiveis criptografados (LGPD)
- Secrets no `.env`, nunca no codigo
- async/await em todo o backend
- Type hints em todas as funcoes
- snake_case em Python, camelCase em TypeScript

## Fluxo completo do sistema

O dado nasce no AGHU e precisa chegar até uma fila ordenada por prioridade. Cada camada é um passo desse caminho:

```
AGHU (dados brutos) → CSV (mock do AGHU) → Models (estrutura) → Pipeline (importação) → Providers (acesso) → Algoritmo (pontuação) → API (endpoint)
```

## Tasks de backend (redistribuição pra 6 pessoas, sem frontend)

### P1 — Models + Migrations ("A planta da casa")

**O que é:** Classes Python que descrevem a forma das tabelas do banco de dados. Cada model é uma tabela.

**O que entrega:** As 5 classes SQLAlchemy + Alembic migrations.

**Onde fica:** `src/models/`

**Na prática:**
```python
# src/models/paciente.py
class Paciente(Base):
    __tablename__ = "pacientes"
    prontuario = Column(Integer, primary_key=True)
    telefone = Column(String)
    cidade = Column(String)
    estado = Column(String)
```

Quando a aplicação sobe, o SQLAlchemy lê essa classe e cria a tabela `pacientes` no banco com essas colunas. Em vez de escrever `INSERT INTO pacientes (prontuario, cidade) VALUES (123, 'Recife')`, você faz:
```python
paciente = Paciente(prontuario=123, cidade="Recife")
session.add(paciente)
await session.commit()
```

**Por que existe:** Sem isso, não tem onde guardar os dados. É a fundação — tudo depende de saber qual é a estrutura.

**Orientação do orientador:** "Na pasta models/ devemos criar o modelo conceitual do nosso banco. A aplicação não deve usar SQL direto, e sim ORM — tratar os dados como objetos e chamar métodos pra salvar/consultar."

---

### P2 — Script Faker + CSVs Mock ("Dados fictícios que imitam o AGHU")

**O que é:** Um script Python que usa a biblioteca Faker pra gerar centenas de linhas de dados fictícios em arquivos CSV, imitando o formato real do AGHU.

**O que entrega:** `scripts/gerar_dados_mock.py` + CSVs em `data/`

**Onde fica:** `scripts/gerar_dados_mock.py`, saída em `data/`

**Na prática:**
```python
# scripts/gerar_dados_mock.py
from faker import Faker
fake = Faker('pt_BR')

paciente = {
    "prontuario": fake.random_int(min=10000000, max=22999999),
    "telefone": "81" + fake.numerify("########"),
    "cidade": fake.city(),
    "estado": "Pernambuco",
}
```

Gera CSVs na pasta `data/` com o mesmo formato do CSV real do AGHU que já existe (aquele com 402 linhas).

**Por que existe:** Sem dados, o sistema não tem o que processar. E não se pode usar dados reais de pacientes pra desenvolvimento (LGPD). Então gera dados falsos, testa tudo, e quando o acesso ao AGHU vier, é só chavear.

**Analogia:** Vocês não têm acesso ao banco real do hospital ainda. Então precisam de "figurantes" — dados falsos mas realistas. O Faker gera nomes brasileiros, CPFs, cidades de PE, etc.

---

### P3 — Pipeline de Importação ("Quem bota os dados dentro do banco")

**O que é:** Um script que lê os CSVs (mock ou futuramente do AGHU) e insere os dados no banco usando os Models (via ORM).

**O que entrega:** `scripts/popular_banco.py` (CSV → banco via ORM)

**Onde fica:** `scripts/popular_banco.py`

**Na prática:**
```python
# scripts/popular_banco.py
import csv
from src.models.paciente import Paciente

with open("data/pacientes.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        paciente = Paciente(
            prontuario=int(row["prontuario"]),
            telefone=row["telefone"],
            cidade=row["cidade"],
            estado=row["estado"],
        )
        session.add(paciente)
    await session.commit()
```

**Por que existe:** O CSV é só um arquivo solto. Pra aplicação consultar, filtrar, ordenar e relacionar os dados de forma eficiente, eles precisam estar no banco de dados. O pipeline faz essa ponte.

**Futuro:** Quando o acesso ao AGHU vier, esse mesmo script vai ser adaptado pra ler direto do Postgres/Oracle do AGHU em vez de ler do CSV. A lógica de inserção no banco local continua a mesma.

**Analogia:** Você tem a planta da casa (Models) e os tijolos (CSVs com dados). O Pipeline é o pedreiro — ele pega os tijolos e monta a casa seguindo a planta.

---

### P4 — Providers CSV ("Quem busca os dados quando a API precisa")

**O que é:** Classes que sabem como buscar dados de uma fonte específica. Cada provider implementa uma interface (contrato) que diz "eu sei listar pacientes" e "eu sei buscar paciente por código".

**O que entrega:** Interfaces + implementações CSV + fábricas em `dependencies.py`

**Onde fica:** `src/providers/interfaces/` e `src/providers/implementations/`

**Na prática:**
```python
# Interface (contrato) — diz O QUE deve existir
class PacienteProviderInterface(ABC):
    async def listar_pacientes(self) -> List[Dict]:
        pass

# Implementação CSV — diz COMO buscar do CSV
class PacienteCsvProvider(PacienteProviderInterface):
    async def listar_pacientes(self):
        # lê o CSV e retorna lista de dicts

# Implementação Postgres — diz COMO buscar do banco
class PacientePostgresProvider(PacienteProviderInterface):
    async def listar_pacientes(self):
        # executa SQL e retorna lista de dicts
```

Permite **chavear** entre CSV (dev) e banco real (produção) mudando UMA linha:
```python
STRATEGY = "csv"       # ← desenvolvimento
STRATEGY = "postgres"  # ← produção (quando tiver acesso ao AGHU)
```

**Por que existe:** É o que permite chavear entre CSV e banco real mudando uma linha. O cliente não sabe e nem precisa saber de onde veio. Ele só recebe os dados.

**Orientação do orientador:** "A aplicação precisa estar preparada para chavear entre o CSV mock e o banco real do AGHU quando o acesso for liberado." — É exatamente isso que os providers fazem.

**Analogia:** Garçom de restaurante. O cliente (controller) pede "me traz a lista de pacientes". O garçom (provider) vai buscar. De onde? Depende: PacienteCsvProvider → vai buscar no CSV. PacientePostgresProvider → vai buscar no banco Postgres do AGHU.

---

### P5 — Algoritmo de Pontuação ("O cérebro da fila")

**O que é:** Funções puras que recebem os dados de um paciente/solicitação e retornam uma pontuação de 0 a 100+. Essa pontuação define a posição na fila.

**O que entrega:** `src/services/pontuacao.py` + testes unitários

**Onde fica:** `src/services/pontuacao.py`

**Critérios de pontuação:**
- Data de retorno: **35%**
- Urgência (unidade solicitante): **25%**
- Morbidades: **20%**
- Localidade: **15%**
- Idade: **5%**
- Bônus: tempo de espera na fila

**Na prática:**
```python
# src/services/pontuacao.py
def calcular_pontuacao(paciente: dict, solicitacao: dict) -> float:
    score = (
        score_data_retorno(solicitacao["data_retorno"])       * 0.35 +
        score_urgencia(solicitacao["unidade_solicitante"])     * 0.25 +
        score_localidade(paciente["cidade"])                   * 0.15 +
        score_idade(paciente["data_nascimento"])               * 0.05
    )
    score += bonus_tempo_espera(solicitacao["data_entrada_fila"])
    return score
```

Mapa de urgência por unidade solicitante:
```python
def score_urgencia(unidade: str) -> float:
    mapa = {
        "UTI ADULTO": 100,
        "CENTRO OBSTETRICO": 90,
        "NEFROLOGIA (AMBULATÓRIO)": 70,
        "CARDIOLOGIA (AMBULATÓRIO)": 65,
        "PNEUMOLOGIA (AMBULATÓRIO)": 50,
    }
    return mapa.get(unidade, 40)
```

**Por que existe:** É a razão de ser do sistema inteiro. Sem isso, não tem ordenação de fila, não tem prioridade — não tem produto.

**Analogia:** É o juiz que olha pra cada paciente e dá uma nota baseada nos critérios que vocês definiram.

---

### P6 — API (Routers + Controllers) ("A porta de entrada")

**O que é:** Os endpoints HTTP que o frontend (ou qualquer outro cliente) vai chamar. O Router define a URL, o Controller orquestra a lógica.

**O que entrega:** Endpoints REST da fila e solicitações

**Onde fica:** `src/routers/fila.py` e `src/controllers/fila_controller.py`

**Na prática:**
```python
# src/routers/fila.py
@router.get("/api/fila")
async def listar_fila(provider = Depends(get_solicitacao_provider(STRATEGY))):
    return await fila_controller.obter_fila_ordenada(provider)

# src/controllers/fila_controller.py
async def obter_fila_ordenada(provider):
    solicitacoes = await provider.listar_solicitacoes()
    for s in solicitacoes:
        s["pontuacao"] = calcular_pontuacao(s["paciente"], s)
    return sorted(solicitacoes, key=lambda x: x["pontuacao"], reverse=True)
```

**Por que existe:** Sem isso, os dados ficam presos no backend. A API é o que expõe tudo para consumo — frontend, Postman, outro sistema, etc.

**Analogia:** O Router é a porta do restaurante com o cardápio na parede (`GET /api/fila`, `GET /api/solicitacoes`). O Controller é o chef — ele recebe o pedido, chama o provider pra buscar os dados, chama o algoritmo pra calcular a pontuação, e devolve a resposta pronta.

---

### Como tudo se conecta

```
P2 gera CSV mock ——→  P3 lê via Provider ——→  P5 expõe via API
                          ⇅                        ⇅
P1 cria as tabelas ——→  Pipeline importa   ——→  P4 calcula pontuação
```

Fluxo de uma requisição real:
```
Usuário chama GET /api/fila
    ↓
Router (P6) recebe a requisição
    ↓
Controller (P6) pede dados ao Provider
    ↓
Provider (P4) busca do CSV ou banco
    ↓
Controller passa dados pro Algoritmo (P5)
    ↓
Algoritmo calcula pontuação de cada solicitação
    ↓
Controller ordena e retorna a fila
```

## Comandos uteis

```bash
# Rodar o backend
uvicorn src.main:app --reload

# Migrations
alembic revision --autogenerate -m "descricao"
alembic upgrade head

# Frontend (dentro de frontend/)
npm run dev
npm run build
```
Tudo que você fizer será revisado pelo Codex