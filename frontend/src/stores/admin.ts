import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { FiltrosFila } from '../funcionario/types';
import { filtrarAgendamentos, FILTROS_VAZIOS } from '../shared/utils/filtrarAgendamentos';
import type { AgendamentoGerenciamento, AgendamentoRemovido, Funcionario, Kpi, PendenciaItem, VisaoGeral, SerieBarrasEtapas } from '../admin/types';
import api from '../services/api';
import { TITULOS_KPIS } from '../shared/constants';

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
        visaoGeral.value = null;
    } finally {
      if (!opcoes.silencioso) isLoadingVisaoGeral.value = false;
    }
  }

  // Pendências
  async function fetchPendencias(opcoes: { silencioso?: boolean } = {}) {
    if (!opcoes.silencioso) isLoadingPendencias.value = true;
    try {
      const response = await api.get<PendenciaItem[]>(`/api/admin/pendencias`);
      pendencias.value = response.data;
    } catch {
      pendencias.value = [];
    } finally {
      if (!opcoes.silencioso) isLoadingPendencias.value = false;
    }
  }

  // Filtros
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
    try {
      const [resEmAndamento, resConcluidos, resRemovidos] = await Promise.all([
        api.get<AgendamentoGerenciamento[]>(`/api/admin/agendamentos?estado=em_andamento`),
        api.get<AgendamentoGerenciamento[]>(`/api/admin/agendamentos?estado=concluidos`),
        api.get<AgendamentoRemovido[]>(`/api/admin/agendamentos?estado=excluidos`),
      ]);
      agendamentosEmAndamento.value = resEmAndamento.data;
      agendamentosConcluidos.value = resConcluidos.data;
      agendamentosRemovidos.value = resRemovidos.data;
    } catch {
      agendamentosEmAndamento.value = [];
      agendamentosConcluidos.value = [];
      agendamentosRemovidos.value = [];
    } finally {
      if (!opcoes.silencioso) isLoadingAgendamentos.value = false;
    }
  }

  async function reatribuirAgendamento(id: number, funcionarioUsername: string) {
    try {
      const item = agendamentosEmAndamento.value.find((i) => i.id === id) ??
        pendencias.value.find((i) => i.id === id);
      if (!item) return;

      await api.post(`/api/admin/agendamentos/${item.solicitacao}/reatribuir`, { 
        funcionario: funcionarioUsername
      });

      // atualiza o estado local reativamente após o sucesso da API
      if (agendamentosEmAndamento.value.some(i => i.id === id)) {
        // Se estava em andamento, apenas troca o responsável na tela
        const emAndamento = agendamentosEmAndamento.value.find((i) => i.id === id);
        if (emAndamento) emAndamento.funcionarioAtribuido = funcionarioUsername;
      } else {
        // Se era uma pendência, ela foi resolvida/reatribuída, então removemos da lista de travados
        pendencias.value = pendencias.value.filter((i) => i.id !== id);
      }    
    } catch (error) {
      console.error('Erro ao reatribuir agendamento',error);
      throw error;
    } 
  }

  async function devolverAFilaAdmin(id: number, motivo: string) {
    try {
      // localiza o item em qualquer uma das listas locais para obter a propriedade 'solicitacao'
      const item =
        agendamentosEmAndamento.value.find((i) => i.id === id) ??
        agendamentosConcluidos.value.find((i) => i.id === id) ??
        pendencias.value.find((i) => i.id === id);
        
      if (!item) return;

      await api.post(`/api/admin/agendamentos/${item.solicitacao}/devolver`, { 
        motivo: motivo 
      });

      // depois do sucesso da API, remove o item localmente das listas do front-end
      agendamentosEmAndamento.value = agendamentosEmAndamento.value.filter((i) => i.id !== id);
      agendamentosConcluidos.value = agendamentosConcluidos.value.filter((i) => i.id !== id);
      pendencias.value = pendencias.value.filter((i) => i.id !== id);    } catch {
    }
  }

  async function removerProblema(id: number) {
    try {
      // localiza o item em qualquer uma das listas locais para obter a propriedade 'solicitacao'
      const item =
        agendamentosEmAndamento.value.find((i) => i.id === id) ??
        agendamentosConcluidos.value.find((i) => i.id === id) ??
        pendencias.value.find((i) => i.id === id);
        
      if (!item) return;

      await api.delete(`/api/admin/agendamentos/${item.solicitacao}`);

      // depois do sucesso da API, remove o item localmente das listas do front-end
      agendamentosEmAndamento.value = agendamentosEmAndamento.value.filter((i) => i.id !== id);
      agendamentosConcluidos.value = agendamentosConcluidos.value.filter((i) => i.id !== id);
      pendencias.value = pendencias.value.filter((i) => i.id !== id);    
    } catch {
      //
    }
  }

  // Filtros
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

  // Funcionários
  async function fetchFuncionarios() {
    try {
      const response = await api.get<Funcionario[]>('/api/admin/funcionarios');
      funcionarios.value = response.data;
    } catch (error) {
      console.error('Erro ao buscar funcionários', error);
    }
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
    setBuscaPendencias,
    aplicarFiltrosPendencias,
    limparFiltrosPendencias,
    removerProblema,

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
    setBuscaAgendamentos,
    aplicarFiltrosAgendamentos,
    limparFiltrosAgendamentos,

    funcionarios,
    fetchFuncionarios,
  };
});