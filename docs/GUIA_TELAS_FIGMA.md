# Guia: Implementando Telas a partir do Figma com Claude Code

Este guia compacta o fluxo de trabalho usado para implementar o módulo `frontend/src/funcionario` (telas "Fila de Agendamento" e "Minha Área") a partir de screenshots do Figma, com auxílio do Claude Code. Use-o como ponto de partida para as próximas telas (ex.: módulo administrativo).

Diferente do [GUIA_DESENVOLVIMENTO.md](./GUIA_DESENVOLVIMENTO.md) (que cobre uma feature full-stack nova, com SQL/Provider/Controller/Router), este guia foca em telas de **frontend** que consomem uma API REST já definida (real ou ainda não implementada) — o caso comum quando se está traduzindo um design do Figma para código.

---

## 1. Prompt-base (copie e adapte)

Cole algo como o texto abaixo no Claude Code, anexando os prints do Figma da tela:

```
Anexei os prints do Figma da tela "<NOME_DA_TELA>" do módulo <funcionario|admin|...>.

Implemente esta tela seguindo os padrões já usados em frontend/src/funcionario
(componentes em funcionario/components, view em funcionario/views, tipos em
funcionario/types.ts, store Pinia em stores/<modulo>.ts). Reutilize componentes
compartilhados existentes (Modal.vue, FilaFiltros.vue etc.) sempre que possível
em vez de recriar.

Depois de implementar:
1. Verifique type-check (vue-tsc) e build.
2. Suba o dev server e teste a tela em um browser real (Playwright), cobrindo
   todos os estados visíveis no Figma (vazio, carregando, lista, detalhe,
   formulários, dropdowns, confirmações). Se não existir backend real para
   os endpoints usados, crie um mock backend descartável (Node puro, sem
   dependências) só para esta sessão de testes — não faça parte do commit.
3. Reporte qualquer estado que não bata com o Figma antes de seguir adiante.

Ao final, crie commits pequenos e granulares, um por mudança lógica, no
formato `feat(front): <descrição em português>` (ou `fix(front):` para
correção de bug), com a trailer de coautoria do Claude.
```

Ajuste `<NOME_DA_TELA>` e o módulo de destino. Quanto mais específico sobre quais endpoints/contratos de API já existem (ou não existem), melhor.

---

## 2. Convenções já estabelecidas no frontend

- **Vue 3 Composition API exclusivamente**, sempre `<script setup lang="ts">`.
- **Pinia** com stores no estilo *setup* (`ref`/`computed`/funções, sem `state`/`actions` em objeto).
- **TailwindCSS v4**, usando as variáveis de cor customizadas `--color-govbr-*` (`govbr-primary`, `govbr-text`, `govbr-border`, `govbr-bg`, `govbr-error` etc.) em vez de cores genéricas do Tailwind.
- **vue-router v4** com layout por rota: cada `RouteRecordRaw` define `meta.layout` (ex.: `FuncionarioLayout`, `FormLayout`, `LoginLayout`) e o `App.vue` renderiza `<component :is="route.meta.layout">`. Rotas que exigem login usam `meta.requiresAuth: true`.
- **Axios** apenas via `src/services/api.ts` (nunca importar `axios` direto nas views/stores) — ele já injeta o `Authorization` header e trata refresh de token em um 401.
- **vue-toastification** (`useToast()`) para feedback de sucesso/erro de toda ação assíncrona.
- **Ícones:** só `@heroicons/vue/24/outline`. Não introduzir outra lib de ícones.
- **Componentes compartilhados** em `shared/components` (ex.: `Modal.vue`) e `shared/layouts` — sempre checar se já existe algo reaproveitável antes de criar um componente novo.

---

## 3. Armadilhas já identificadas

- **`Modal.vue` usa `overflow-hidden rounded-2xl` no card.** Qualquer conteúdo que precise crescer dentro do modal (ex.: um dropdown de seleção) **deve permanecer no fluxo normal do documento**, nunca em `position: fixed`/`teleport` para "escapar" do clipping — isso troca um bug visual (conteúdo cortado) por outro (conteúdo flutuante cobrindo os botões do rodapé do modal). A solução correta é deixar o card crescer (`height: auto`) para acomodar o dropdown, empurrando o rodapé para baixo.
- **Padrão de fechar-ao-clicar-fora:** `ref` no elemento raiz + `document.addEventListener('click', handler)` ativado/desativado via `watch()` no booleano de "aberto", com `removeEventListener` no `onBeforeUnmount`.
- **Atualização otimista de estado local:** ações que removem/movem um item de uma lista (ex.: "puxar" um paciente da fila para "minha área") devem atualizar o `ref` da store imediatamente após a resposta da API, e não depender de um refetch subsequente — senão a UI parece travada/bugada para quem está testando manualmente.
- **Sem lib de tempo real no stack aprovado.** "Atualizar para todos os usuários" (múltiplos atendentes simultâneos) deve ser resolvido com **polling** (refetch periódico) e tratamento de erro de conflito (ex.: a ação de "puxar" falhar porque outro atendente já pegou aquele paciente — mostrar um toast claro e atualizar a lista), não com WebSockets/SSE.

---

## 4. Como testar antes de reportar como concluído

Tipagem e build passando **não** comprova que a tela funciona — é preciso ver a tela rodando:

1. Se a tela depende de endpoints que ainda não existem no backend real, crie um mock backend descartável (script Node usando só o módulo `http`, sem dependências, vivendo em `/tmp`, **nunca commitado**) que responda no mesmo formato esperado pela store.
2. Suba o Vite dev server (`./dev.sh` ou `npm run dev` em `frontend/`).
3. Use Playwright (instalado avulso, não como dependência do projeto) para navegar por todos os estados da tela e tirar screenshots — compare visualmente com os prints do Figma.
4. Ao encontrar algo estranho num screenshot, investigue a causa raiz antes de "corrigir" — pode ser um artefato do próprio script de teste (timing de uma transição CSS, modal anterior ainda aberto) e não um bug real do componente.

---

## 5. Commits e Pull Request

- Commits pequenos, um por mudança lógica, sempre `feat(front): <descrição em português>` (ou `fix(front):` quando for correção de bug), com a trailer:
  ```
  Co-Authored-By: Claude <modelo> <noreply@anthropic.com>
  ```
- Não existe `CONTRIBUTING.md` nem template de PR neste repositório — siga o padrão observado no histórico de commits e no corpo da PR #4 (`feat/formulario`).
- Ao final da implementação, abra a PR com `gh pr create`, com um resumo das mudanças e um plano de testes no corpo da descrição.
