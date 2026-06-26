export type CategoriaExame =
  | 'Tomografia'
  | 'Mamografia'
  | 'Raio-X'
  | 'Endoscopia'
  | 'Colonoscopia'
  | 'Ecocardiograma'
  | 'Ultrassonografia';

type ExameCatalogo = {
  codigo: string;
  nome: string;
  categoria: CategoriaExame;
};

export const CATALOGO_EXAMES: ExameCatalogo[] = [
  { codigo: 'TCABI', nome: 'Abdômen Inferior com Contraste', categoria: 'Tomografia' },
  { codigo: 'TCABC', nome: 'Abdômen Superior com Contraste', categoria: 'Tomografia' },
  { codigo: 'TCAVT', nome: 'Angiotomografia Venosa de Tórax', categoria: 'Tomografia' },
  { codigo: 'TCTX1', nome: 'Tórax', categoria: 'Tomografia' },

  { codigo: 'RXMM1', nome: 'Mamografia Bilateral', categoria: 'Mamografia' },

  { codigo: 'RXAB6', nome: 'Abdômen Simples (Decúbito Dorsal e Ortostática)', categoria: 'Raio-X' },
  { codigo: 'RXPAP', nome: 'RX Tórax (PA+Perfil)', categoria: 'Raio-X' },
  { codigo: 'RXTX1', nome: 'Tórax (AP) Leito', categoria: 'Raio-X' },
  { codigo: 'RXTX4', nome: 'Tórax (PA+P+OBL)', categoria: 'Raio-X' },

  { codigo: 'EDA', nome: 'Endoscopia Digestiva Alta', categoria: 'Endoscopia' },

  { codigo: 'CLN', nome: 'Colonoscopia', categoria: 'Colonoscopia' },

  { codigo: 'ECO', nome: 'Ecocardiograma', categoria: 'Ecocardiograma' },

  { codigo: 'USABT', nome: 'Abdômen Total', categoria: 'Ultrassonografia' },
  { codigo: 'USTDO', nome: 'Eco de Tireoide com Doppler a Cores', categoria: 'Ultrassonografia' },
  { codigo: 'USIDA', nome: 'USG Doppler do Membro Inferior Direito Arterial', categoria: 'Ultrassonografia' },
  { codigo: 'USIDV', nome: 'USG Doppler do Membro Inferior Direito Venoso', categoria: 'Ultrassonografia' },
  { codigo: 'USIEA', nome: 'USG Doppler do Membro Inferior Esquerdo Arterial', categoria: 'Ultrassonografia' },
  { codigo: 'USIEV', nome: 'USG Doppler do Membro Inferior Esquerdo Venoso', categoria: 'Ultrassonografia' },
  { codigo: 'USGOD', nome: 'USG Obstétrica com Dopplerfluxometria Colorida', categoria: 'Ultrassonografia' },
];

const mapaCodigoCategoria = new Map<string, CategoriaExame>(
  CATALOGO_EXAMES.map((e) => [e.codigo, e.categoria]),
);

const mapaCodigoNome = new Map<string, string>(
  CATALOGO_EXAMES.map((e) => [e.codigo, e.nome]),
);

export const CATEGORIAS_EXAME: CategoriaExame[] = [
  'Tomografia',
  'Mamografia',
  'Raio-X',
  'Endoscopia',
  'Colonoscopia',
  'Ecocardiograma',
  'Ultrassonografia',
];

export function categoriaDoCodigo(codigo: string): CategoriaExame | null {
  return mapaCodigoCategoria.get(codigo) ?? null;
}

export function nomeDoCodigo(codigo: string): string {
  return mapaCodigoNome.get(codigo) ?? codigo;
}
