import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';
import type { AgendamentoItem, FiltrosFila } from '../funcionario/types';

const FILTROS_VAZIOS: FiltrosFila = {
  busca: '',
  regioes: [],
  tiposExame: [],
  municipio: '',
  faixaEtaria: 'Todas',
};

export const useFuncionarioStore = defineStore('funcionario', () => {
  // state
  const agendamentos = ref<AgendamentoItem[]>([]);
  const isLoading = ref(false);
  const filtros = ref<FiltrosFila>({ ...FILTROS_VAZIOS });

  // computed
  const totalAgendamentos = computed(() => agendamentos.value.length);

  const agendamentosFiltrados = computed(() => {
    const busca = filtros.value.busca.trim().toLowerCase();
    const municipio = filtros.value.municipio.trim().toLowerCase();

    return agendamentos.value.filter((item) => {
      const correspondeBusca =
        !busca ||
        item.nome.toLowerCase().includes(busca) ||
        item.prontuario.includes(busca);

      const correspondeRegiao =
        filtros.value.regioes.length === 0 ||
        filtros.value.regioes.includes(item.regiao);

      const correspondeExame =
        filtros.value.tiposExame.length === 0 ||
        item.exames.some((exame) => filtros.value.tiposExame.includes(exame));

      const correspondeMunicipio =
        !municipio || item.localizacao.toLowerCase().includes(municipio);

      const correspondeFaixaEtaria =
        filtros.value.faixaEtaria === 'Todas' ||
        (filtros.value.faixaEtaria === '0-17' && item.idade <= 17) ||
        (filtros.value.faixaEtaria === '18-59' && item.idade >= 18 && item.idade <= 59) ||
        (filtros.value.faixaEtaria === '60+' && item.idade >= 60);

      return (
        correspondeBusca &&
        correspondeRegiao &&
        correspondeExame &&
        correspondeMunicipio &&
        correspondeFaixaEtaria
      );
    });
  });

  // actions
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
  };
});
