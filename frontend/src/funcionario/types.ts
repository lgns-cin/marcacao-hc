export type StatusPaciente = 'ALTA' | 'MÉDIA' | 'BAIXA';

export type AgendamentoItem = {
  id: number;
  nome: string;
  prontuario: string;
  solicitacao: string;
  exame: string;
  exameCodigo: string;
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

export type EstadoMinhaArea = 'EM_ANDAMENTO' | 'AGUARDANDO_CONFIRMACAO' | 'FINALIZADO';
export type ResultadoMinhaArea = 'CONFIRMADO' | 'PROBLEMA_REPORTADO';

export const LABEL_ESTADO: Record<'CONFIRMADO' | 'PROBLEMA_REPORTADO', string> = {
  CONFIRMADO: 'Confirmado',
  PROBLEMA_REPORTADO: 'Encerrado',
};

export type MinhaAreaItem = AgendamentoItem & {
  estado: EstadoMinhaArea;
  resultado: ResultadoMinhaArea;
};

export { MOTIVOS_DEVOLUCAO, MOTIVOS_PROBLEMA } from '../shared/constants';
