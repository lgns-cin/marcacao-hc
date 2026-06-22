import type { AgendamentoItem, EstadoMinhaArea, ResultadoFinalizacao } from '../funcionario/types';

export type CategoriaIndicador = 'principal' | 'extra';

export type Kpi = {
  id: string;
  label: string;
  valor: number;
  sufixo?: string;
  tendencia?: number;
  categoria: CategoriaIndicador;
};

export type SerieBarrasEtapas = {
  categoria: string;
  agendados: number;
  emAndamento: number;
  aAgendar: number;
};

export type SerieMotivoDevolucao = {
  motivo: string;
  quantidade: number;
};

export type GraficoBarrasEtapas = {
  id: string;
  titulo: string;
  subtitulo: string;
  tipo: 'barras_horizontais';
  categoria: CategoriaIndicador;
  dados: SerieBarrasEtapas[];
};

export type GraficoMotivosDevolucao = {
  id: string;
  titulo: string;
  subtitulo: string;
  tipo: 'barras_verticais';
  categoria: CategoriaIndicador;
  dados: SerieMotivoDevolucao[];
};

export type Grafico = GraficoBarrasEtapas | GraficoMotivosDevolucao;

export type VisaoGeral = {
  kpis: Kpi[];
  graficos: Grafico[];
};

export type SituacaoPendencia = 'BLOQUEADO' | 'PARADO';

export type PendenciaItem = AgendamentoItem & {
  situacao: SituacaoPendencia;
  responsavel: string;
  problema_motivo?: string | null;
  problema_detalhes?: string | null;
};

export type AgendamentoGerenciamento = AgendamentoItem & {
  estado: EstadoMinhaArea;
  resultado?: ResultadoFinalizacao;
  responsavel: string;
};

export type Funcionario = {
  username: string;
  nome: string;
};

export const PREFERENCIAS_VISAO_GERAL_KEY = 'admin-visao-geral-preferencias';
