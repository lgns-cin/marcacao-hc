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

  // o const {data} já desestrutura a resposta da promise e pega só o data
  //obs: esse view:nivelado já deixa o dado no formato que queremos
  // pq caso o ibge não ofereça essa view, teríamos que fazer um segundo
  // endpoint para obter as mesorregiões e depois montar o objeto na mão
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
// para não ficar chamando fetchMunicipios() em loop, geramos um mapa
// desse mapeamento uma vez só
// com map não precisamos ordenar, só faz a busca linear no hash
export async function derivarRegioes(
  itens: { localizacao: string }[], // precisa ter a propriedade localizacao pra poder chamar esse método
): Promise<Map<string, string>> {// 'caruaru' --> 'Agreste'
  const municipios = await fetchMunicipios();
  const mapa = new Map<string, string>();

  // catalogo de municipios
  for (const municipio of municipios) {
    mapa.set(municipio.nome.toLowerCase(), municipio.mesorregiao.nome);
  }

  // agora montamos o resultado
  const resultado = new Map<string, string>();
  for (const item of itens) {
    const chave = item.localizacao.trim().toLowerCase();
    resultado.set(chave, mapa.get(chave) ?? FORA_DO_ESTADO);
  }

  return resultado;
}
