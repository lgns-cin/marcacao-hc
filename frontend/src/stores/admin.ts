import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { AgendamentoItem, FiltrosFila } from '../funcionario/types';
import { filtrarAgendamentos, FILTROS_VAZIOS } from '../shared/utils/filtrarAgendamentos';
import type { AgendamentoGerenciamento, Funcionario, PendenciaItem, VisaoGeral } from '../admin/types';
import { PREFERENCIAS_VISAO_GERAL_KEY } from '../admin/types';

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
  // ==========================================
  // ESTADOS (STATE)
  // ==========================================
  const visaoGeral = ref<VisaoGeral | null>(null);
  const isLoadingVisaoGeral = ref(false);
  const indicadoresVisiveis = ref<string[] | null>(carregarPreferenciasIniciais());

  const pendencias = ref<PendenciaItem[]>([]);
  const isLoadingPendencias = ref(false);
  const filtrosPendencias = ref<FiltrosFila>({ ...FILTROS_VAZIOS });

  const agendamentosEmAndamento = ref<AgendamentoGerenciamento[]>([]);
  const agendamentosConcluidos = ref<AgendamentoGerenciamento[]>([]);
  const isLoadingAgendamentos = ref(false);
  const filtrosAgendamentos = ref<FiltrosFila>({ ...FILTROS_VAZIOS });

  const fila = ref<AgendamentoItem[]>([]);
  const isLoadingFila = ref(false);
  const filtrosFila = ref<FiltrosFila>({ ...FILTROS_VAZIOS });

  const funcionarios = ref<Funcionario[]>([]);

  // Colocamos aqui os dados hardecoded 
  const MOCK_FUNCIONARIOS: Funcionario[] = [
    { username: 'fabiana.lopes', nome: 'Fabiana Lopes' },
    { username: 'joao.silva', nome: 'João Silva' },
    { username: 'carla.mendes', nome: 'Carla Mendes' },
    { username: 'ricardo.alves', nome: 'Ricardo Alves' },
  ];

  const MOCK_VISAO_GERAL: VisaoGeral = {
    kpis: [
      { id: 'media_card_funcionario', label: 'Média de Card por Funcionário', valor: 3.5, categoria: 'principal' },
      { id: 'media_exames_agendados', label: 'Média de Exames Agendados', valor: 4.0, tendencia: 5, categoria: 'principal' },
      { id: 'quantidade_funcionarios', label: 'Quantidade de Funcionários', valor: 4, categoria: 'principal' },
      { id: 'total_cards', label: 'Total de Cards', valor: 14, categoria: 'principal' },
      { id: 'tempo_medio_atendimento', label: 'Tempo médio de atendimento', valor: 3.8, sufixo: 'dias', categoria: 'extra' },
      { id: 'solicitacoes_atendidas', label: 'Solicitações atendidas', valor: 367, categoria: 'extra' },
      { id: 'pacientes_devolvidos_fila', label: 'Pacientes devolvidos à fila', valor: 55, tendencia: 15, categoria: 'extra' },
    ],
    graficos: [
      {
        id: 'por_tipo_exame',
        titulo: 'Por tipo de exame',
        subtitulo: 'Acompanhe a distribuição dos exames por tipo',
        tipo: 'barras_horizontais',
        categoria: 'principal',
        dados: [
          { categoria: 'Colonoscopia', agendados: 8, emAndamento: 2, aAgendar: 0 },
          { categoria: 'Endoscopia', agendados: 4, emAndamento: 6, aAgendar: 1 },
          { categoria: 'Ultrassonografia', agendados: 3, emAndamento: 0, aAgendar: 2 },
          { categoria: 'Mamografia', agendados: 1, emAndamento: 1, aAgendar: 0 },
          { categoria: 'Espirometria', agendados: 0, emAndamento: 1, aAgendar: 0 },
        ],
      },
      {
        id: 'por_localidade',
        titulo: 'Por localidade',
        subtitulo: 'Entenda como os exames se distribuem por localidade',
        tipo: 'barras_horizontais',
        categoria: 'principal',
        dados: [
          { categoria: 'Olinda', agendados: 0, emAndamento: 8, aAgendar: 2 },
          { categoria: 'Recife', agendados: 4, emAndamento: 0, aAgendar: 5 },
          { categoria: 'Jaboatão dos Guararapes', agendados: 0, emAndamento: 2, aAgendar: 1 },
          { categoria: 'Caruaru', agendados: 1, emAndamento: 1, aAgendar: 0 },
          { categoria: 'Petrolina', agendados: 1, emAndamento: 0, aAgendar: 0 },
        ],
      },
      {
        id: 'motivos_devolucao',
        titulo: 'Pacientes devolvidos à fila',
        subtitulo: 'Quantitativo por motivo de devolução',
        tipo: 'barras_verticais',
        categoria: 'extra',
        dados: [
          { motivo: 'Falha em contato com o paciente', quantidade: 99 },
          { motivo: 'Pendência Operacional', quantidade: 74 },
          { motivo: 'Reagendamento', quantidade: 95 },
          { motivo: 'Outros', quantidade: 24 },
        ],
      },
    ],
  };

  const MOCK_PENDENCIAS: PendenciaItem[] = [
    {
      id: 201,
      nome: 'Everaldo Albuquerque Cavalcanti',
      prontuario: '000555444',
      exames: ['Tomografia'],
      diasNaFila: 15,
      status: 'ALTA',
      unidadeExecutora: 'Hospital da Restauração',
      unidadeSolicitante: 'UBS Centro',
      dataRetorno: '10/07/2026',
      localizacao: 'Olinda',
      regiao: 'Região Metropolitana',
      idade: 62,
      problema_motivo: 'Erro cadastral no prontuário do paciente',
      problema_detalhes: 'Erro cadastral no prontuário do paciente',
      responsavel: 'fabiana.lopes',
      situacao: 'BLOQUEADO',
    }
  ];

  const MOCK_GERENCIAMENTO_ANDAMENTO: AgendamentoGerenciamento[] = [
    {
      id: 301,
      nome: 'Gisela Maria Santos',
      prontuario: '000333222',
      exames: ['Ressonância'],
      diasNaFila: 22,
      status: 'MÉDIA',
      unidadeExecutora: 'Hospital das Clínicas - Recife',
      unidadeSolicitante: 'UBS Boa Vista',
      dataRetorno: '05/08/2026',
      localizacao: 'Recife',
      regiao: 'Região Metropolitana',
      idade: 41,
      estado: 'EM_ANDAMENTO',
      responsavel: 'joao.silva',
    }
  ];

  const MOCK_GERENCIAMENTO_CONCLUIDO: AgendamentoGerenciamento[] = [
    {
      id: 302,
      nome: 'Severino Ramos da Silva',
      prontuario: '000111999',
      exames: ['Endoscopia'],
      diasNaFila: 45,
      status: 'ALTA',
      unidadeExecutora: 'Hospital Universitário Oswaldo Cruz',
      unidadeSolicitante: 'UBS Centro - Caruaru',
      dataRetorno: '12/07/2026',
      localizacao: 'Caruaru',
      regiao: 'Agreste',
      idade: 69,
      estado: 'FINALIZADO',
      resultado: 'CONFIRMADO',
      responsavel: 'carla.mendes',
    }
  ];

  const MOCK_FILA_ADMIN: AgendamentoItem[] = [
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
      regiao: 'Agreste',
      idade: 67,
    }
  ];

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
  const filaFiltrada = computed(() => filtrarAgendamentos(fila.value, filtrosFila.value));

  //Ações
  
  // Visão Geral
  async function fetchVisaoGeral(opcoes: { silencioso?: boolean } = {}) {
    if (!opcoes.silencioso) isLoadingVisaoGeral.value = true;
    await new Promise((r) => setTimeout(r, 300));
    visaoGeral.value = MOCK_VISAO_GERAL;
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
    agendamentosEmAndamento.value = MOCK_GERENCIAMENTO_ANDAMENTO;
    agendamentosConcluidos.value = MOCK_GERENCIAMENTO_CONCLUIDO;
    if (!opcoes.silencioso) isLoadingAgendamentos.value = false;
  }

  async function reatribuirAgendamento(id: number, funcionarioUsername: string) {
    await new Promise((r) => setTimeout(r, 200));
    // Procura localmente e altera o funcionário responsável (Mock)
    const item = agendamentosEmAndamento.value.find((i) => i.id === id);
    if (item) {
      item.responsavel = funcionarioUsername;
    }
  }

  async function devolverAFilaAdmin(id: number, _motivo: string) {
    await new Promise((r) => setTimeout(r, 200));
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