<script setup lang="ts">
import { ArrowPathIcon, CheckCircleIcon, CheckIcon, XCircleIcon, XMarkIcon } from '@heroicons/vue/24/outline';
import { onMounted, ref } from 'vue';
import FormContainer from './components/FormContainer.vue';
import { useRouter } from 'vue-router';
import { useFormStore } from '../stores/form';
import { useUiStore } from '../stores/ui.js';
import ButtonWithIcon from './components/ButtonWithIcon.vue';

const formStore = useFormStore();
const uiStore = useUiStore();

const router = useRouter();
const toStart = async () => await router.push("/");
const toPrev = async () => await router.push("/contato");

const state = ref<"DISPONÍVEL" | "INDISPONÍVEL" | "DUPLICATA" | "SUBMETIDO">("DISPONÍVEL");

onMounted(async () => {
    // Se o paciente não preencheu nada anteriormente,
    // mande ele pro passo anterior
    if (!formStore.solicitacao || !formStore.prontuario || !formStore.local) await toPrev();

    uiStore.setLoading(true);

    // TODO: Fazer requisição à API
    // Resgata o nome e o código dos exames associados à solicitação no AGHU.
    // Retorna uma flag para cada exame indicando se ele tem ou não vaga no AGHU,
    // ou se o paciente já tem esse exame na fila.
    
    // hardcoded até finalizarem a API..
    exames.value = [
        {
            name: "Teste 1",
            code: "T1",
            flag: "DISPONÍVEL"
        },
        {
            name: "Teste 2",
            code: "T2",
            flag: "DISPONÍVEL"
        },
        {
            name: "Teste 3",
            code: "T3",
            flag: "DUPLICATA"
        }
    ];


    if (exames.value.every(v => v.flag == "DISPONÍVEL")) {
        // Se tudo já está disponível, faça o onSubmit automaticamente
        await onSubmit();
    }
    else if (exames.value.every(v => v.flag != "DISPONÍVEL")) {
        state.value = "INDISPONÍVEL";
    }
    else if (exames.value.every(v => v.flag == "DUPLICATA")) {
        state.value = "DUPLICATA";
    } 

    uiStore.setLoading(false);
});

const exames = ref<any[]>([]);

const onSubmit = async () => {
    const examesToDo = exames.value.filter(v => v.flag == "DISPONÍVEL").map(v => { v.name, v.code });

    // TODO: Fazer POST à API
    // Envia prontuário, solicitação, telefone, estado, cidade, e os exames a serem inseridos na fila

    state.value = "SUBMETIDO";
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
                    <div class="flex flex-row gap-2" v-if="exame.flag != 'DUPLICATA'">
                        <template v-if="exame.flag == 'DISPONÍVEL'">
                            <CheckCircleIcon #icon class="w-8 h-8 stroke-dark-green" />
                            <p class="text-dark-green">{{ exame.name }}</p>
                        </template>
                        <template v-else>
                            <XCircleIcon #icon class="w-8 h-8 stroke-light-red" />
                            <p class="text-light-red">{{ exame.name }}</p>
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
                <p class="text-center">Devido à falta de vagas, todos os exames da sua solicitação estão <span class="text-light-red underline">indisponíveis</span>.</p>
                <p class="text-center">Por favor, aguarde a liberação de vagas.</p>
            </template>

            <template v-else-if="state == 'DUPLICATA'">
                <div class="flex justify-center items-center">
                    <XMarkIcon #icon class="stroke-dark-blue w-32 h-32"/>
                </div>
                <h1 class="font-bold text-3xl text-center">Solicitação inválida.</h1>
                <p class="text-center">Essa solicitação já teve seus exames <span class="underline">marcados</span>.</p>
                <p class="text-center">Por favor, aguarde a liberação de vagas.</p>
            </template>

            <template v-else-if="state == 'SUBMETIDO'">
                <div class="flex justify-center items-center">
                    <CheckIcon #icon class="stroke-dark-blue w-32 h-32"/>
                </div>
                <h1 class="font-bold text-3xl text-center">Solicitação enviada!</h1>
                <template v-if="exames.filter(v => v.flag == 'DISPONÍVEL').length == exames.filter(v => v.flag != 'DUPLICATA').length">
                    <p class="text-center">Todos os exames relacionados à sua solicitação já foram enviados para marcação!</p>
                </template>
                <div class="text-center" v-else>
                    <p>Exames enviados:</p>
                    <ul>
                        <template v-for="exame in exames">
                            <p v-if="exame.flag == 'DISPONÍVEL'" class="font-semibold">
                                {{ exame.name }}
                            </p>
                        </template>
                    </ul>
                </div>
                <p class="text-center">Aguarde contato via <span class="underline">WhatsApp</span>.</p>
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