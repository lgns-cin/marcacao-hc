import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { AgendamentoItem, FiltrosFila } from '../funcionario/types';
import { filtrarAgendamentos, FILTROS_VAZIOS } from '../shared/utils/filtrarAgendamentos';
import type { AgendamentoGerenciamento, AgendamentoRemovido, Funcionario, Kpi, PendenciaItem, VisaoGeral, SerieBarrasEtapas } from '../admin/types';
import {
  MOCK_FUNCIONARIOS,
  MOCK_PENDENCIAS,
  MOCK_GERENCIAMENTO_ANDAMENTO,
  MOCK_GERENCIAMENTO_CONCLUIDO,
  MOCK_REMOVIDOS,
  MOCK_FILA_ADMIN,
} from '../admin/mockData';
import { mockDelay } from '../shared/utils/mockDelay';
import api from '../services/api';

const TITULOS_KPIS: Record<string, string> = {
  media_cards_por_funcionario: 'Média de exames por funcionário',
  pct_problematicas: 'Exames problemáticos',
  pct_concluidas: 'Exames concluídos',
  tempo_medio_atendimento_dias: 'Tempo médio de atendimento',
};

export const useAdminStore = defineStore('admin', () => {
  // Estados
  const visaoGeral = ref<VisaoGeral | null>(null);
  const isLoadingVisaoGeral = ref(false);

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


  // Visão Geral
  async function fetchVisaoGeral(opcoes: { silencioso?: boolean } = {}) {
    if (!opcoes.silencioso) isLoadingVisaoGeral.value = true;
    try {
      const [resKpis, resRankingExames, resRankingMunicipios] = await Promise.all([
        api.get<Kpi[]>(`/api/admin/visao-geral`),
        api.get<SerieBarrasEtapas[]>(`/api/admin/dashboard/ranking-exames`),
        api.get<SerieBarrasEtapas[]>(`/api/admin/dashboard/ranking-municipios`)
      ]);

      const kpis: Kpi[] = resKpis.data.map((kpi) => ({
        id: kpi.id,
        titulo: TITULOS_KPIS[kpi.id] ?? kpi,
        valor: kpi.valor,
        formato: kpi.formato,
      }));

      visaoGeral.value = {
        kpis,
        graficos: [
          { id: 'ranking-exames', titulo: 'Top 10 - Distribuição por Tipo de Exame', tipo: 'barras_horizontais', dados: resRankingExames.data },
          { id: 'ranking-municipios', titulo: 'Top 10 - Distribuição por Município', tipo: 'barras_horizontais', dados: resRankingMunicipios.data },
        ]
      };
    } catch {
      visaoGeral.value = {
        kpis: [
          { id: 'media_cards_por_funcionario', titulo: 'Média de exames por funcionário', valor: '3.5', formato: 'numero' },
          { id: 'porcentagem_problematicas', titulo: 'Solicitações problemáticas', valor: '25', formato: 'porcentagem' },
          { id: 'porcentagem_concluidas', titulo: 'Solicitações concluídas', valor: '25', formato: 'porcentagem' },
          { id: 'tempo_medio_marcacao', titulo: 'Tempo médio de marcação', valor: '31', formato: 'dias' },
        ],
        graficos: [
          {
            id: 'ranking-exames',
            titulo: 'Top 10 - Distribuição por Tipo de Exame',
            tipo: 'barras_horizontais',
            dados: [
              { categoria: 'Colonoscopia', pendentes: 3, emAgendamento: 2, concluidos: 8, total: 13 },
              { categoria: 'Endoscopia', pendentes: 1, emAgendamento: 6, concluidos: 4, total: 11 },
              { categoria: 'Ultrassonografia', pendentes: 2, emAgendamento: 0, concluidos: 3, total: 5 },
              { categoria: 'Mamografia', pendentes: 0, emAgendamento: 1, concluidos: 1, total: 2 },
              { categoria: 'Ecocardiograma', pendentes: 0, emAgendamento: 1, concluidos: 0, total: 1 },
            ],
          },
          {
            id: 'ranking-municipios',
            titulo: 'Top 10 - Distribuição por Município',
            tipo: 'barras_horizontais',
            dados: [
              { categoria: 'Recife', pendentes: 5, emAgendamento: 3, concluidos: 8, total: 16 },
              { categoria: 'Olinda', pendentes: 2, emAgendamento: 1, concluidos: 3, total: 6 },
              { categoria: 'Caruaru', pendentes: 1, emAgendamento: 1, concluidos: 2, total: 4 },
              { categoria: 'Petrolina', pendentes: 1, emAgendamento: 0, concluidos: 1, total: 2 },
              { categoria: 'Jaboatão dos Guararapes', pendentes: 0, emAgendamento: 1, concluidos: 1, total: 2 },
            ],
          },
        ],
      };
    } finally {
      if (!opcoes.silencioso) isLoadingVisaoGeral.value = false;
    }
  }

  // Pendências
  async function fetchPendencias(opcoes: { silencioso?: boolean } = {}) {
    if (!opcoes.silencioso) isLoadingPendencias.value = true;
    await mockDelay();
    pendencias.value = MOCK_PENDENCIAS;
    if (!opcoes.silencioso) isLoadingPendencias.value = false;
  }

  async function resolverPendencia(id: number) {
    await mockDelay('action');
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
    await mockDelay();
    agendamentosEmAndamento.value = [...MOCK_GERENCIAMENTO_ANDAMENTO];
    agendamentosConcluidos.value = [...MOCK_GERENCIAMENTO_CONCLUIDO];
    agendamentosRemovidos.value = [...MOCK_REMOVIDOS];
    if (!opcoes.silencioso) isLoadingAgendamentos.value = false;
  }

  async function reatribuirAgendamento(id: number, funcionarioUsername: string) {
    await mockDelay('action');
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
    await mockDelay('action');
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
        solicitacao: item.solicitacao,
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
    await mockDelay('action');
    agendamentosRemovidos.value = agendamentosRemovidos.value.filter((i) => i.id !== id);
  }

  async function removerDaFila(id: number) {
    await mockDelay('action');
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
    await mockDelay();
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
    await mockDelay('fast');
    funcionarios.value = MOCK_FUNCIONARIOS;
  }

  return {
    visaoGeral,
    isLoadingVisaoGeral,
    fetchVisaoGeral,

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