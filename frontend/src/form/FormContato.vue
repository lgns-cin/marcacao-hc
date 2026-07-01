<script setup lang="ts">
import { HomeIcon, PhoneIcon } from '@heroicons/vue/24/outline';
import TextWithIcon from './components/TextWithIcon.vue';
import { useRouter } from 'vue-router';
import * as zod from 'zod';
import { toTypedSchema } from '@vee-validate/zod';
import { useFormStore } from '../stores/form';
import FormView from './components/FormView.vue';
import { onMounted, ref } from 'vue';
import { ErrorMessage, Field } from 'vee-validate';
import { getEstados, getMunicipios } from '../services/ibge_api.js';

const formStore = useFormStore();

onMounted(async () => {
    // Se o paciente não preencheu a solicitação ou prontuário,
    // mande ele pro passo anterior
    if (!formStore.solicitacao || !formStore.prontuario) await toPrev();
})

const router = useRouter();
const toPrev = async () => await router.push("/solicitacao");
const toNext = async () => await router.push("/submit");

const validationSchema = toTypedSchema(
    zod.object({
        telefone: zod.number({
            invalid_type_error: "Deve ser um número.",
            required_error: "Campo está vazio."
        }).int("Número deve ser inteiro.")
          .gte(10_0_0000_0000, "Número muito pequeno.")
          .lte(99_9_9999_9999, "Número muito grande.")
          .refine((tel: number) => tel.toString().charAt(2) == '9', "O terceiro dígito deve ser 9."),

        estado: zod.string({
            required_error: "Campo está vazio."
        }).refine(
              (_: string) => estados.value.length != 0,
              "Não pudemos recuperar os estados. Tente novamente depois."
          )
          .refine(
              (estado: string) => estados.value.length > 0 && estados.value.includes(estado), 
              "Não é um estado."
          ),

        cidade: zod.string({
            required_error: "Campo está vazio."
        }).refine(
              (_: string) => local.value.estado && estados.value.length > 0 && estados.value.includes(local.value.estado),
              "O estado não foi preenchido corretamente."
          )
          .refine(
              (_: string) => cidades.value.length != 0,
              "Não pudemos recuperar os municípios. Tente novamente depois."
          )
          .refine(
              (cidade: string) => cidades.value.length > 0 && cidades.value.includes(cidade), 
              "Não é um município desse estado."
          )
    })
);

const onSubmit = async (values: any, _: any) => {
    formStore.setTelefone(values.telefone);
    formStore.setLocal({
        estado: values.estado,
        cidade: values.cidade
    });

    await toNext();
}

const items = [
    {
        name: 'telefone',
        type: 'number',
        placeholder: '(11) 9 1234-5678',
        default: formStore.telefone
    }
];

const local = ref<{
    estado?: string
    cidade?: string
}>({});

const estados = ref<string[]>([]);
const idsEstado = ref<number[]>([]);

onMounted(async () => {
    const arr = await getEstados();
    estados.value = arr.map(pair => pair.nome);
    idsEstado.value = arr.map(pair => pair.id);

    local.value.estado = formStore.local?.estado;
    if (local.value.estado) {
        updateMunicipios(local.value.estado);
        local.value.cidade = formStore.local?.cidade;
    }
});

const cidades = ref<string[]>([]);

const updateMunicipios = async (e: string) => {
    cidades.value = [];
    const idx = estados.value.indexOf(e);
    
    if (idx == -1) return;

    const id = idsEstado.value[idx];
    const arr = await getMunicipios(id);

    cidades.value = arr.map(pair => pair.nome);
}

</script>

<template>

    <FormView
        :items="items"
        :validation-schema="validationSchema"
        :on-prev-click="toPrev"
        :on-submit="onSubmit"
        :prevent-submit="(errors) => 'estado' in errors || 'cidade' in errors"
    >
        <template v-for="item in items" #[`text-${item.name}`]>
            <!-- texto pra telefone -->
            <TextWithIcon v-if="item.name == 'telefone'">
                <PhoneIcon #icon class="w-8 h-8 stroke-dark-blue-transparent" />
                <label :for="item.name">Número de <span class="underline">telefone</span>:</label>
            </TextWithIcon>
        </template>

        <!--
            dropdowns: localidade
            usando datalist para ter autocomplete
        -->
        <template #extra>
            <TextWithIcon>
                <HomeIcon #icon class="w-8 h-8 stroke-dark-blue-transparent" />
                <label for="local">Seu <span class="underline">município e estado</span>:</label>
            </TextWithIcon>

            <!-- estado -->
            <div>
                <Field
                    as="input"
                    list="estados"
                    v-model="local.estado" 
                    name="estado"
                    placeholder="Estado..."
                    class="
                        grid grid-cols-none grid-flow-col auto-cols-auto
                        gap-2 px-3 py-2 min-w-full
                        text-2xl placeholder-dark-blue-transparent font-semibold text-white
                        outline-2 outline-dark-blue rounded-xl bg-dark-blue-transparent
                    "
                    validate-on-input validate-on-change
                    @update:model-value="updateMunicipios"
                >
                    <datalist id="estados">
                        <template v-for="estado in estados">
                            <option :value="estado">{{ estado }}</option>
                        </template>
                    </datalist>
                </Field>
                <ErrorMessage name="estado" class="text-base font-normal text-light-red" />
            </div>

            <!-- cidade -->
            <div>
                <Field
                    as="input"
                    list="cidades"
                    v-model="local.cidade" 
                    name="cidade"
                    placeholder="Município..."
                    class="
                        grid grid-cols-none grid-flow-col auto-cols-auto
                        gap-2 px-3 py-2 min-w-full
                        text-2xl placeholder-dark-blue-transparent font-semibold text-white
                        outline-2 outline-dark-blue rounded-xl bg-dark-blue-transparent
                    "
                    validate-on-input validate-on-change
                    :disabled="!local.estado"
                    :class="{ 'cursor-not-allowed': !local.estado }"
                >
                    <datalist id="cidades">
                        <template v-for="cidade in cidades">
                            <option :value="cidade">{{ cidade }}</option>
                        </template>
                    </datalist>
                </Field>
                <ErrorMessage name="cidade" class="text-base font-normal text-light-red" />
            </div>
        </template>
    </FormView>
</template>