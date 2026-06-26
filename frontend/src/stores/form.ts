import { defineStore } from "pinia";
import { ref } from "vue";


export const useFormStore = defineStore("form", () => {
    type Local = {
        estado: string
        cidade: string
    };

    type Exame = {
        codigo_exame: string
        nome_exame: string
        status_vaga: "DISPONÍVEL" | "INDISPONÍVEL" | "DUPLICADO"
    }

    const prontuario = ref<number>();
    const setProntuario = (val: number) => prontuario.value = val;

    const solicitacao = ref<number>();
    const setSolicitacao = (val: number) => solicitacao.value = val;

    const telefone = ref<number>();
    const setTelefone = (val: number) => telefone.value = val;

    const local = ref<Local>();
    const setLocal = (val: Local) => local.value = val;

    const exames = ref<Exame[]>([]);
    const setExames = (val: Exame[]) => exames.value = val;

    return {
        prontuario, setProntuario,
        solicitacao, setSolicitacao,
        telefone, setTelefone,
        local, setLocal,
        exames, setExames
    }
})