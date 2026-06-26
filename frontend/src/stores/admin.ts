import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { AgendamentoItem, FiltrosFila } from '../funcionario/types';
import { filtrarAgendamentos, FILTROS_VAZIOS } from '../shared/utils/filtrarAgendamentos';
import type { AgendamentoGerenciamento, AgendamentoRemovido, Funcionario, Kpi, PendenciaItem, VisaoGeral } from '../admin/types';
import { PREFERENCIAS_VISAO_GERAL_KEY } from '../admin/types';
import {
  MOCK_FUNCIONARIOS,
  MOCK_VISAO_GERAL,
  MOCK_PENDENCIAS,
  MOCK_GERENCIAMENTO_ANDAMENTO,
  MOCK_GERENCIAMENTO_CONCLUIDO,
  MOCK_REMOVIDOS,
  MOCK_FILA_ADMIN,
} from '../admin/mockData';

// isso é só pra funcionar por enquanto ...
function carregarPreferenciasIniciais(): string[] | null {
  try {
    const salvas = localStorage.getItem(PREFERENCIAS_VISAO_GERAL_KEY);
    return salvas ? JSON.parse(salvas) : null;
  } catch {
    return null;
  }
}

export const useAdminStore = defineStore('admin', () => {
  // Estados
  const visaoGeral = ref<VisaoGeral | null>(null);
  const isLoadingVisaoGeral = ref(false);
  const indicadoresVisiveis = ref<string[] | null>(carregarPreferenciasIniciais());

  const pendencias = ref<PendenciaItem[]>([]);
  const isLoadingPendencias = ref(false);
  const filtrosPendencias = ref<FiltrosFila>({ ...FILTROS_VAZIOS });

  const agendamentosEmAndamento = ref<AgendamentoGerenciamento[]>([]);
  const agendamentosConcluidos = ref<AgendamentoGerenciamento[]>([]);
  const agendamentosRemovidos = ref<AgendamentoRemovido[]>([]);
  const isLoadingAgendamentos = ref(false);
  const filtrosAgendamentos = ref<FiltrosFila>({ ...FILTROS_VAZIOS });

  const fila = ref<AgendamentoItem[]>([]);
  const isLoadingFila = ref(false);
  const filtrosFila = ref<FiltrosFila>({ ...FILTROS_VAZIOS });

  const funcionarios = ref<Funcionario[]>([]);

  // Computed
  const kpisVisiveis = computed(() => {
    if (!visaoGeral.value) return [];
    if (!indicadoresVisiveis.value) return visaoGeral.value.kpis;
    return visaoGeral.value.kpis.filter((kpi) => indicadoresVisiveis.value!.includes(kpi.id));
  });

  const graficosVisiveis = computed(() => {
    if (!visaoGeral.value) return [];
    if (!indicadoresVisiveis.value) return visaoGeral.value.graficos;
    return visaoGeral.value.graficos.filter((g) => indicadoresVisiveis.value!.includes(g.id));
  });

  const todosIndicadores = computed(() => {
    if (!visaoGeral.value) return [];
    return [
      ...visaoGeral.value.kpis.map((k) => ({ id: k.id, label: k.label })),
      ...visaoGeral.value.graficos.map((g) => ({ id: g.id, label: g.titulo })),
    ];
  });

  const pendenciasFiltradas = computed(() => filtrarAgendamentos(pendencias.value, filtrosPendencias.value));
  const agendamentosEmAndamentoFiltrados = computed(() =>
    filtrarAgendamentos(agendamentosEmAndamento.value, filtrosAgendamentos.value)
  );
  const agendamentosConcluidosFiltrados = computed(() =>
    filtrarAgendamentos(agendamentosConcluidos.value, filtrosAgendamentos.value)
  );
  const agendamentosRemovidosFiltrados = computed(() =>
    filtrarAgendamentos(agendamentosRemovidos.value, filtrosAgendamentos.value)
  );
  const filaFiltrada = computed(() => filtrarAgendamentos(fila.value, filtrosFila.value));

  //Ações

  // Visão Geral
  function calcularKpis(): Kpi[] {
    // As KPIs são apresentadas no contexto das vagas, liberadas por mês
    // (validado com a Taty) — sempre no recorte do mês atual.
    const PERIODO = 'no mês atual';

    const totalCards = MOCK_FILA_ADMIN.length
      + MOCK_GERENCIAMENTO_ANDAMENTO.length
      + MOCK_GERENCIAMENTO_CONCLUIDO.length
      + MOCK_PENDENCIAS.length;

    const totalFuncionarios = MOCK_FUNCIONARIOS.length;

    const mediaCardFuncionario = totalFuncionarios > 0
      ? +(totalCards / totalFuncionarios).toFixed(1)
      : 0;

    const percentProblematicas = totalCards > 0
      ? +((MOCK_PENDENCIAS.length / totalCards) * 100).toFixed(1)
      : 0;

    const percentConcluidas = totalCards > 0
      ? +((MOCK_GERENCIAMENTO_CONCLUIDO.length / totalCards) * 100).toFixed(1)
      : 0;

    // Tempo médio de marcação: tempo até o caso ser efetivamente marcado/concluído.
    // Aproximado pelos dias na fila dos agendamentos já concluídos.
    const tempoMedioMarcacao = MOCK_GERENCIAMENTO_CONCLUIDO.length > 0
      ? +(MOCK_GERENCIAMENTO_CONCLUIDO.reduce((acc, i) => acc + i.diasNaFila, 0) / MOCK_GERENCIAMENTO_CONCLUIDO.length).toFixed(1)
      : 0;

    return [
      { id: 'media_card_funcionario', label: 'Média de Exames por Funcionário ', valor: mediaCardFuncionario, categoria: 'principal', periodo: PERIODO },
      { id: 'percent_problematicas', label: 'Solicitações problemáticas ', valor: percentProblematicas, sufixo: '%', categoria: 'principal', periodo: PERIODO },
      { id: 'percent_concluidas', label: 'Solicitações concluídas ', valor: percentConcluidas, sufixo: '%', categoria: 'principal', periodo: PERIODO },
      { id: 'tempo_medio_marcacao', label: 'Tempo médio de marcação ', valor: tempoMedioMarcacao, sufixo: 'dias', categoria: 'principal', periodo: PERIODO },
    ];
  }

  async function fetchVisaoGeral(opcoes: { silencioso?: boolean } = {}) {
    if (!opcoes.silencioso) isLoadingVisaoGeral.value = true;
    await new Promise((r) => setTimeout(r, 300));
    visaoGeral.value = { kpis: calcularKpis(), graficos: MOCK_VISAO_GERAL.graficos };
    if (!opcoes.silencioso) isLoadingVisaoGeral.value = false;
  }

  function definirIndicadoresVisiveis(ids: string[]) {
    indicadoresVisiveis.value = ids;
    localStorage.setItem(PREFERENCIAS_VISAO_GERAL_KEY, JSON.stringify(ids));
  }

  // Pendências
  async function fetchPendencias(opcoes: { silencioso?: boolean } = {}) {
    if (!opcoes.silencioso) isLoadingPendencias.value = true;
    await new Promise((r) => setTimeout(r, 300));
    pendencias.value = MOCK_PENDENCIAS;
    if (!opcoes.silencioso) isLoadingPendencias.value = false;
  }

  async function resolverPendencia(id: number) {
    await new Promise((r) => setTimeout(r, 200));
    const item = pendencias.value.find((i) => i.id === id);
    if (item) {
      agendamentosRemovidos.value = [
        ...agendamentosRemovidos.value,
        {
          ...item,
          problema_motivo: item.problema_motivo ?? '',
          problema_detalhes: item.problema_detalhes,
        },
      ];
    }
    pendencias.value = pendencias.value.filter((i) => i.id !== id);
  }

  function setBuscaPendencias(busca: string) {
    filtrosPendencias.value.busca = busca;
  }

  function aplicarFiltrosPendencias(novosFiltros: Partial<FiltrosFila>) {
    filtrosPendencias.value = { ...filtrosPendencias.value, ...novosFiltros };
  }

  function limparFiltrosPendencias() {
    const buscaAtual = filtrosPendencias.value.busca;
    filtrosPendencias.value = { ...FILTROS_VAZIOS, busca: buscaAtual };
  }

  // Gerenciamento de Agendamentos
  async function fetchAgendamentosGerenciamento(opcoes: { silencioso?: boolean } = {}) {
    if (!opcoes.silencioso) isLoadingAgendamentos.value = true;
    await new Promise((r) => setTimeout(r, 300));
    agendamentosEmAndamento.value = [...MOCK_GERENCIAMENTO_ANDAMENTO];
    agendamentosConcluidos.value = [...MOCK_GERENCIAMENTO_CONCLUIDO];
    agendamentosRemovidos.value = [...MOCK_REMOVIDOS];
    if (!opcoes.silencioso) isLoadingAgendamentos.value = false;
  }

  async function reatribuirAgendamento(id: number, funcionarioUsername: string) {
    await new Promise((r) => setTimeout(r, 200));
    const item = agendamentosEmAndamento.value.find((i) => i.id === id);
    if (item) {
      item.responsavel = funcionarioUsername;
      return;
    }
    // Reatribuir uma pendência: o caso passa para o novo funcionário e deixa de estar parado/bloqueado.
    const pendencia = pendencias.value.find((i) => i.id === id);
    if (pendencia) {
      pendencias.value = pendencias.value.filter((i) => i.id !== id);
    }
  }

  async function devolverAFilaAdmin(id: number, motivo: string) {
    await new Promise((r) => setTimeout(r, 200));
    // Localiza o item em qualquer uma das listas para registrar a devolução com o motivo.
    const item =
      agendamentosEmAndamento.value.find((i) => i.id === id) ??
      agendamentosConcluidos.value.find((i) => i.id === id) ??
      pendencias.value.find((i) => i.id === id);
    if (item) {
      // Detalhes originais, caso o item devolvido seja uma pendência já com problema reportado.
      const detalhesOriginais = (item as PendenciaItem).problema_detalhes ?? null;
      const removido: AgendamentoRemovido = {
        id: item.id,
        nome: item.nome,
        prontuario: item.prontuario,
        numeroSolicitacao: item.numeroSolicitacao,
        exame: item.exame,
        diasNaFila: item.diasNaFila,
        status: item.status,
        unidadeSolicitante: item.unidadeSolicitante,
        dataRetorno: item.dataRetorno,
        localizacao: item.localizacao,
        regiao: item.regiao,
        idade: item.idade,
        telefone: item.telefone,
        responsavel: item.responsavel ?? '',
        problema_motivo: motivo,
        problema_detalhes: detalhesOriginais,
      };
      agendamentosRemovidos.value = [...agendamentosRemovidos.value, removido];
    }
    agendamentosEmAndamento.value = agendamentosEmAndamento.value.filter((i) => i.id !== id);
    agendamentosConcluidos.value = agendamentosConcluidos.value.filter((i) => i.id !== id);
    pendencias.value = pendencias.value.filter((i) => i.id !== id);
  }

  async function devolverRemovidoAFila(id: number) {
    await new Promise((r) => setTimeout(r, 200));
    agendamentosRemovidos.value = agendamentosRemovidos.value.filter((i) => i.id !== id);
  }

  async function removerDaFila(id: number) {
    await new Promise((r) => setTimeout(r, 200));
    agendamentosRemovidos.value = agendamentosRemovidos.value.filter((i) => i.id !== id);
  }

  function setBuscaAgendamentos(busca: string) {
    filtrosAgendamentos.value.busca = busca;
  }

  function aplicarFiltrosAgendamentos(novosFiltros: Partial<FiltrosFila>) {
    filtrosAgendamentos.value = { ...filtrosAgendamentos.value, ...novosFiltros };
  }

  function limparFiltrosAgendamentos() {
    const buscaAtual = filtrosAgendamentos.value.busca;
    filtrosAgendamentos.value = { ...FILTROS_VAZIOS, busca: buscaAtual };
  }

  // Fila Pública (Visão Admin)
  async function fetchFila(opcoes: { silencioso?: boolean } = {}) {
    if (!opcoes.silencioso) isLoadingFila.value = true;
    await new Promise((r) => setTimeout(r, 300));
    fila.value = MOCK_FILA_ADMIN;
    if (!opcoes.silencioso) isLoadingFila.value = false;
  }

  function setBuscaFila(busca: string) {
    filtrosFila.value.busca = busca;
  }

  function aplicarFiltrosFila(novosFiltros: Partial<FiltrosFila>) {
    filtrosFila.value = { ...filtrosFila.value, ...novosFiltros };
  }

  function limparFiltrosFila() {
    const buscaAtual = filtrosFila.value.busca;
    filtrosFila.value = { ...FILTROS_VAZIOS, busca: buscaAtual };
  }

  // Funcionários
  async function fetchFuncionarios() {
    await new Promise((r) => setTimeout(r, 100));
    funcionarios.value = MOCK_FUNCIONARIOS;
  }

  return {
    visaoGeral,
    isLoadingVisaoGeral,
    indicadoresVisiveis,
    kpisVisiveis,
    graficosVisiveis,
    todosIndicadores,
    fetchVisaoGeral,
    definirIndicadoresVisiveis,

    pendencias,
    isLoadingPendencias,
    filtrosPendencias,
    pendenciasFiltradas,
    fetchPendencias,
    resolverPendencia,
    setBuscaPendencias,
    aplicarFiltrosPendencias,
    limparFiltrosPendencias,

    agendamentosEmAndamento,
    agendamentosConcluidos,
    agendamentosRemovidos,
    isLoadingAgendamentos,
    filtrosAgendamentos,
    agendamentosEmAndamentoFiltrados,
    agendamentosConcluidosFiltrados,
    agendamentosRemovidosFiltrados,
    fetchAgendamentosGerenciamento,
    reatribuirAgendamento,
    devolverAFilaAdmin,
    devolverRemovidoAFila,
    removerDaFila,
    setBuscaAgendamentos,
    aplicarFiltrosAgendamentos,
    limparFiltrosAgendamentos,

    fila,
    isLoadingFila,
    filtrosFila,
    filaFiltrada,
    fetchFila,
    setBuscaFila,
    aplicarFiltrosFila,
    limparFiltrosFila,

    funcionarios,
    fetchFuncionarios,
  };
});