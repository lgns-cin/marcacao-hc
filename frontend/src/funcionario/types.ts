export type StatusPaciente = 'ALTA' | 'MÉDIA' | 'BAIXA';

export type AgendamentoItem = {
  id: number;
  nome: string;
  prontuario: string;
  exames: string[];
  diasNaFila: number;
  status: StatusPaciente;
  unidadeSolicitante: string;
  dataRetorno: string;
  localizacao: string;
  regiao: string;
  idade: number;
};

export type FiltrosFila = {
  busca: string;
  regioes: string[];
  tiposExame: string[];
  municipio: string;
  faixaEtaria: string;
};

export type EstadoMinhaArea = 'EM_ANDAMENTO' | 'AGUARDANDO_CONFIRMACAO' | 'FINALIZADO';

export type ResultadoFinalizacao = 'CONFIRMADO' | 'CANCELADO';

export type MinhaAreaItem = AgendamentoItem & {
  estado: EstadoMinhaArea;
  resultado?: ResultadoFinalizacao;
};

export const MOTIVOS_DEVOLUCAO = [
  'Exame selecionado por engano.',
  'Solicitação atribuída incorretamente pela administração.',
  'Outro',
];

export const MOTIVOS_PROBLEMA = [
  'Paciente não respondeu',
  'Dados inconsistentes',
  'Duplicidade',
  'Erro cadastral',
  'Outro',
];
