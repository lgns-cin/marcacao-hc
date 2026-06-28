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

export const TITULOS_KPIS: Record<string, string> = {
  media_cards_por_funcionario: 'Média de exames por funcionário',
  pct_problematicas: 'Exames problemáticos',
  pct_concluidas: 'Exames concluídos',
  tempo_medio_atendimento_dias: 'Tempo médio de marcação',
};

/**
 * O limite de exames retornados por requisições à API de fila de agendamentos
 */
export const LIMITE_AGENDAMENTOS = 12;


