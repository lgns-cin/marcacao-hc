# API do Módulo Funcionário — Referência

Este documento mapeia **todos** os endpoints HTTP consumidos pelas telas do módulo `funcionario` (Fila de Agendamento, Minha Área e Login), com contratos de requisição/resposta, códigos de status e o estado real de implementação no backend.

Fontes de verdade usadas para este mapeamento:
- Frontend: `frontend/src/stores/auth.ts`, `frontend/src/stores/funcionario.ts`, `frontend/src/services/api.ts`.
- Backend: `src/routers/auth.py` (único roteador relacionado já implementado).

> **Importante:** o backend atual (`src/routers/`) só possui roteadores para `auth`, `pacientes`, `admin`, `aih`, `bpa` e `material`. **Não existe** um roteador `funcionario`/`agendamento` em `src/main.py`. Os endpoints da seção 2 são o **contrato que o frontend já assume e está pronto para consumir**, validado durante o desenvolvimento desta feature contra um mock backend descartável (Node, fora do repositório). Eles precisam ser implementados no backend antes de ir para produção — ver seção 5 para recomendações de implementação.

---

## 0. Convenções gerais

| Aspecto | Valor |
| :--- | :--- |
| **Base path** | `/api` (proxy do Vite `/api` → backend FastAPI, ver `vite.config.ts`) |
| **Formato de erro** | FastAPI padrão: `{ "detail": "<mensagem>" }` |
| **Autenticação** | `Authorization: Bearer <access_token>` em todas as rotas exceto `POST /api/login` |
| **Cliente HTTP** | `frontend/src/services/api.ts` (instância Axios única — nunca chamado `axios` diretamente nas views/stores) |
| **Renovação automática** | Em qualquer resposta `401` (exceto a própria chamada de refresh), o interceptor de resposta do Axios tenta `POST /api/token/refresh` uma vez e repete a requisição original; se falhar, desloga o usuário (`authStore.logout()`) |

---

## 1. Autenticação — `src/routers/auth.py`

### `POST /api/login`
Autentica o usuário e retorna um token de acesso (JWT).

| | |
| :--- | :--- |
| **Autenticação** | Não |
| **Content-Type** | `application/x-www-form-urlencoded` |
| **Consumido por** | `stores/auth.ts → login()` |

**Corpo (form fields):**

| Campo | Tipo | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- |
| `username` | string | Sim | Usuário (AD `sAMAccountName` em produção; usuário mock em desenvolvimento) |
| `password` | string | Sim | Senha em texto puro (trafega apenas via HTTPS) |
| `remember_me` | boolean | Não (default `false`) | Ver comportamento abaixo |

**Respostas:**

| Status | Corpo | Quando |
| :--- | :--- | :--- |
| `200` | `{ "access_token": string, "token_type": "bearer" }` | Credenciais válidas |
| `401` | `{ "detail": "Invalid mock credentials" }` ou `{ "detail": "Invalid credentials" }` | Usuário/senha inválidos |
| `503` | `{ "detail": "AD server is down or unreachable" }` | Falha de conectividade com o AD (produção) |
| `500` | `{ "detail": "An unexpected error occurred: ..." }` | Erro inesperado no provedor de autenticação |

**Comportamento notável (`remember_me`):**
- `false` (padrão): o `access_token` expira em `JWT_EXP_HOURS` horas (variável de ambiente, default 24h) e **nenhum** refresh token é emitido — ao expirar, o usuário precisa logar novamente.
- `true`: o `access_token` expira em **15 minutos**, mas um refresh token de longa duração (`REFRESH_TOKEN_EXP_DAYS` dias, default 30) é gravado em um cookie `HttpOnly`/`Secure`/`SameSite=Lax` chamado `refresh_token`, permitindo renovação silenciosa via `POST /api/token/refresh`.

---

### `POST /api/token/refresh`
Troca o cookie `refresh_token` por um novo par de tokens (access + refresh, com rotação).

| | |
| :--- | :--- |
| **Autenticação** | Cookie `refresh_token` (`HttpOnly`), não usa o header `Authorization` |
| **Content-Type** | Nenhum corpo esperado |
| **Consumido por** | `stores/auth.ts → initializeAuth()` (na ausência de token em `localStorage`) e pelo interceptor de resposta de `services/api.ts` (em qualquer 401) |

**Respostas:**

| Status | Corpo | Quando |
| :--- | :--- | :--- |
| `200` | `{ "access_token": string, "token_type": "bearer" }` | Cookie válido e não expirado; o cookie é rotacionado (novo valor setado na resposta) |
| `401` | `{ "detail": "Refresh token not found" }` | Sem cookie `refresh_token` (ex.: login anterior com `remember_me=false`) |
| `401` | `{ "detail": "Invalid or expired refresh token" }` | Cookie presente mas inválido/expirado |
| `401` | `{ "detail": "Failed to re-authenticate user: ..." }` | Usuário não existe mais no provedor de autenticação |

> Como o token é rotacionado a cada chamada, **não** deve ser invocado mais de uma vez em paralelo — o interceptor em `services/api.ts` já implementa uma fila (`isRefreshing`/`failedQueue`) para serializar chamadas concorrentes que disparariam refresh simultaneamente.

---

### `POST /api/logout`
Invalida o refresh token atual e limpa o cookie.

| | |
| :--- | :--- |
| **Autenticação** | Cookie `refresh_token` (opcional — não falha se ausente) |
| **Consumido por** | `stores/auth.ts → logout()`, acionado pelo botão "Sair da Conta" em `FuncionarioLayout.vue` |

**Respostas:**

| Status | Corpo |
| :--- | :--- |
| `200` | `{ "message": "Logged out successfully" }` |

O frontend ignora falhas desta chamada (best-effort) e sempre limpa o `access_token` local e redireciona para `Login` em seguida.

---

### `GET /api/users/me`
Retorna os dados do usuário autenticado, extraídos diretamente do payload do JWT.

| | |
| :--- | :--- |
| **Autenticação** | `Authorization: Bearer <access_token>` |
| **Consumido por** | `stores/auth.ts → fetchUser()`, chamado após login e na inicialização do app (`App.vue → onMounted`) |

**Resposta `200`** — payload decodificado do JWT (não um modelo fixo; campos variam conforme o provedor de autenticação):

| Campo | Tipo | Origem |
| :--- | :--- | :--- |
| `username` | string | Sempre presente (também replicado em `sub`) |
| `groups` | string[] | Sempre presente (usado por `authStore.isAdmin`, comparando com o grupo `GLO-SEC-HCPE-SETISD`) |
| `givenName` | string[] | Apenas AD |
| `userPrincipalName` | string[] | Apenas AD |
| `title` | string[] | Apenas AD |
| `department` | string[] | Apenas AD |
| `employeeNumber` | string[] | Apenas AD |
| `displayName` | string[] | Apenas mock |
| `email` | string | Apenas mock |
| `sub`, `exp` | string / number | Claims padrão de JWT — não usados pelo frontend |

**Respostas de erro:**

| Status | Corpo | Quando |
| :--- | :--- | :--- |
| `401` | `{ "detail": "Token has expired" }` | Access token expirado (dispara o fluxo de refresh automático) |
| `401` | `{ "detail": "Invalid token" }` | Token malformado/assinatura inválida |

---

## 2. Fila de Agendamento e Minha Área

Todos os endpoints abaixo são prefixados por `/api/funcionario` e exigem `Authorization: Bearer <access_token>`. Definidos e consumidos por `stores/funcionario.ts`.

### `GET /api/funcionario/agendamentos`
Lista os pacientes disponíveis na fila de agendamento (ainda não atribuídos a nenhum atendente).
- **Resposta `200`:** `AgendamentoItem[]` (schema completo na seção 3).

### `POST /api/funcionario/agendamentos/{id}/puxar`
Atribui (reivindica) um paciente da fila ao atendente autenticado, movendo-o para "Minha Área" com `estado: "EM_ANDAMENTO"`.

| Path param | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | number | `id` do `AgendamentoItem` na fila |

- **Consumido por:** `puxarAgendamento(id)`, chamado a partir de `PatientQueueCard.vue` e `PatientDetailModal.vue`.
- **Resposta `200`:** corpo vazio (`{}`). Em caso de sucesso, o frontend remove o item da lista local **imediatamente** (sem esperar um refetch).
- **Resposta `409`:** `{ "detail": "Este paciente já foi atribuído a outro atendente." }` — emitido quando o paciente já não está mais na fila (ex.: outro atendente o puxou primeiro). O frontend trata esse status especificamente (`FilaAgendamento.vue → puxarAgendamento`): mostra um toast de erro dedicado e força um refetch da fila. Ver seção 5 para a recomendação de implementação atômica deste endpoint.

### `GET /api/funcionario/minha-area`
Lista todos os pacientes atribuídos ao atendente autenticado, em qualquer estado (`EM_ANDAMENTO`, `AGUARDANDO_CONFIRMACAO`, `FINALIZADO`).
- **Resposta `200`:** `MinhaAreaItem[]` (schema completo na seção 3).

### `POST /api/funcionario/minha-area/{id}/aguardar-confirmacao`
Marca um item `EM_ANDAMENTO` como `AGUARDANDO_CONFIRMACAO` (agendamento feito, aguardando confirmação do paciente).

| Path param | Tipo |
| :--- | :--- |
| `id` | number |

- **Consumido por:** `aguardarConfirmacao(id)`, botão "Aguardar confirmação do Paciente" em `MinhaAreaDetailModal.vue`.
- **Resposta `200`:** corpo vazio. O frontend atualiza `estado` do item localmente após sucesso.

### `POST /api/funcionario/minha-area/{id}/devolver`
Devolve o item à fila geral de agendamento (remove de "Minha Área", reaparece em `GET /api/funcionario/agendamentos`).

| Path param | Tipo |
| :--- | :--- |
| `id` | number |

**Corpo (JSON):**

| Campo | Tipo | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- |
| `motivo` | string | Sim | Texto livre. O frontend oferece as opções pré-definidas em `MOTIVOS_DEVOLUCAO` (`funcionario/types.ts`) via `SeletorMotivo.vue`, mas envia uma string simples — o backend não deve assumir um enum fechado. |

- **Consumido por:** `devolverAFila(id, motivo)`, fluxo "Devolver à fila" em `MinhaAreaDetailModal.vue`.
- **Resposta `200`:** corpo vazio. O frontend remove o item de `minhaArea` localmente após sucesso.

### `POST /api/funcionario/minha-area/{id}/reportar-problema`
Registra um problema relatado pelo atendente sobre o item, alternado seu estado para `PROBLEMA_RELATADO`.

| Path param | Tipo |
| :--- | :--- |
| `id` | number |

**Corpo (JSON):**

| Campo | Tipo | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- |
| `motivo` | string | Sim | Texto livre; opções sugeridas em `MOTIVOS_PROBLEMA` (`funcionario/types.ts`) |

- **Consumido por:** `reportarProblema(id, motivo)`, fluxo "Reportar Problema" em `MinhaAreaDetailModal.vue`.
- **Resposta `200`:** corpo vazio. Não há atualização de estado local — o item permanece como está.

### `POST /api/funcionario/minha-area/{id}/finalizar`
Finaliza o atendimento de um item `AGUARDANDO_CONFIRMACAO`, registrando o resultado.

| Path param | Tipo |
| :--- | :--- |
| `id` | number |

**Corpo (JSON):**

| Campo | Tipo | Obrigatório | Valores |
| :--- | :--- | :--- | :--- |
| `resultado` | string (enum) | Sim | `"CONFIRMADO"` \| `"CANCELADO"` | `PROBLEMA_RELATADO` |

- **Consumido por:** `finalizarAgendamento(id, resultado)`, botões "Confirmado"/"Cancelado" em `MinhaAreaDetailModal.vue`.
- **Resposta `200`:** corpo vazio. O frontend atualiza `estado` para `"FINALIZADO"` e grava `resultado` localmente após sucesso.

---

## 3. Modelos de dados compartilhados

Definidos em `frontend/src/funcionario/types.ts` — refletem o shape que o frontend espera receber/enviar; ainda não existe um `response_model` Pydantic equivalente no backend.

### `AgendamentoItem`

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | number | Identificador único do agendamento |
| `nome` | string | Nome do paciente |
| `prontuario` | string | Número do prontuário (AGHU) |
| `exames` | string[] | Lista de exames solicitados |
| `diasNaFila` | number | Dias desde a entrada na fila (exibido como "há Nd") |
| `status` | `StatusPaciente` | Prioridade/classificação do paciente — ⚠️ ver nota abaixo |
| `unidadeExecutora` | string | Unidade que executará o exame |
| `unidadeSolicitante` | string | Unidade que solicitou o exame |
| `dataRetorno` | string | Data de retorno esperada (`DD/MM/AAAA`) |
| `localizacao` | string | Município de residência do paciente |
| `regiao` | string | Região de saúde (usado no filtro client-side) |
| `idade` | number | Idade do paciente em anos |

> **Inconsistência de tipos que percebemos:** `StatusPaciente` está declarado em `types.ts` como `'ALTA'` apenas (um único literal), mas os dados reais já usam `'MÉDIA'` e `'BAIXA'` também. O tipo deveria ser `'ALTA' | 'MÉDIA' | 'BAIXA'` — não corrigido nesta PR para não ampliar o escopo, mas deve ser ajustado antes de o backend real definir um enum equivalente.

### `MinhaAreaItem`
`AgendamentoItem` **+**:

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `estado` | `'EM_ANDAMENTO' \| 'AGUARDANDO_CONFIRMACAO' \| 'FINALIZADO'` | Estado do item dentro de "Minha Área" |
| `resultado` | `'CONFIRMADO' \| 'CANCELADO' \| 'PROBLEMA_RELATADO'` (opcional) | Preenchido apenas quando `estado === 'FINALIZADO'` |

### Motivos sugeridos (texto livre, não um enum de backend)

| Constante | Valores |
| :--- | :--- |
| `MOTIVOS_DEVOLUCAO` | "Exame selecionado por engano.", "Solicitação atribuída incorretamente pela administração.", "Outro" |
| `MOTIVOS_PROBLEMA` | "Dados inconsistentes", "Duplicidade", "Erro cadastral", "Outro" |

---

## 4. Filtros — aplicados no cliente, não há contrato de API

`FiltrosFila` (`busca`, `regioes`, `tiposExame`, `municipio`, `faixaEtaria`) é processado **inteiramente no frontend**, em `stores/funcionario.ts → filtrarAgendamentos()`, sobre a lista completa já carregada por `GET /api/funcionario/agendamentos` ou `GET /api/funcionario/minha-area`. **Não existem query params de filtro hoje.**

Isso é aceitável para os volumes de teste atuais, mas não escala: à medida que a fila crescer, recomenda-se migrar para filtragem e paginação no backend (query params equivalentes aos campos de `FiltrosFila`), evitando trafegar toda a fila a cada requisição.

---

## 5. Índice de endpoints

| Método | Rota |
| :--- | :--- |
| POST | `/api/login` |
| POST | `/api/token/refresh` |
| POST | `/api/logout` |
| GET | `/api/users/me` |
| GET | `/api/funcionario/agendamentos` |
| POST | `/api/funcionario/agendamentos/{id}/puxar` |
| GET | `/api/funcionario/minha-area` |
| POST | `/api/funcionario/minha-area/{id}/aguardar-confirmacao` |
| POST | `/api/funcionario/minha-area/{id}/devolver` |
| POST | `/api/funcionario/minha-area/{id}/reportar-problema` |
| POST | `/api/funcionario/minha-area/{id}/finalizar` |
