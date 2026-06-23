import axios from "axios";

/**
 * Aqui estou comunicando com uma API externa para resgatar os nomes dos municípios e estados.
 * https://servicodados.ibge.gov.br/api/docs/localidades
 * 
 * Essa API é mantida ativamente pelo IBGE, o que garante sua confiabilidade tanto nos dados
 * quanto na estabilidade dos servidores.
 * 
 * Como existem milhares de municípios ao todo, essa escolha cria uma dependência extra 
 * em troca de mais agilidade. No entanto, pelo caráter oficial da API, não vejo porque não usá-la.
 */
const apiMunicipiosEstados = axios.create({
    baseURL: "https://servicodados.ibge.gov.br/api/v1/",
    timeout: 5000 // ! se a requisição demorar demais, haverá erro...
});

type MunicipiosEstadosResponse = Array<{
    id: number
    nome: string
    // etc...
}>;

async function getEstados(): Promise<MunicipiosEstadosResponse> {
    const { data } = await apiMunicipiosEstados
                            .get<MunicipiosEstadosResponse>("localidades/estados")
                            .catch();

    return data;
}

async function getMunicipios(idEstado: number): Promise<MunicipiosEstadosResponse> {
    const { data } = await apiMunicipiosEstados
                            .get<MunicipiosEstadosResponse>(`localidades/estados/${idEstado}/municipios`)
                            .catch();


    return data;
}

export { getEstados, getMunicipios };