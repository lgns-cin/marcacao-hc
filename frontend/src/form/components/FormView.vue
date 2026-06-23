<script setup lang="ts">
import { ArrowLeftIcon, ArrowRightIcon, CheckIcon, XMarkIcon } from '@heroicons/vue/24/outline';
import { ref } from 'vue';
import FormContainer from './FormContainer.vue';
import ButtonWithIcon from './ButtonWithIcon.vue';
import { ErrorMessage, Field, Form, TypedSchema } from 'vee-validate';

const props = defineProps<{
    imgSrc?: string
    items: { name: string, type: string, placeholder: string, default?: any }[]
    validationSchema: TypedSchema<any>
    onPrevClick: () => void
    onSubmit: (values: any, actions: any) => void
    preventSubmit?: (errors: Partial<Record<string, string | undefined>>) => boolean
}>();

const values = ref<any[]>(
    // atribuindo os valores default para cada campo a ser preenchido
    Array.from(
        { length: props.items.length },
        (_, i) => props.items[i].default
    )
);

const invalidValuesPresent = (errors: Partial<Record<string, string | undefined>>) => {
    for (let i = 0; i < props.items.length; i++) {
        const v = values.value[i];
        const name = props.items[i].name;
        if (v == undefined || name in errors) return true;
    }

    return false;
}

</script>

<template>
    <img v-if="props.imgSrc" :src="`../../public/${props.imgSrc}.png`" class="max-w-[328px] rounded-xl" />

    <Form
        v-slot="{ isSubmitting, getErrors }"
        @submit="props.onSubmit" 
        :validation-schema="props.validationSchema"
    >
        <FormContainer>
            <template #contents>
                <!-- aqui, todo item em items tem um campo específico -->
                <template v-for="item in props.items" :key="item.name">
                    <slot :name="`text-${item.name}`"></slot>
                    <div>
                        <div
                            class="
                                grid grid-cols-none grid-flow-col auto-cols-auto
                                gap-2 px-3 py-2 
                                outline-2 rounded-xl bg-dark-blue-transparent
                            "
                            :class="[
                                item.name in getErrors()
                                    ? 'outline-light-red' 
                                    : values[props.items.indexOf(item)] != undefined 
                                        ? 'outline-light-green' 
                                        : 'outline-dark-blue'
                            ]"
                        >
                            <Field
                                :name="item.name"
                                as="input"
                                :type="item.type"
                                class="
                                    min-w-full border-b-2 border-dotted border-dark-blue-transparent
                                    font-semibold text-3xl text-white placeholder-dark-blue-transparent
                                " 
                                :placeholder="item.placeholder"
                                v-model="values[props.items.indexOf(item)]"
                                validate-on-input
                            />
                            <XMarkIcon
                                #icon
                                v-if="item.name in getErrors()"
                                class="stroke-light-red stroke-2 w-10 h-10 min-w-full"
                            />
                            <CheckIcon
                                #icon
                                v-else-if="values[props.items.indexOf(item)] != undefined"
                                class="stroke-light-green stroke-2 w-10 h-10 min-w-full"
                            />
                        </div>
                        <ErrorMessage :name="item.name" class="text-base font-normal text-light-red" />
                    </div>
                </template>
                <slot name="extra"></slot>
            </template>

            <template #buttons>
                <ButtonWithIcon @click="props.onPrevClick">
                    <ArrowLeftIcon #icon class="w-8 h-8 stroke-2 stroke-white"/>
                </ButtonWithIcon>
                <ButtonWithIcon type="submit" :disabled="invalidValuesPresent(getErrors()) || (props.preventSubmit && props.preventSubmit(getErrors())) || isSubmitting">
                    <ArrowRightIcon #icon class="w-8 h-8 stroke-2 stroke-white"/>
                </ButtonWithIcon>
            </template>
        </FormContainer>
    </Form>
</template>