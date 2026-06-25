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
          .gte(1_000_000, "Número muito pequeno.")
          .lte(9_999_999, "Número muito grande.")
    })
);

const onSubmit = async (values: any, actions: any) => {
    const prontuario = formStore.prontuario;
    const solicitacao = values.solicitacao;

    let exists = true, mismatched = false;
    let exames = undefined;

    try {
        const { status, data } = await api.get(`forms/validar_solicitacao/${prontuario}/${solicitacao}`);
        exists = status == 200;
        mismatched = status == 422;
        exames = data.exames;
    } catch {
        actions.setErrors({ prontuario: "Ocorreu uma falha na validação interna." });
        return;
    }

    if (!exists || exames === undefined) {
        actions.setErrors({ solicitacao: "Número não encontrado." });
        return;
    }

    if (mismatched) {
        actions.setErrors({ solicitacao: "Esse número não é o da sua solicitação." });
        return;
    }

    formStore.setExames(exames); // exames é truthy aqui
    formStore.setSolicitacao(solicitacao);
    await toNext();
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