import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { AgendamentoItem, FiltrosFila, MinhaAreaItem, ResultadoFinalizacao } from '../funcionario/types';
import { filtrarAgendamentos, FILTROS_VAZIOS } from '../shared/utils/filtrarAgendamentos';
import { derivarRegioes, fetchMesorregioes, fetchMunicipios, FORA_DO_ESTADO } from '../shared/services/ibge';
import type { MunicipioIBGE } from '../shared/services/ibge';
import { AGENDAMENTOS_MOCK, MINHA_AREA_MOCK } from '../funcionario/mockData';

export const useFuncionarioStore = defineStore('funcionario', () => {
  // state - fila de agendamento
  const agendamentos = ref<AgendamentoItem[]>([]);
  const isLoading = ref(false);
  const filtros = ref<FiltrosFila>({ ...FILTROS_VAZIOS });

  // state - minha área
  const minhaArea = ref<MinhaAreaItem[]>([]);
  const isLoadingMinhaArea = ref(false);
  const filtrosMinhaArea = ref<FiltrosFila>({ ...FILTROS_VAZIOS });

  // state - IBGE
  const regioes = ref<string[]>([]);
  const municipiosIBGE = ref<MunicipioIBGE[]>([]);

  // computed - fila de agendamento
  const totalAgendamentos = computed(() => agendamentos.value.length);

  const agendamentosFiltrados = computed(() => filtrarAgendamentos(agendamentos.value, filtros.value));

  // computed - minha área
  const minhaAreaFiltrada = computed(() => filtrarAgendamentos(minhaArea.value, filtrosMinhaArea.value));

  const itensEmAndamento = computed(() =>
    minhaAreaFiltrada.value.filter((item) => item.estado === 'EM_ANDAMENTO')
  );

  const itensAguardandoConfirmacao = computed(() =>
    minhaAreaFiltrada.value.filter((item) => item.estado === 'AGUARDANDO_CONFIRMACAO')
  );

  const itensFinalizados = computed(() =>
    minhaAreaFiltrada.value.filter((item) => item.estado === 'FINALIZADO')
  );

  const nomesMunicipios = computed(() =>
    municipiosIBGE.value.map((m) => m.nome),
  );

  async function preencherRegioes<T extends { localizacao: string }>(
    itens: Omit<T, 'regiao'>[],
  ): Promise<(T & { regiao: string })[]> {
    //geramos o dic de uma vez só para os itens enviados
    const mapaRegioes = await derivarRegioes(itens);

    //monta o array final instantaneamente sem fazer novas buscas
    return itens.map((item) => {
      const chave = item.localizacao.trim().toLowerCase();
      return {
        ...item,
        regiao: mapaRegioes.get(chave) ?? 'FORA_DO_ESTADO',
      };
    }) as (T & { regiao: string })[];
  }

  // colocamos essa função aqui porque ela depende do state do store
  // por isso não colocamos ela junto com as outras funções de ibge.
  // essa função vai popular o state do store com os dados do ibge
  async function carregarDadosIBGE() {
    const [mesorregioes, municipios] = await Promise.all([
      fetchMesorregioes(),
      fetchMunicipios(),
    ]);
    regioes.value = [...mesorregioes, FORA_DO_ESTADO]; // adicionamos a mesorregião "Fora do Estado"
    municipiosIBGE.value = municipios; // guardamos os municipios
  }

  // actions - fila de agendamento
  async function fetchAgendamentos(opcoes: { silencioso?: boolean } = {}) {
    if (!opcoes.silencioso) isLoading.value = true;
    await carregarDadosIBGE();
    agendamentos.value = await preencherRegioes<AgendamentoItem>(AGENDAMENTOS_MOCK);
    if (!opcoes.silencioso) isLoading.value = false;
  }

  async function puxarAgendamento(id: number) {
    // Remove localmente (mock)
    agendamentos.value = agendamentos.value.filter((i) => i.id !== id);
  }

  function setBusca(busca: string) {
    filtros.value.busca = busca;
  }

  function aplicarFiltros(novosFiltros: Partial<FiltrosFila>) {
    filtros.value = { ...filtros.value, ...novosFiltros };
  }

  function limparFiltros() {
    const buscaAtual = filtros.value.busca;
    filtros.value = { ...FILTROS_VAZIOS, busca: buscaAtual };
  }

  // actions - minha área
  async function fetchMinhaArea(opcoes: { silencioso?: boolean } = {}) {
    if (!opcoes.silencioso) isLoadingMinhaArea.value = true;
    await carregarDadosIBGE();
    minhaArea.value = await preencherRegioes<MinhaAreaItem>(MINHA_AREA_MOCK);
    if (!opcoes.silencioso) isLoadingMinhaArea.value = false;
  }

  async function aguardarConfirmacao(id: number) {
    const item = minhaArea.value.find((i) => i.id === id);
    if (item) item.estado = 'AGUARDANDO_CONFIRMACAO';
  }

  async function devolverAFila(id: number, _motivo: string) {
    minhaArea.value = minhaArea.value.filter((i) => i.id !== id);
  }

  async function reportarProblema(_id: number, _motivo: string) {
    // mock: sem efeito
  }

  async function finalizarAgendamento(id: number, resultado: ResultadoFinalizacao) {
    const item = minhaArea.value.find((i) => i.id === id);
    if (item) {
      item.estado = 'FINALIZADO';
      item.resultado = resultado;
    }
  }

  function setBuscaMinhaArea(busca: string) {
    filtrosMinhaArea.value.busca = busca;
  }

  function aplicarFiltrosMinhaArea(novosFiltros: Partial<FiltrosFila>) {
    filtrosMinhaArea.value = { ...filtrosMinhaArea.value, ...novosFiltros };
  }

  function limparFiltrosMinhaArea() {
    const buscaAtual = filtrosMinhaArea.value.busca;
    filtrosMinhaArea.value = { ...FILTROS_VAZIOS, busca: buscaAtual };
  }

  return {
    agendamentos,
    isLoading,
    filtros,
    totalAgendamentos,
    agendamentosFiltrados,
    regioes,
    municipiosIBGE,
    nomesMunicipios,
    fetchAgendamentos,
    puxarAgendamento,
    setBusca,
    aplicarFiltros,
    limparFiltros,

    minhaArea,
    isLoadingMinhaArea,
    filtrosMinhaArea,
    minhaAreaFiltrada,
    itensEmAndamento,
    itensAguardandoConfirmacao,
    itensFinalizados,
    fetchMinhaArea,
    aguardarConfirmacao,
    devolverAFila,
    reportarProblema,
    finalizarAgendamento,
    setBuscaMinhaArea,
    aplicarFiltrosMinhaArea,
    limparFiltrosMinhaArea,
  };
});
