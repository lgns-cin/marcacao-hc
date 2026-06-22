<script setup lang="ts">
import { IdentificationIcon } from '@heroicons/vue/24/outline';
import TextWithIcon from './components/TextWithIcon.vue';
import { useRouter } from 'vue-router';
import * as zod from 'zod';
import { toTypedSchema } from '@vee-validate/zod';
import { useFormStore } from '../stores/form';
import FormView from './components/FormView.vue';

const formStore = useFormStore();

const router = useRouter();
const toPrev = async () => await router.push("/");
const toNext = async () => await router.push("/solicitacao");

const validationSchema = toTypedSchema(
    zod.object({
        prontuario: zod.number({
            invalid_type_error: "Deve ser um número.",
            required_error: "Campo está vazio."
        }).int("Número deve ser inteiro.")
          .gte(10_000_000, "Número muito pequeno.")
          .lte(99_999_999, "Número muito grande.")
    })
);

const onSubmit = async (values: any, actions: any) => {
    const prontuario = values.prontuario;

    let exists = true;
    // TODO: Fazer requisição à API
    // Verifica se `prontuario` existe no AGHU

    if (!exists) {
        actions.setErrors({ prontuario: "Número não encontrado." });
        return;
    }

    formStore.setProntuario(prontuario);
    await toNext();
};

const items = [
    {
        name: 'prontuario',
        type: 'number',
        placeholder: '1234567/8',
        default: formStore.prontuario
    }
];

</script>

<template>
    <FormView
        img-src="exemplo_prontuario"
        :items="items"
        :validation-schema="validationSchema"
        :on-prev-click="toPrev"
        :on-submit="onSubmit"
    >
        <template v-for="item in items" #[`text-${item.name}`]>
            <!-- texto pro prontuário -->
            <TextWithIcon v-if="item.name == 'prontuario'">
                <IdentificationIcon #icon class="w-8 h-8 stroke-dark-blue-transparent" />
                <label :for="item.name">Número de <span class="underline">prontuário</span>:</label>
            </TextWithIcon>
        </template>
    </FormView>
</template>