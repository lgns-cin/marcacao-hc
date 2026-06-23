<script setup lang="ts">
import { ArrowRightIcon } from '@heroicons/vue/24/outline';
import { computed } from 'vue';
import FormContainer from './components/FormContainer.vue';
import ButtonWithIcon from './components/ButtonWithIcon.vue';
import { useRouter } from 'vue-router';

const greeting = computed(() => {
    const hours = new Date().getHours();
    
    if (hours >= 5 && hours < 12) return "Bom dia!"
    else if (hours >= 12 && hours < 18) return "Boa tarde!"
    else return "Boa noite!"
});

const router = useRouter();
const toNext = async () => await router.push("/prontuario");

</script>

<template>
    <img src="../../public/hc_banner_branco.png" class="max-w-[328px] rounded-xl" />

    <FormContainer>
        <template #contents>
            <h1 class="font-bold text-4xl text-center">{{ greeting }}</h1>
            <p>Este é o <span class="underline">formulário de marcação de exames</span> do Hospital das Clínicas UFPE.</p>
            <p>Antes de começar, garanta que sua <span class="underline">solicitação</span> está em mãos.</p>
        </template>

        <template #buttons>
            <ButtonWithIcon @click="toNext">
                <h2>Começar</h2>
                <ArrowRightIcon #icon class="stroke-2 stroke-white"/>
            </ButtonWithIcon>
        </template>
    </FormContainer>
</template>