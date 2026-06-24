import type { AgendamentoItem, FiltrosFila } from '../../funcionario/types';

export function filtrarAgendamentos<T extends AgendamentoItem>(lista: T[], filtros: FiltrosFila): T[] {
  const busca = filtros.busca.trim().toLowerCase();
  const municipio = filtros.municipio.trim().toLowerCase();

  return lista.filter((item) => {
    const correspondeBusca =
      !busca ||
      item.nome.toLowerCase().includes(busca) ||
      item.prontuario.includes(busca);

    const correspondeRegiao =
      filtros.regioes.length === 0 ||
      filtros.regioes.includes(item.regiao);

    const correspondeExame =
      filtros.tiposExame.length === 0 ||
      item.exames.some((exame) => filtros.tiposExame.includes(exame));

    const correspondeMunicipio =
      !municipio || item.localizacao.toLowerCase().includes(municipio);

    const correspondeFaixaEtaria =
      filtros.faixaEtaria === 'Todas' ||
      (filtros.faixaEtaria === '0-17' && item.idade <= 17) ||
      (filtros.faixaEtaria === '18-59' && item.idade >= 18 && item.idade <= 59) ||
      (filtros.faixaEtaria === '60+' && item.idade >= 60);

    return (
      correspondeBusca &&
      correspondeRegiao &&
      correspondeExame &&
      correspondeMunicipio &&
      correspondeFaixaEtaria
    );
  });
}

export const FILTROS_VAZIOS: FiltrosFila = {
  busca: '',
  regioes: [],
  tiposExame: [],
  municipio: '',
  faixaEtaria: 'Todas',
};
