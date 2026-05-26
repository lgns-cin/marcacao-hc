# Especificação de Requisitos

### 1. FUNCIONÁRIO — Requisitos Funcionais (RF)
| ID | Título | Descrição | Prioridade |
| :--- | :--- | :--- | :--- |
| RF003 | Assumir solicitação | O funcionário deve conseguir assumir uma solicitação da fila geral. | Alta |
| RF004 | Devolver solicitação | O funcionário deve conseguir devolver uma solicitação para a fila geral. | Alta |
| RF005 | Área individual | O funcionário deve possuir uma área individual no sistema. | Média |
| RF006 | Visualizar fila | Mostrar fila ordenada de cartões com informações das solicitações. | Essencial |
| RF007 | Filtrar solicitações | O funcionário deve conseguir filtrar solicitações. | Essencial |
| RF008 | Pesquisar solicitações | Pesquisar por nome do paciente, prontuário ou tipo de exame. | Essencial |
| RF009 | Cards resumo | Visualizar informações resumidas das solicitações através de cards. | Essencial |
| RF010 | Alterar status | Alterar o status de uma solicitação. | Essencial |

### 2. FUNCIONÁRIO — Requisitos Não Funcionais (RNF)
| ID | Categoria | Descrição |
| :--- | :--- | :--- |
| RNF003 | Consistência | Todo funcionário deve ver a mesma fila em tempo real. |
| RNF004 | Confiabilidade | Evitar que dois funcionários assumam/editem simultaneamente a mesma solicitação. |
| RNF005 | Usabilidade | Baixo esforço cognitivo; principais ações em poucos cliques; leitura rápida via cores/tags. |

### 3. ADMINISTRADOR — Requisitos Funcionais (RF)
| ID | Título | Descrição | Prioridade |
| :--- | :--- | :--- | :--- |
| RF011 | Definir vagas | Definir a quantidade de vagas disponíveis para agendamento. | Alta |
| RF012 | Configurar filtros rápidos | Definir quais filtros rápidos serão exibidos na fila principal. | Média |
| RF013 | Visualizar agendamentos | Visualizar exames agendados e o funcionário responsável. | Alta |
| RF014 | Filtrar agendamentos | Filtrar exames agendados por critérios (data, funcionário, tipo). | Média |
| RF015 | Liberar solicitações | Permitir que o administrador libere solicitações que ficaram bloqueadas (assumidas por um funcionário por tempo excessivo) | Alta |
| RF016 | Reatribuir solicitações | Reatribuir solicitações entre funcionários. | Alta |
| RF017 | Métricas operacionais | Visualizar métricas operacionais da fila. | Média |
| RF018 | Solicitações paradas | Visualizar solicitações paradas por muito tempo. | Média |

### 4. ADMINISTRADOR — Requisitos Não Funcionais (RNF)
| ID | Categoria | Descrição |
| :--- | :--- | :--- |
| RNF006 | Usabilidade | Baixo esforço cognitivo; principais ações em poucos cliques; leitura rápida via cores/tags. |

### 9. FORMS — Requisitos Funcionais
| ID | Título | Descrição | Prioridade |
| :--- | :--- | :--- | :--- |
| RF024 | Feedback imediato | Usuário recebe feedback sobre envio do formulário na mesma sessão. | Essencial |
| RF025 | Validação ao enviar | Informações validadas assim que são enviadas. | Essencial |
| RF026 | Checagem disponibilidade | Sistema verifica individualmente disponibilidade de cada exame por solicitação. | Essencial |
| RF027 | Resultado por exame | Deixar claro quais exames puderam ser marcados e quais não (relatório por solicitação). | Essencial |
| RF028 | Resposta a erros | Resposta imediata em casos de formulários preenchidos incorretamente. | Essencial |

### 10. FORMS — Requisitos Não Funcionais
| ID | Categoria | Descrição |
| :--- | :--- | :--- |
| RNF007 | Acessibilidade | Elementos visuais preferíveis; fácil compreensão; etapas separadas para reduzir carga cognitiva. |
| RNF008 | Design responsivo | Priorizar visão em telefones/telas pequenas; layout adaptativo. |
| RNF009 | Simplicidade | Minimizar número de campos; auto-preenchimento assistido onde aplicável. |
