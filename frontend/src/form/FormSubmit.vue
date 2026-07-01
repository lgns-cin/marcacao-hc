<script setup lang="ts">
import { ArrowPathIcon, CheckCircleIcon, CheckIcon, XCircleIcon, XMarkIcon } from '@heroicons/vue/24/outline';
import { onMounted, ref } from 'vue';
import FormContainer from './components/FormContainer.vue';
import { useRouter } from 'vue-router';
import { useFormStore } from '../stores/form';
import { useUiStore } from '../stores/ui.js';
import ButtonWithIcon from './components/ButtonWithIcon.vue';
import api from '../services/api';

const formStore = useFormStore();
const uiStore = useUiStore();

const router = useRouter();
const toStart = async () => await router.push("/");
const toPrev = async () => await router.push("/contato");

const state = ref<"DISPONÍVEL" | "INDISPONÍVEL" | "DUPLICADO" | "SUBMETIDO" | "ERRO">("DISPONÍVEL");

onMounted(async () => {
    // Se o paciente não preencheu nada anteriormente,
    // mande ele pro passo anterior
    if (!formStore.solicitacao || !formStore.prontuario || !formStore.local) await toPrev();

    uiStore.setLoading(true);
    
    exames.value = formStore.exames;

    if (exames.value.every(v => v.status_vaga == "DUPLICADO") || exames.value.length == 0) {
        // tudo já tá na fila OU não tem nenhum exame novo.
        state.value = "DUPLICADO";
    }
    else if (exames.value.every(v => v.status_vaga != "INDISPONÍVEL")) {
        // tudo já está disponível (ou duplicado com pelo menos um disponível),
        // faça o onSubmit automaticamente (dos que estão disponíveis)
        await onSubmit();
    }
    else if (exames.value.every(v => v.status_vaga != "DISPONÍVEL")) {
        state.value = "INDISPONÍVEL";
    }

    uiStore.setLoading(false);
});

const exames = ref<any[]>([]);

const onSubmit = async () => {
    const examesToDo = exames.value.filter(v => v.status_vaga == "DISPONÍVEL").map(v => v.codigo_exame);
    await api.post(
        "/api/forms/enviar",
        {
            numero_prontuario: formStore.prontuario,
            numero_solicitacao: formStore.solicitacao,
            telefone: formStore.telefone?.toString(),
            estado: formStore.local?.estado,
            cidade: formStore.local?.cidade,
            exames: examesToDo
        }
    ).then(response => {
        if (response.data.status !== "sucesso") {
            throw new Error();
        }

        state.value = "SUBMETIDO";
    }).catch(() => {
        state.value = "ERRO";
    });
}

</script>

<template>
    <FormContainer>
        <template #contents>
            <template v-if="uiStore.isLoading">
                <div class="flex justify-center items-center">
                    <ArrowPathIcon #icon class="stroke-dark-blue w-32 h-32 animate-spin"/>
                </div>
                <h1 class="font-bold text-4xl text-center">Verificando dados...</h1>
                <p class="text-center">Por favor, aguarde.</p>
            </template>
            
            <template v-else-if="state == 'DISPONÍVEL'">
                <p>Sua <span class="underline">solicitação</span> se refere aos seguintes <span class="underline">exames</span>:</p>
                
                <template v-for="exame in exames">
                    <div
                        class="grid grid-cols-none grid-flow-col auto-cols-auto gap-2 justify-start text-start text-xl"
                        v-if="exame.status_vaga != 'DUPLICADO'"
                    >
                        <template v-if="exame.status_vaga == 'DISPONÍVEL'">
                            <CheckCircleIcon #icon class="w-8 h-8 stroke-dark-green" />
                            <p class="text-dark-green">{{ exame.nome_exame }}</p>
                        </template>
                        <template v-else>
                            <XCircleIcon #icon class="w-8 h-8 stroke-light-red" />
                            <p class="text-light-red">{{ exame.nome_exame }}</p>
                        </template>
                    </div>
                </template>

                <p>Devido à falta de vagas, alguns exames estão <span class="text-light-red underline">indisponíveis</span>.</p>
                <p>Deseja enviar o pedido de marcação apenas para os exames <span class="text-dark-green underline">disponíveis</span>?</p>

            </template>

            <template v-else-if="state == 'INDISPONÍVEL'">
                <div class="flex justify-center items-center">
                    <XMarkIcon #icon class="stroke-dark-blue w-32 h-32"/>
                </div>
                <h1 class="font-bold text-3xl text-center">Não será possível marcar agora.</h1>
                <div class="flex flex-col align-items justify-center-safe text-center" v-if="exames.filter(v => v.status_vaga == 'DUPLICADO').length > 0">
                    <p>Exames já enviados:</p>
                    <ul class="px-8 flex flex-col justify-center align-middle">
                        <template v-for="exame in exames">
                            <li 
                                class="grid grid-cols-none grid-flow-col auto-cols-auto gap-2 justify-start text-start text-xl"
                                v-if="exame.status_vaga == 'DUPLICADO'"
                            >
                                <CheckCircleIcon #icon class="w-8 h-8 stroke-dark-blue" />
                                <p class="font-semibold text-xl">{{ exame.nome_exame }}</p>
                            </li>
                        </template>
                    </ul>
                </div>
                <p class="text-center">{{ `Devido à falta de vagas, os ${exames.filter(v => v.status_vaga != 'DUPLICADO').length > 0 ? "outros" : ""} exames da sua solicitação estão ` }}<span class="text-light-red underline">indisponíveis</span>.</p>
                <p class="text-center">Por favor, aguarde a liberação de vagas ou procure a <span class="underline">Unidade Básica de Saúde</span> mais próxima.</p>
            </template>

            <template v-else-if="state == 'DUPLICADO'">
                <div class="flex justify-center items-center">
                    <XMarkIcon #icon class="stroke-dark-blue w-32 h-32"/>
                </div>
                <h1 class="font-bold text-3xl text-center">Solicitação inválida.</h1>
                <p class="text-center">Seus exames de imagem já foram <span class="underline">enviados</span>.</p>
                <p class="text-center">Por favor, aguarde contato via <span class="underline">WhatsApp</span>.</p>
            </template>

            <template v-else-if="state == 'SUBMETIDO'">
                <div class="flex justify-center items-center">
                    <CheckIcon #icon class="stroke-dark-blue w-32 h-32"/>
                </div>
                <h1 class="font-bold text-3xl text-center">Solicitação enviada!</h1>
                <template v-if="exames.filter(v => v.status_vaga == 'DISPONÍVEL').length == exames.filter(v => v.status_vaga != 'DUPLICADO').length">
                    <p class="text-center">Todos os exames relacionados à sua solicitação já foram enviados para marcação!</p>
                </template>
                <div class="text-center" v-else>
                    <p>Exames enviados:</p>
                    <ul>
                        <template v-for="exame in exames">
                            <p v-if="exame.status_vaga == 'DISPONÍVEL'" class="font-semibold">
                                {{ exame.nome_exame }}
                            </p>
                        </template>
                    </ul>
                </div>
                <p class="text-center">Aguarde contato via <span class="underline">WhatsApp</span>.</p>
            </template>

            <template v-else-if="state == 'ERRO'">
                <div class="flex justify-center items-center">
                    <XMarkIcon #icon class="stroke-dark-blue w-32 h-32"/>
                </div>
                <h1 class="font-bold text-3xl text-center">Um erro ocorreu.</h1>
                <p class="text-center">Não conseguimos enviar sua solicitação no momento.</p>
                <p class="text-center">Por favor, tente novamente mais tarde.</p>
            </template>
        </template>

        <template #buttons>
            <div class="flex flex-col gap-4" v-if="state == 'DISPONÍVEL'">
                <ButtonWithIcon @click="onSubmit">
                    <h2>Sim</h2>
                    <CheckIcon #icon class="stroke-2 stroke-white"/>
                </ButtonWithIcon>
                <ButtonWithIcon @click="toStart">
                    <h2>Não</h2>
                    <XMarkIcon #icon class="stroke-2 stroke-white"/>
                </ButtonWithIcon>
            </div>
            <ButtonWithIcon @click="toStart" v-else>
                Voltar
            </ButtonWithIcon>
        </template>
    </FormContainer>
</template>