import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { AgendamentoItem, FiltrosFila, MinhaAreaItem } from '../funcionario/types';
import { filtrarAgendamentos, FILTROS_VAZIOS } from '../shared/utils/filtrarAgendamentos';
import { derivarRegioes, fetchMesorregioes, fetchMunicipios, FORA_DO_ESTADO } from '../shared/services/ibge';
import type { MunicipioIBGE } from '../shared/services/ibge';
import api from '../services/api';
import { LIMITE_AGENDAMENTOS } from '../shared/constants';

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
    minhaAreaFiltrada.value.filter((item) => item.estado === 'FINALIZADO' && item.resultado)
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
    let successful = true;

    if (!opcoes.silencioso) isLoading.value = true;

    await carregarDadosIBGE();

    await api.get<AgendamentoItem[]>(`/api/funcionario/agendamentos?limit=${LIMITE_AGENDAMENTOS}`)
      .then(async response => {
        const { data } = response;
        agendamentos.value = await preencherRegioes<AgendamentoItem>(data);
      })
      .catch(_ => {
        successful = false;
      });

    if (!opcoes.silencioso) isLoading.value = false;

    return successful;
  }

  async function puxarAgendamento(id: number): Promise<number> {
    const item = agendamentos.value.find(agendamento => agendamento.id === id);
    
    let statusCode = -1;
    await api.post(`/api/funcionario/agendamentos/${item?.solicitacao}/${item?.exameCodigo}/puxar`)
      .then(response => statusCode = response.status)
      .catch(error => statusCode = error.status);

    return statusCode;
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
  async function fetchMinhaArea(opcoes: { silencioso?: boolean } = {}): Promise<boolean> {
    let successful = true;

    if (!opcoes.silencioso) isLoadingMinhaArea.value = true;
    await carregarDadosIBGE();
    await api.get<MinhaAreaItem[]>(`/api/funcionario/minha-area`)
      .then(async response => {
        const { data } = response;
        minhaArea.value = await preencherRegioes<MinhaAreaItem>(data);
      })
      .catch(_ => {
        successful = false;
      });

    if (!opcoes.silencioso) isLoadingMinhaArea.value = false;
    
    return successful;
  }

  async function aguardarConfirmacao(id: number): Promise<boolean> {
    let successful = true;
    const item = minhaArea.value.find(agendamento => agendamento.id === id);

    await api.post(`/api/funcionario/minha-area/${item?.solicitacao}/${item?.exameCodigo}/aguardar-confirmacao`)
      .catch(_ => successful = false);
    
    return successful;
  }

  async function devolverAFila(id: number, _motivo: string) {
    let successful = true;
    const item = minhaArea.value.find(agendamento => agendamento.id === id);

    await api.post(
        `/api/funcionario/minha-area/${item?.solicitacao}/${item?.exameCodigo}/devolver`,
        { motivo: _motivo }
      ).catch(_ => successful = false);
    
    return successful;
  }

  async function reportarProblema(id: number, _motivo: string, _detalhes?: string) {
    let successful = true;
    console.log(minhaArea.value);
    const item = minhaArea.value.find(agendamento => agendamento.id === id);

    await api.post(
        `/api/funcionario/minha-area/${item?.solicitacao}/${item?.exameCodigo}/reportar-problema`,
        {
          motivo: _motivo,
          detalhes: _detalhes
        }
      ).catch(_ => successful = false);
    
    return successful;
  }

  async function finalizarAgendamento(id: number) {
    let successful = true;
    const item = minhaArea.value.find(agendamento => agendamento.id === id);

    await api.post(
        `/api/funcionario/minha-area/${item?.solicitacao}/${item?.exameCodigo}/finalizar`,
        { resultado: "CONFIRMADO" }
      )
      .catch(_ => successful = false);
    
    return successful;
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
    carregarDadosIBGE,
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
