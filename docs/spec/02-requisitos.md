# Especificação de Requisitos

## Requisitos Funcionais (RF)

### 1. FORMULÁRIO
| ID | Título | Descrição | Prioridade |
| :--- | :--- | :--- | :--- |
| RF101 | Feedback imediato | Usuário recebe feedback sobre envio do formulário na mesma sessão. | Essencial |
| RF102 | Validação ao enviar | Informações validadas assim que são enviadas. | Essencial |
| RF103 | Checagem disponibilidade | Sistema verifica individualmente disponibilidade de cada exame por solicitação. | Essencial |
| RF104 | Resultado por exame | Deixar claro quais exames puderam ser marcados e quais não (relatório por solicitação). | Essencial |
| RF105 | Resposta a erros | Resposta imediata em casos de formulários preenchidos incorretamente. | Essencial |

### 2. ÁREA DO FUNCIONÁRIO
| ID | Título | Descrição | Prioridade |
| :--- | :--- | :--- | :--- |
| RF201 | Assumir solicitação | O funcionário deve conseguir assumir uma solicitação da fila geral. | Alta |
| RF202 | Devolver solicitação | O funcionário deve conseguir devolver uma solicitação para a fila geral. | Alta |
| RF203 | Área individual | O funcionário deve possuir uma área individual no sistema. | Média |
| RF204 | Visualizar fila | Mostrar fila ordenada de cartões com informações das solicitações. | Essencial |
| RF205 | Filtrar solicitações | O funcionário deve conseguir filtrar solicitações. | Essencial |
| RF206 | Pesquisar solicitações | Pesquisar por nome do paciente, prontuário ou tipo de exame. | Essencial |
| RF207 | Cards resumo | Visualizar informações resumidas das solicitações através de cards. | Essencial |
| RF208 | Alterar status | Alterar o status de uma solicitação. | Essencial |

### 3. ÁREA DO ADMINISTRADOR
| ID | Título | Descrição | Prioridade |
| :--- | :--- | :--- | :--- |
| RF301 | Definir vagas | Definir a quantidade de vagas disponíveis para agendamento. | Alta |
| RF302 | Configurar filtros rápidos | Definir quais filtros rápidos serão exibidos na fila principal. | Média |
| RF303 | Visualizar agendamentos | Visualizar exames agendados e o funcionário responsável. | Alta |
| RF304 | Filtrar agendamentos | Filtrar exames agendados por critérios (data, funcionário, tipo). | Média |
| RF305 | Liberar solicitações | Permitir que o administrador libere solicitações que ficaram bloqueadas (assumidas por um funcionário por tempo excessivo) | Alta |
| RF306 | Reatribuir solicitações | Reatribuir solicitações entre funcionários. | Alta |
| RF307 | Métricas operacionais | Visualizar métricas operacionais da fila. | Média |
| RF308 | Solicitações paradas | Visualizar solicitações paradas por muito tempo. | Média |

## Requisitos Não Funcionais (RNF)

### 1. FORMULÁRIO
| ID | Categoria | Descrição |
| :--- | :--- | :--- |
| RNF101 | Acessibilidade | Elementos visuais preferíveis; fácil compreensão; etapas separadas para reduzir carga cognitiva. |
| RNF102 | Design responsivo | Priorizar visão em telefones/telas pequenas; layout adaptativo. |
| RNF103 | Simplicidade | Minimizar número de campos; auto-preenchimento assistido onde aplicável. |

### 2. ÁREA DO FUNCIONÁRIO
| ID | Categoria | Descrição |
| :--- | :--- | :--- |
| RNF201 | Consistência | Todo funcionário deve ver a mesma fila em tempo real. |
| RNF202 | Confiabilidade | Evitar que dois funcionários assumam/editem simultaneamente a mesma solicitação. |
| RNF203 | Usabilidade | Baixo esforço cognitivo; principais ações em poucos cliques; leitura rápida via cores/tags. |

### 3. ÁREA DO ADMINISTRADOR
| ID | Categoria | Descrição |
| :--- | :--- | :--- |
| RNF301 | Usabilidade | Baixo esforço cognitivo; principais ações em poucos cliques; leitura rápida via cores/tags. |
