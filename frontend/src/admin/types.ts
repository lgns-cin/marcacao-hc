import type { AgendamentoItem, EstadoMinhaArea } from '../funcionario/types';

export type Kpi = {
  id: string;
  titulo: string;
  valor: string;
  formato: string;
};

export type SerieBarrasEtapas = {
  categoria: string;
  pendentes: number;
  emAgendamento: number;
  concluidos: number;
  total: number;
};

export type SerieMotivoReportarProblema = {
  motivo: string;
  quantidade: number;
};

export type GraficoBarrasEtapas = {
  id: string;
  titulo: string;
  subtitulo?: string;
  tipo: 'barras_horizontais';
  dados: SerieBarrasEtapas[];
};

export type GraficoBarrasVerticais = {
  id: string;
  titulo: string;
  subtitulo?: string;
  tipo: 'barras_verticais';
  dados: SerieMotivoReportarProblema[];
};

export type Grafico = GraficoBarrasEtapas | GraficoBarrasVerticais;

export type VisaoGeral = {
  kpis: Kpi[];
  graficos: Grafico[];
};

//export type SituacaoPendencia = 'BLOQUEADO' | 'PARADO';

export type PendenciaItem = AgendamentoItem & {
  //situacao: SituacaoPendencia;
  funcionarioAtribuido: string;
  motivo: string;
  detalhes?: string | null;
};

export type AgendamentoGerenciamento = AgendamentoItem & {
  estadoAtribuicao: EstadoMinhaArea;
  resultado: 'PROBLEMA_REPORTADO'| 'CONCLUIDO';
  funcionarioAtribuido: string;
  motivo?: string | null;
  detalhes?: string | null;
};

export type AgendamentoRemovido = AgendamentoItem & {
  funcionarioAtribuido: string;
  motivo: string;
  detalhes?: string | null;
};

export type Funcionario = {
  username: string;
  nome: string;
};
