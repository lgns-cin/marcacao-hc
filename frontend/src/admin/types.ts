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

export type SerieMotivoDevolucao = {
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

export type GraficoMotivosDevolucao = {
  id: string;
  titulo: string;
  subtitulo: string;
  tipo: 'barras_verticais';
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
  funcionarioAtribuido: string;
  problema_motivo?: string | null;
  problema_detalhes?: string | null;
};

export type AgendamentoGerenciamento = AgendamentoItem & {
  estado: EstadoMinhaArea;
  funcionarioAtribuido: string;
  problema_motivo?: string | null;
  problema_detalhes?: string | null;
};

export type AgendamentoRemovido = AgendamentoItem & {
  funcionarioAtribuido: string;
  problema_motivo: string;
  problema_detalhes?: string | null;
};

export type Funcionario = {
  username: string;
  nome: string;
};
