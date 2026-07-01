# 🏥 Marcação HC - CORTeX

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue.js 3](https://img.shields.io/badge/Frontend-Vue.js%203-4FC08D.svg?style=flat-square&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/Frontend-TypeScript-3178C6.svg?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

---

O **CORTeX** é um sistema desenvolvido com o objetivo de otimizar e centralizar a gestão de vagas para exames diagnósticos no **Hospital das Clínicas da UFPE (HC)**.

A solução atua baseada em três módulos principais:

*   **Formulário do Paciente:** Interface intuitiva e acessível para que os pacientes insiram seus dados, contendo validações em tempo real integradas ao AGHU para evitar erros de digitação e duplicidade antes mesmo da submissão.
*   **Painel do Funcionário:** Fila de trabalho unificada e ordenada de forma automática com algoritmos de priorização, permitindo "puxar" atendimentos, controlar estados, registrar justificativas de devolução e diminuir o tempo médio de agendamento.
*   **Painel do Administrador:** Central de controle (Dashboard) com KPIs em tempo real, monitoramento de pendências (solicitações com problemas) e capacidade de reatribuição de carga de trabalho para melhorar a tomada de decisões da gestão.

---

## ⚙️ Stack utilizada

| Componente | Tecnologia Utilizada |
| :--- | :--- |
| **Backend** | Python 3.10+, FastAPI, Uvicorn |
| **Frontend** | Vue 3, Vite, TypeScript, TailwindCSS |
| **Banco de Dados Local** | SQLAlchemy 2.0+ (SQLite) |
| **Banco do Hospital** | PostgreSQL (AGHU) |

---

## 📁 Estrutura do Repositório

Abaixo está o mapeamento dos principais diretórios e a organização arquitetural do projeto:

```text
.
├── data/                           # Dados estáticos para testes e ambiente Mock
├── docs/                           # Documentação técnica e especificações do projeto
│   ├── adr/                        # Architectural Decision Records
│   ├── model/                      # Modelagem de arquitetura
│   ├── spec/                       # Especificações de requisitos e regras de negócio (SPEC.md)
│   ├── API_FUNCIONARIO.md          # Documentação de referência dos endpoints HTTP
│   ├── ARCHITECTURE.md             # Detalhes da arquitetura de camadas e injeção de provedores
│   ├── AUTHENTICATION.md           # Fluxo e lógica do sistema de autenticação (AD & Mock)
│   ├── GUIA_DESENVOLVIMENTO.md     # Guia prático passo a passo de desenvolvimento
│   └── SETUP.md                    # Manual de instalação e configuração do ambiente
├── frontend/                       # Código-fonte da aplicação frontend
│   ├── public/                     # Assets estáticos públicos
│   └── src/                        # Código principal da aplicação
│       ├── admin/                  # Telas e fluxos da Central Administrativa
│       ├── auth/                   # Fluxo de login e autenticação
│       ├── form/                   # Formulário de solicitação de exames do Paciente
│       ├── funcionario/            # Telas da Fila de Agendamento e Minha Área do Funcionário
│       ├── router/                 # Configuração de rotas da aplicação
│       ├── services/               # Serviços de API e integração HTTP
│       └── stores/                 # Gerenciamento de estados globais
├── src/                            # Código-fonte do backend (FastAPI + Uvicorn)
│   ├── auth/                       # Lógica de autenticação (AD, Mock, JWT)
│   ├── controllers/                # Lógica de negócio e orquestração
│   ├── dependencies.py             # Fábrica de injeção de dependência
│   ├── models/                     # Modelos de dados
│   ├── providers/                  # Camada de acesso a dados
│   │   ├── implementations/
│   │   └── interfaces/
│   ├── resources/                  # Configuração de recursos
│   └── routers/                    # Definição dos endpoints da API
├── dev.sh                          # Script de execução em Desenvolvimento
├── start.sh                        # Script de execução em Produção
├── .env.example                    # Arquivo de exemplo para variáveis de ambiente
└── README.md                       # Esta documentação
```

---

## 🛠️ Primeiros Passos

Siga as instruções rápidas abaixo para colocar a aplicação em execução no seu ambiente local. Para detalhes avançados de instalação, consulte o [Guia de Instalação e Execução (SETUP.md)](./docs/SETUP.md).

### Pré-requisitos

Certifique-se de ter instalado em sua máquina:
- **Node.js 18** ou superior
- **Python 3.10** ou superior
- Gerenciador **uv** (para dependências Python):
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### Configuração Inicial

1. Duplique o arquivo de variáveis de ambiente e configure suas credenciais:
   ```bash
   cp .env.example .env
   ```

2. Abra o arquivo `.env` gerado e defina as variáveis necessárias. *(Nota: Por padrão, a aplicação inicia no modo offline caso não detecte um servidor AD ativo).*

---

## 🚀 Scripts de Inicialização

O projeto possui scripts automatizados em bash na raiz para acelerar seu desenvolvimento:

### A. Modo Desenvolvimento (Recomendado)
Inicia o backend (FastAPI) e o frontend (Vite dev server) em paralelo no mesmo terminal.
- **Porta Frontend:** `http://localhost:5173` (com proxy automático configurado para `/api` redirecionar para a porta `8000`)
- **Porta Backend:** `http://localhost:8000`
- **Comando:**
  ```bash
  ./dev.sh
  ```

### B. Modo Produção Local (Unified Server)
Gera o build otimizado dos arquivos do frontend e os consolida para serem servidos diretamente pelo FastAPI.
- **Porta Única (Frontend + Backend):** `http://localhost:8000`
- **Comando:**
  ```bash
  ./start.sh
  ```

---

## 📚 Aprofundamento

Para documentações técnicas detalhadas sobre regras de negócio, fluxos e implementação, explore os links abaixo:

### Configuração e Execução
- **[Guia de Instalação (SETUP.md)](./docs/SETUP.md)**: Passos e instruções de troubleshooting do ambiente.

### Arquitetura e Engenharia de Software
- **[Arquitetura do Projeto (ARCHITECTURE.md)](./docs/ARCHITECTURE.md)**: Entenda o funcionamento do padrão de Provedores com Seleção de Estratégias.
- **[Guia de Desenvolvimento (GUIA_DESENVOLVIMENTO.md)](./docs/GUIA_DESENVOLVIMENTO.md)**: Passo a passo de ponta a ponta de como implementar um novo módulo no sistema.
- **[Decisões de Projeto (docs/adr)](./docs/adr)**: Registro das Architectural Decision Records do sistema.
- **[Modelagem de Componentes (docs/model)](./docs/model)**: Diagramação C4 da estrutura da plataforma.
