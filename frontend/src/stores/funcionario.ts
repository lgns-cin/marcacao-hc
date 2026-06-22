import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';
import type { AgendamentoItem, FiltrosFila, MinhaAreaItem, ResultadoFinalizacao } from '../funcionario/types';

const FILTROS_VAZIOS: FiltrosFila = {
  busca: '',
  regioes: [],
  tiposExame: [],
  municipio: '',
  faixaEtaria: 'Todas',
};

function filtrarAgendamentos<T extends AgendamentoItem>(lista: T[], filtros: FiltrosFila): T[] {
  const busca = filtros.busca.trim().toLowerCase();
  const municipio = filtros.municipio.trim().toLowerCase();

  return lista.filter((item) => {
    const correspondeBusca =
      !busca ||
      item.nome.toLowerCase().includes(busca) ||
      item.prontuario.includes(busca);

    const correspondeRegiao =
      filtros.regioes.length === 0 ||
      filtros.regioes.includes(item.regiao);

    const correspondeExame =
      filtros.tiposExame.length === 0 ||
      item.exames.some((exame) => filtros.tiposExame.includes(exame));

    const correspondeMunicipio =
      !municipio || item.localizacao.toLowerCase().includes(municipio);

    const correspondeFaixaEtaria =
      filtros.faixaEtaria === 'Todas' ||
      (filtros.faixaEtaria === '0-17' && item.idade <= 17) ||
      (filtros.faixaEtaria === '18-59' && item.idade >= 18 && item.idade <= 59) ||
      (filtros.faixaEtaria === '60+' && item.idade >= 60);

    return (
      correspondeBusca &&
      correspondeRegiao &&
      correspondeExame &&
      correspondeMunicipio &&
      correspondeFaixaEtaria
    );
  });
}

export const useFuncionarioStore = defineStore('funcionario', () => {
  // state - fila de agendamento
  const agendamentos = ref<AgendamentoItem[]>([]);
  const isLoading = ref(false);
  const filtros = ref<FiltrosFila>({ ...FILTROS_VAZIOS });

  // state - minha área
  const minhaArea = ref<MinhaAreaItem[]>([]);
  const isLoadingMinhaArea = ref(false);
  const filtrosMinhaArea = ref<FiltrosFila>({ ...FILTROS_VAZIOS });

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

  // actions - fila de agendamento
  async function fetchAgendamentos() {
    isLoading.value = true;
    try {
      const { data } = await api.get('/api/funcionario/agendamentos');
      agendamentos.value = data;
    } finally {
      isLoading.value = false;
    }
  }

  async function puxarAgendamento(id: number) {
    await api.post(`/api/funcionario/agendamentos/${id}/puxar`);
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
  async function fetchMinhaArea() {
    isLoadingMinhaArea.value = true;
    try {
      const { data } = await api.get('/api/funcionario/minha-area');
      minhaArea.value = data;
    } finally {
      isLoadingMinhaArea.value = false;
    }
  }

  async function aguardarConfirmacao(id: number) {
    await api.post(`/api/funcionario/minha-area/${id}/aguardar-confirmacao`);
    const item = minhaArea.value.find((i) => i.id === id);
    if (item) item.estado = 'AGUARDANDO_CONFIRMACAO';
  }

  async function devolverAFila(id: number, motivo: string) {
    await api.post(`/api/funcionario/minha-area/${id}/devolver`, { motivo });
    minhaArea.value = minhaArea.value.filter((i) => i.id !== id);
  }

  async function reportarProblema(id: number, motivo: string) {
    await api.post(`/api/funcionario/minha-area/${id}/reportar-problema`, { motivo });
  }

  async function finalizarAgendamento(id: number, resultado: ResultadoFinalizacao) {
    await api.post(`/api/funcionario/minha-area/${id}/finalizar`, { resultado });
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
