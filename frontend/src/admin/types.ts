import type { AgendamentoItem, EstadoMinhaArea } from '../funcionario/types';

export type CategoriaIndicador = 'principal' | 'extra';

export type Kpi = {
  id: string;
  label: string;
  valor: number;
  sufixo?: string;
  tendencia?: number;
  categoria: CategoriaIndicador;
  periodo?: string;
};

// Recorte temporal das KPIs da Central. Enviado como parâmetro temporal à API
// (Leonardo adicionou o parâmetro nas rotas existentes, sem mudar as rotas).
export type PeriodoVisaoGeral = 'mes_atual' | 'ultimos_3_meses' | 'ultimos_6_meses' | 'ultimo_ano';

export const PERIODOS_VISAO_GERAL: { id: PeriodoVisaoGeral; label: string; sufixo: string }[] = [
  { id: 'mes_atual', label: 'Mês atual', sufixo: 'no mês atual' },
  { id: 'ultimos_3_meses', label: 'Últimos 3 meses', sufixo: 'nos últimos 3 meses' },
  { id: 'ultimos_6_meses', label: 'Últimos 6 meses', sufixo: 'nos últimos 6 meses' },
  { id: 'ultimo_ano', label: 'Último ano', sufixo: 'no último ano' },
];

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

//export type SituacaoPendencia = 'BLOQUEADO' | 'PARADO';

export type PendenciaItem = AgendamentoItem & {
  //situacao: SituacaoPendencia;
  responsavel: string;
  problema_motivo?: string | null;
  problema_detalhes?: string | null;
};

export type AgendamentoGerenciamento = AgendamentoItem & {
  estado: EstadoMinhaArea;
  responsavel: string;
  problema_motivo?: string | null;
  problema_detalhes?: string | null;
};

export type AgendamentoRemovido = AgendamentoItem & {
  responsavel: string;
  problema_motivo: string;
  problema_detalhes?: string | null;
};

export type Funcionario = {
  username: string;
  nome: string;
};

export const PREFERENCIAS_VISAO_GERAL_KEY = 'admin-visao-geral-preferencias';
