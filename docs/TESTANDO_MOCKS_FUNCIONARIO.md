# Guia de Teste Manual — Fluxo do Funcionário com Provedor Mock

Este guia descreve como iniciar a aplicação localmente e validar as funcionalidades da interface do funcionário utilizando os 6 pacientes mockados e o sistema de autenticação mock.

---

## ⚙️ 1. Configuração do Ambiente

1. Certifique-se de que o arquivo `.env` na raiz do projeto está configurado para usar as estratégias de mock:
   ```env
   # Define a estratégia de dados do funcionário como MOCK
   FUNCIONARIO_STRATEGY=MOCK

   # Mantém o banco SQLite local configurado (necessário para persistência de sessão de tokens)
   SQLITE_DSN=sqlite+aiosqlite:///app.db
   APP_DB_URL=sqlite+aiosqlite:///app.db

   # Configura o paciente geral para carregar do CSV local
   PACIENTE_PROVIDER_TYPE=CSV
   ```

---

## 🚀 2. Inicializando os Servidores

Execute o script de desenvolvimento para sincronizar as dependências e iniciar o backend e o frontend em paralelo:
```bash
./dev.sh
```

- O **Vite (frontend)** estará ouvindo em: [http://localhost:5173/](http://localhost:5173/)
- O **FastAPI (backend)** estará ouvindo em: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🔑 3. Login com Usuário Mock

1. Acesse [http://localhost:5173/](http://localhost:5173/).
2. Insira as credenciais de desenvolvimento offline:
   - **Usuário:** `admin`
   - **Senha:** `admin`
3. Clique em **Entrar**. Você será redirecionado para a Fila de Agendamento em `/funcionario`.

---

## 📋 4. Os 6 Pacientes Mockados na Fila

A fila exibe 6 pacientes variados que cobrem diferentes cenários de teste:

| ID | Nome do Paciente | Idade | Prioridade (Status) | Cor da Badge | Localização / Região | Exames |
|---|---|---|---|---|---|---|
| **1** | Maria Silva Souza | 72 | **ALTA** | Vermelha | Recife (I Regional) | Ecocardiograma, Eletrocardiograma |
| **2** | Pedro Henrique Ramos | 8 | **MÉDIA** | Amarela | Olinda (I Regional) | Ultrassonografia Abdominal |
| **3** | Ana Paula Medeiros | 34 | **BAIXA** | Verde | Caruaru (IV Regional) | Hemograma, Glicemia, Creatinina |
| **4** | José Carlos Oliveira | 67 | **BAIXA** | Verde | Petrolina (VIII Regional) | Ressonância de Crânio |
| **5** | Juliana Santos Lima | 45 | **ALTA** | Vermelha | Jaboatão (I Regional) | Mamografia Bilateral |
| **6** | Lucas Cavalcanti Farias | 16 | **MÉDIA** | Amarela | Paulista (I Regional) | Raio-X de Tórax |

---

## 🧪 5. Roteiro de Testes para Validar as Ações

### Teste A: Filtros e Busca (Client-side)
1. Digite `Maria` ou o prontuário `123456-7` no campo de busca. Verifique se apenas o paciente correspondente é exibido.
2. Limpe a busca. Selecione a faixa etária **60+**. Apenas os pacientes **Maria (72)** e **José (67)** devem aparecer.
3. Altere a faixa etária para **0-17**. Apenas **Pedro (8)** e **Lucas (16)** devem aparecer.

### Teste B: Ação "Puxar" (Fila Geral → Minha Área)
1. Escolha o paciente **Pedro Henrique Ramos** e clique em **Puxar**.
2. O card dele deve desaparecer imediatamente da fila geral.
3. Navegue até a aba **Minha Área** no menu lateral.
4. Verifique se **Pedro Henrique Ramos** está na seção **Em Andamento**.

### Teste C: Ação "Aguardar Confirmação"
1. No card de **Pedro Henrique Ramos** (em Minha Área), clique em **Ver mais** ou abra seus detalhes.
2. Clique no botão **Aguardar confirmação do Paciente**.
3. O paciente deve se mover da coluna/seção *Em Andamento* para a seção **Aguardando Confirmação**.

### Teste D: Ação "Devolver à Fila"
1. No card de **Pedro Henrique Ramos**, clique em **Devolver à fila**.
2. Selecione um motivo (ex: "Exame selecionado por engano.") e confirme.
3. O paciente deve sumir de "Minha Área" e reaparecer na fila geral de **Agendamento**.

### Teste E: Ação "Reportar Problema"
1. Puxe outro paciente (ex: **Juliana Santos Lima**) para sua área.
2. Abra os detalhes dela e clique em **Reportar Problema**.
3. Selecione o motivo (ex: "Dados inconsistentes") e clique em **Enviar**.
4. O problema será registrado em log e o fluxo continuará ativo em sua área de trabalho.

### Teste F: Ação "Finalizar" (Confirmado/Cancelado)
1. Puxe **Juliana Santos Lima** e coloque-a em estado **Aguardando Confirmação** (seguindo os passos dos Testes B e C).
2. Na seção *Aguardando Confirmação*, clique no card dela e selecione **Confirmado** ou **Cancelado**.
3. O paciente deve se mover para a seção **Finalizados**, exibindo o resultado selecionado na badge de status.
