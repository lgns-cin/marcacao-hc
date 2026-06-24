import axios from 'axios';

const IBGE_API = 'https://servicodados.ibge.gov.br/api/v1/localidades';
const UF_PERNAMBUCO = 26;

export type Mesorregiao = {
  id: number;
  nome: string;
};

export type MunicipioIBGE = {
  id: number;
  nome: string;
  mesorregiao: Mesorregiao;
};

type MunicipioNivelado = {
  'municipio-id': number;
  'municipio-nome': string;
  'mesorregiao-id': number;
  'mesorregiao-nome': string;
};

const NOME_AMIGAVEL: Record<string, string> = {
  'Metropolitana de Recife': 'Região Metropolitana',
  'Agreste Pernambucano': 'Agreste',
  'Mata Pernambucana': 'Zona da Mata',
  'Sertão Pernambucano': 'Sertão',
  'São Francisco Pernambucano': 'São Francisco',
};

export const FORA_DO_ESTADO = 'Fora do Estado';

function nomeAmigavel(nomeIBGE: string): string {
  return NOME_AMIGAVEL[nomeIBGE] ?? nomeIBGE;
}

let cacheMunicipios: MunicipioIBGE[] | null = null;
let cacheMesorregioes: string[] | null = null;

export async function fetchMesorregioes(): Promise<string[]> {
  if (cacheMesorregioes) return cacheMesorregioes;

  const { data } = await axios.get<Mesorregiao[]>(
    `${IBGE_API}/estados/${UF_PERNAMBUCO}/mesorregioes`,
    { params: { orderBy: 'nome' } },
  );

  cacheMesorregioes = data.map((m) => nomeAmigavel(m.nome));
  return cacheMesorregioes;
}

export async function fetchMunicipios(): Promise<MunicipioIBGE[]> {
  if (cacheMunicipios) return cacheMunicipios;

  const { data } = await axios.get<MunicipioNivelado[]>(
    `${IBGE_API}/estados/${UF_PERNAMBUCO}/municipios`,
    { params: { orderBy: 'nome', view: 'nivelado' } },
  );

  cacheMunicipios = data.map((m) => ({
    id: m['municipio-id'],
    nome: m['municipio-nome'],
    mesorregiao: {
      id: m['mesorregiao-id'],
      nome: nomeAmigavel(m['mesorregiao-nome']),
    },
  }));

  return cacheMunicipios;
}

export async function derivarRegiao(localizacao: string): Promise<string> {
  const municipios = await fetchMunicipios();
  const normalizado = localizacao.trim().toLowerCase();
  const encontrado = municipios.find(
    (m) => m.nome.toLowerCase() === normalizado,
  );
  return encontrado ? encontrado.mesorregiao.nome : FORA_DO_ESTADO;
}

export async function derivarRegioes(
  itens: { localizacao: string }[],
): Promise<Map<string, string>> {
  const municipios = await fetchMunicipios();
  const mapa = new Map<string, string>();

  for (const municipio of municipios) {
    mapa.set(municipio.nome.toLowerCase(), municipio.mesorregiao.nome);
  }

  const resultado = new Map<string, string>();
  for (const item of itens) {
    const chave = item.localizacao.trim().toLowerCase();
    resultado.set(chave, mapa.get(chave) ?? FORA_DO_ESTADO);
  }

  return resultado;
}
