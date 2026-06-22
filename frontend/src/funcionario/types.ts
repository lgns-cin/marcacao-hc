export type StatusPaciente = 'ALTA';

export type AgendamentoItem = {
  id: number;
  nome: string;
  prontuario: string;
  exames: string[];
  diasNaFila: number;
  status: StatusPaciente;
  unidadeExecutora: string;
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
