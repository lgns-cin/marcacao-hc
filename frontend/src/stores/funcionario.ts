import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { AgendamentoItem, FiltrosFila, MinhaAreaItem } from '../funcionario/types';
import { FILTROS_VAZIOS } from '../shared/utils/filtrarAgendamentos';
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

  const agendamentosFiltrados = computed(() => agendamentos.value);

  // computed - minha área
  const minhaAreaFiltrada = computed(() => minhaArea.value);

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

    const params = new URLSearchParams();
    params.append('limit', String(LIMITE_AGENDAMENTOS));
    if (filtros.value.busca) params.append('busca', filtros.value.busca);
    if (filtros.value.regioes.length > 0) params.append('regioes', filtros.value.regioes.join(','));
    if (filtros.value.municipio) params.append('municipio', filtros.value.municipio);
    if (filtros.value.tiposExame.length > 0) params.append('tipos_exame', filtros.value.tiposExame.join(','));
    if (filtros.value.faixaEtaria && filtros.value.faixaEtaria !== 'Todas') {
      let faixa = '';
      if (filtros.value.faixaEtaria === '0-17') faixa = 'menor_idade';
      else if (filtros.value.faixaEtaria === '18-59') faixa = 'adulto';
      else if (filtros.value.faixaEtaria === '60+') faixa = 'idoso';
      if (faixa) params.append('faixa_etaria', faixa);
    }

    await api.get<AgendamentoItem[]>(`/api/funcionario/agendamentos?${params.toString()}`)
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
    fetchAgendamentos({ silencioso: true });
  }

  function aplicarFiltros(novosFiltros: Partial<FiltrosFila>) {
    filtros.value = { ...filtros.value, ...novosFiltros };
    fetchAgendamentos();
  }

  function limparFiltros() {
    const buscaAtual = filtros.value.busca;
    filtros.value = { ...FILTROS_VAZIOS, busca: buscaAtual };
    fetchAgendamentos();
  }

  // actions - minha área
  async function fetchMinhaArea(opcoes: { silencioso?: boolean } = {}): Promise<boolean> {
    let successful = true;

    if (!opcoes.silencioso) isLoadingMinhaArea.value = true;
    await carregarDadosIBGE();

    const params = new URLSearchParams();
    if (filtrosMinhaArea.value.busca) params.append('busca', filtrosMinhaArea.value.busca);
    if (filtrosMinhaArea.value.regioes.length > 0) params.append('regioes', filtrosMinhaArea.value.regioes.join(','));
    if (filtrosMinhaArea.value.municipio) params.append('municipio', filtrosMinhaArea.value.municipio);
    if (filtrosMinhaArea.value.tiposExame.length > 0) params.append('tipos_exame', filtrosMinhaArea.value.tiposExame.join(','));
    if (filtrosMinhaArea.value.faixaEtaria && filtrosMinhaArea.value.faixaEtaria !== 'Todas') {
      let faixa = '';
      if (filtrosMinhaArea.value.faixaEtaria === '0-17') faixa = 'menor_idade';
      else if (filtrosMinhaArea.value.faixaEtaria === '18-59') faixa = 'adulto';
      else if (filtrosMinhaArea.value.faixaEtaria === '60+') faixa = 'idoso';
      if (faixa) params.append('faixa_etaria', faixa);
    }

    await api.get<MinhaAreaItem[]>(`/api/funcionario/minha-area?${params.toString()}`)
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
    fetchMinhaArea({ silencioso: true });
  }

  function aplicarFiltrosMinhaArea(novosFiltros: Partial<FiltrosFila>) {
    filtrosMinhaArea.value = { ...filtrosMinhaArea.value, ...novosFiltros };
    fetchMinhaArea();
  }

  function limparFiltrosMinhaArea() {
    const buscaAtual = filtrosMinhaArea.value.busca;
    filtrosMinhaArea.value = { ...FILTROS_VAZIOS, busca: buscaAtual };
    fetchMinhaArea();
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
