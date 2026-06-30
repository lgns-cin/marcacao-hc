<script setup lang="ts">
import { DocumentDuplicateIcon } from '@heroicons/vue/24/outline';
import TextWithIcon from './components/TextWithIcon.vue';
import { useRouter } from 'vue-router';
import * as zod from 'zod';
import { toTypedSchema } from '@vee-validate/zod';
import { useFormStore } from '../stores/form';
import FormView from './components/FormView.vue';
import { onMounted } from 'vue';
import api from '../services/api';
import { AxiosError } from 'axios';

const formStore = useFormStore();

onMounted(async () => {
    // Se o paciente não preencheu o campo do prontuário ainda,
    // force ele a preencher
    if (!formStore.prontuario) await toPrev();
})

const router = useRouter();
const toPrev = async () => await router.push("/prontuario");
const toNext = async () => await router.push("/contato");

const validationSchema = toTypedSchema(
    zod.object({
        solicitacao: zod.number({
            invalid_type_error: "Deve ser um número.",
            required_error: "Campo está vazio."
        }).int("Número deve ser inteiro.")
          .gte(10_000, "Número muito pequeno.")
          .lte(9_999_999, "Número muito grande.")
    })
);

const onSubmit = async (values: any, actions: any) => {
    const prontuario = formStore.prontuario;
    const solicitacao = values.solicitacao;

    await api.get(`/api/forms/validar_solicitacao/${prontuario}/${solicitacao}`)
            .then(async response => {
                const exames = response.data.exames;

                formStore.setExames(exames);
                formStore.setSolicitacao(solicitacao);
                await toNext();
            })
            .catch((error: AxiosError) => {
                let errorMessage = "";

                switch (error.status) {
                    case 404:
                        errorMessage = "Número não encontrado.";
                        break;
                    case 422:
                        errorMessage = "Esse número não é o da sua solicitação.";
                        break;
                    default:
                        errorMessage = "Ocorreu uma falha na validação interna.";
                        break;
                }

                actions.setErrors({ solicitacao: errorMessage });
            });
};

const items = [
    {
        name: 'solicitacao',
        type: 'number',
        placeholder: '1234567',
        default: formStore.solicitacao
    }
];

</script>

<template>
    <FormView
        img-src="exemplo_solicitacao"
        :items="items"
        :validation-schema="validationSchema"
        :on-prev-click="toPrev"
        :on-submit="onSubmit"
    >
        <template v-for="item in items" #[`text-${item.name}`]>
            <!-- texto pra solicitação -->
            <TextWithIcon v-if="item.name == 'solicitacao'">
                <DocumentDuplicateIcon #icon class="w-8 h-8 stroke-dark-blue-transparent" />
                <label :for="item.name">Número de <span class="underline">solicitação</span>:</label>
            </TextWithIcon>
        </template>
    </FormView>
</template>