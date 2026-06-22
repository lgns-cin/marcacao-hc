import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';
import type { AgendamentoItem, FiltrosFila } from '../funcionario/types';
import { filtrarAgendamentos, FILTROS_VAZIOS } from '../shared/utils/filtrarAgendamentos';
import type { AgendamentoGerenciamento, Funcionario, PendenciaItem, VisaoGeral } from '../admin/types';
import { PREFERENCIAS_VISAO_GERAL_KEY } from '../admin/types';

function carregarPreferenciasIniciais(): string[] | null {
  try {
    const salvas = localStorage.getItem(PREFERENCIAS_VISAO_GERAL_KEY);
    return salvas ? JSON.parse(salvas) : null;
  } catch {
    return null;
  }
}

export const useAdminStore = defineStore('admin', () => {
  // state - visão geral
  const visaoGeral = ref<VisaoGeral | null>(null);
  const isLoadingVisaoGeral = ref(false);
  const indicadoresVisiveis = ref<string[] | null>(carregarPreferenciasIniciais());

  // state - pendências
  const pendencias = ref<PendenciaItem[]>([]);
  const isLoadingPendencias = ref(false);
  const filtrosPendencias = ref<FiltrosFila>({ ...FILTROS_VAZIOS });

  // state - gerenciamento de agendamentos
  const agendamentosEmAndamento = ref<AgendamentoGerenciamento[]>([]);
  const agendamentosConcluidos = ref<AgendamentoGerenciamento[]>([]);
  const isLoadingAgendamentos = ref(false);
  const filtrosAgendamentos = ref<FiltrosFila>({ ...FILTROS_VAZIOS });

  // state - fila de agendamento (visão admin, somente leitura)
  const fila = ref<AgendamentoItem[]>([]);
  const isLoadingFila = ref(false);
  const filtrosFila = ref<FiltrosFila>({ ...FILTROS_VAZIOS });

  // state - funcionários (para reatribuição)
  const funcionarios = ref<Funcionario[]>([]);

  // computed - visão geral
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

  // computed - listas filtradas
  const pendenciasFiltradas = computed(() => filtrarAgendamentos(pendencias.value, filtrosPendencias.value));
  const agendamentosEmAndamentoFiltrados = computed(() =>
    filtrarAgendamentos(agendamentosEmAndamento.value, filtrosAgendamentos.value)
  );
  const agendamentosConcluidosFiltrados = computed(() =>
    filtrarAgendamentos(agendamentosConcluidos.value, filtrosAgendamentos.value)
  );
  const filaFiltrada = computed(() => filtrarAgendamentos(fila.value, filtrosFila.value));

  // actions - visão geral
  async function fetchVisaoGeral(opcoes: { silencioso?: boolean } = {}) {
    if (!opcoes.silencioso) isLoadingVisaoGeral.value = true;
    try {
      const { data } = await api.get('/api/admin/visao-geral');
      visaoGeral.value = data;
    } finally {
      if (!opcoes.silencioso) isLoadingVisaoGeral.value = false;
    }
  }

  function definirIndicadoresVisiveis(ids: string[]) {
    indicadoresVisiveis.value = ids;
    localStorage.setItem(PREFERENCIAS_VISAO_GERAL_KEY, JSON.stringify(ids));
  }

  // actions - pendências
  async function fetchPendencias(opcoes: { silencioso?: boolean } = {}) {
    if (!opcoes.silencioso) isLoadingPendencias.value = true;
    try {
      const { data } = await api.get('/api/admin/pendencias');
      pendencias.value = data;
    } finally {
      if (!opcoes.silencioso) isLoadingPendencias.value = false;
    }
  }

  async function resolverPendencia(id: number) {
    await api.post(`/api/admin/pendencias/${id}/resolver`);
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

  // actions - gerenciamento de agendamentos
  async function fetchAgendamentosGerenciamento(opcoes: { silencioso?: boolean } = {}) {
    if (!opcoes.silencioso) isLoadingAgendamentos.value = true;
    try {
      const [emAndamento, concluidos] = await Promise.all([
        api.get('/api/admin/agendamentos', { params: { estado: 'em_andamento' } }),
        api.get('/api/admin/agendamentos', { params: { estado: 'concluido' } }),
      ]);
      agendamentosEmAndamento.value = emAndamento.data;
      agendamentosConcluidos.value = concluidos.data;
    } finally {
      if (!opcoes.silencioso) isLoadingAgendamentos.value = false;
    }
  }

  async function reatribuirAgendamento(id: number, funcionario: string) {
    await api.post(`/api/admin/agendamentos/${id}/reatribuir`, { funcionario });
    await fetchAgendamentosGerenciamento({ silencioso: true });
  }

  async function devolverAFilaAdmin(id: number, motivo: string) {
    await api.post(`/api/admin/agendamentos/${id}/devolver`, { motivo });
    agendamentosEmAndamento.value = agendamentosEmAndamento.value.filter((i) => i.id !== id);
    agendamentosConcluidos.value = agendamentosConcluidos.value.filter((i) => i.id !== id);
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

  // actions - fila de agendamento (admin)
  async function fetchFila(opcoes: { silencioso?: boolean } = {}) {
    if (!opcoes.silencioso) isLoadingFila.value = true;
    try {
      const { data } = await api.get('/api/funcionario/agendamentos');
      fila.value = data;
    } finally {
      if (!opcoes.silencioso) isLoadingFila.value = false;
    }
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

  // actions - funcionários
  async function fetchFuncionarios() {
    const { data } = await api.get('/api/admin/funcionarios');
    funcionarios.value = data;
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
    isLoadingAgendamentos,
    filtrosAgendamentos,
    agendamentosEmAndamentoFiltrados,
    agendamentosConcluidosFiltrados,
    fetchAgendamentosGerenciamento,
    reatribuirAgendamento,
    devolverAFilaAdmin,
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
