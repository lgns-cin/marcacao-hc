export type StatusPaciente = 'ALTA' | 'MÉDIA' | 'BAIXA';

export type AgendamentoItem = {
  id: number;
  nome: string;
  prontuario: string;
  numeroSolicitacao: string;
  exame: string;
  diasNaFila: number;
  status: StatusPaciente;
  unidadeSolicitante: string;
  dataRetorno: string;
  localizacao: string;
  regiao: string;
  idade: number;
  telefone: string;
};

export type FiltrosFila = {
  busca: string;
  regioes: string[];
  tiposExame: string[];
  municipio: string;
  faixaEtaria: string;
};

export type EstadoMinhaArea = 'EM_ANDAMENTO' | 'AGUARDANDO_CONFIRMACAO' | 'CONFIRMADO' | 'PROBLEMA_REPORTADO';

export const LABEL_ESTADO: Record<'CONFIRMADO' | 'PROBLEMA_REPORTADO', string> = {
  CONFIRMADO: 'Confirmado',
  PROBLEMA_REPORTADO: 'Encerrado',
};

export type MinhaAreaItem = AgendamentoItem & {
  estado: EstadoMinhaArea;
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
  //'Erro cadastral',
  'Outro',
];
