import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { AgendamentoItem, FiltrosFila, MinhaAreaItem, ResultadoFinalizacao } from '../funcionario/types';
import { filtrarAgendamentos, FILTROS_VAZIOS } from '../shared/utils/filtrarAgendamentos';
import { derivarRegiao, fetchMesorregioes, fetchMunicipios, FORA_DO_ESTADO } from '../shared/services/ibge';
import type { MunicipioIBGE } from '../shared/services/ibge';

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

  // Dados mock (sem regiao — será derivada via IBGE)
  const AGENDAMENTOS_MOCK: Omit<AgendamentoItem, 'regiao'>[] = [
    {
      id: 1,
      nome: 'Maria das Graças Oliveira',
      prontuario: '000123456',
      exames: ['Tomografia', 'Ressonância'],
      diasNaFila: 42,
      status: 'ALTA',
      unidadeExecutora: 'Hospital das Clínicas - Recife',
      unidadeSolicitante: 'UBS Centro - Caruaru',
      dataRetorno: '15/07/2026',
      localizacao: 'Caruaru',
      idade: 67,
    },
    {
      id: 2,
      nome: 'João Pedro Ferreira Silva',
      prontuario: '000987654',
      exames: ['Endoscopia'],
      diasNaFila: 18,
      status: 'MÉDIA',
      unidadeExecutora: 'Hospital Universitário Oswaldo Cruz',
      unidadeSolicitante: 'UBS Boa Viagem - Recife',
      dataRetorno: '20/07/2026',
      localizacao: 'Recife',
      idade: 45,
    },
    {
      id: 3,
      nome: 'Ana Beatriz Santos',
      prontuario: '000543210',
      exames: ['Mamografia', 'Ultrassonografia'],
      diasNaFila: 7,
      status: 'BAIXA',
      unidadeExecutora: 'Instituto de Medicina Integral - IMIP',
      unidadeSolicitante: 'UBS Olinda Norte',
      dataRetorno: '10/08/2026',
      localizacao: 'Olinda',
      idade: 52,
    },
    {
      id: 4,
      nome: 'Carlos Eduardo Nascimento',
      prontuario: '000112233',
      exames: ['Colonoscopia'],
      diasNaFila: 31,
      status: 'ALTA',
      unidadeExecutora: 'Hospital Agamenon Magalhães',
      unidadeSolicitante: 'UBS Garanhuns Centro',
      dataRetorno: '18/07/2026',
      localizacao: 'Garanhuns',
      idade: 63,
    },
    {
      id: 5,
      nome: 'Fernanda Lima Rodrigues',
      prontuario: '000334455',
      exames: ['Ressonância'],
      diasNaFila: 5,
      status: 'BAIXA',
      unidadeExecutora: 'Hospital da Restauração',
      unidadeSolicitante: 'UBS Petrolina Centro',
      dataRetorno: '25/08/2026',
      localizacao: 'Petrolina',
      idade: 29,
    },
    {
      id: 6,
      nome: 'Roberto Alves de Souza',
      prontuario: '000667788',
      exames: ['Espirometria', 'Tomografia'],
      diasNaFila: 55,
      status: 'ALTA',
      unidadeExecutora: 'Hospital das Clínicas - Recife',
      unidadeSolicitante: 'UBS Palmares',
      dataRetorno: '12/07/2026',
      localizacao: 'Palmares',
      idade: 71,
    },
    {
      id: 7,
      nome: 'Luciana Moura Costa',
      prontuario: '000889900',
      exames: ['Ultrassonografia'],
      diasNaFila: 12,
      status: 'MÉDIA',
      unidadeExecutora: 'Hospital Dom Malan',
      unidadeSolicitante: 'UBS Arcoverde',
      dataRetorno: '01/08/2026',
      localizacao: 'Arcoverde',
      idade: 38,
    },
    {
      id: 8,
      nome: 'Antônio Pereira da Cruz',
      prontuario: '000001122',
      exames: ['Endoscopia', 'Colonoscopia'],
      diasNaFila: 24,
      status: 'MÉDIA',
      unidadeExecutora: 'Hospital Universitário Oswaldo Cruz',
      unidadeSolicitante: 'UBS Goiana',
      dataRetorno: '30/07/2026',
      localizacao: 'Goiana',
      idade: 55,
    },
  ];

  const MINHA_AREA_MOCK: Omit<MinhaAreaItem, 'regiao'>[] = [
    {
      id: 101,
      nome: 'Patrícia Vieira Mendes',
      prontuario: '000777888',
      exames: ['Tomografia'],
      diasNaFila: 20,
      status: 'ALTA',
      unidadeExecutora: 'Hospital das Clínicas - Recife',
      unidadeSolicitante: 'UBS Jaboatão',
      dataRetorno: '22/07/2026',
      localizacao: 'Jaboatão dos Guararapes',
      idade: 58,
      estado: 'EM_ANDAMENTO',
    },
    {
      id: 102,
      nome: 'Marcos Antônio Lira',
      prontuario: '000444555',
      exames: ['Ressonância', 'Ultrassonografia'],
      diasNaFila: 35,
      status: 'ALTA',
      unidadeExecutora: 'Hospital Agamenon Magalhães',
      unidadeSolicitante: 'UBS Caruaru Sul',
      dataRetorno: '14/07/2026',
      localizacao: 'Caruaru',
      idade: 72,
      estado: 'AGUARDANDO_CONFIRMACAO',
    },
    {
      id: 103,
      nome: 'Simone Cavalcanti',
      prontuario: '000222333',
      exames: ['Mamografia'],
      diasNaFila: 9,
      status: 'BAIXA',
      unidadeExecutora: 'Instituto de Medicina Integral - IMIP',
      unidadeSolicitante: 'UBS Paulista',
      dataRetorno: '05/08/2026',
      localizacao: 'Paulista',
      idade: 48,
      estado: 'FINALIZADO',
      resultado: 'CONFIRMADO',
    },
    {
      id: 104,
      nome: 'Diego Henrique Barbosa',
      prontuario: '000999000',
      exames: ['Espirometria'],
      diasNaFila: 16,
      status: 'MÉDIA',
      unidadeExecutora: 'Hospital da Restauração',
      unidadeSolicitante: 'UBS Afogados da Ingazeira',
      dataRetorno: '28/07/2026',
      localizacao: 'Afogados da Ingazeira',
      idade: 33,
      estado: 'EM_ANDAMENTO',
    },
  ];

  async function preencherRegioes<T extends { localizacao: string }>(
    itens: Omit<T, 'regiao'>[],
  ): Promise<(T & { regiao: string })[]> {
    return Promise.all(
      itens.map(async (item) => ({
        ...item,
        regiao: await derivarRegiao(item.localizacao),
      })) as Promise<T & { regiao: string }>[],
    );
  }

  async function carregarDadosIBGE() {
    const [mesorregioes, municipios] = await Promise.all([
      fetchMesorregioes(),
      fetchMunicipios(),
    ]);
    regioes.value = [...mesorregioes, FORA_DO_ESTADO];
    municipiosIBGE.value = municipios;
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
