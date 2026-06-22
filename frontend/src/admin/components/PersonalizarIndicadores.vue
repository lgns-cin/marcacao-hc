<script setup lang="ts">
import { ref, watch } from 'vue';
import { AdjustmentsHorizontalIcon } from '@heroicons/vue/24/outline';

const props = defineProps<{
  todos: { id: string; label: string }[];
  selecionados: string[] | null;
}>();

const emit = defineEmits<{
  aplicar: [ids: string[]];
}>();

const aberto = ref(false);
const marcados = ref<string[]>(props.selecionados ?? props.todos.map((item) => item.id));

watch(
  () => props.selecionados,
  (novo) => {
    marcados.value = novo ?? props.todos.map((item) => item.id);
  }
);

function selecionarTodos() {
  marcados.value = props.todos.map((item) => item.id);
}

function aplicar() {
  emit('aplicar', marcados.value);
  aberto.value = false;
}
</script>

<template>
  <div class="relative">
    <button
      class="flex items-center gap-2 rounded-full border border-govbr-primary px-5 py-2 text-sm font-bold text-govbr-primary hover:bg-govbr-bg"
      @click="aberto = !aberto"
    >
      <AdjustmentsHorizontalIcon class="h-5 w-5" />
      Personalizar Indicadores
    </button>

    <div v-if="aberto" class="fixed inset-0 z-10" @click="aberto = false" />

    <div
      v-if="aberto"
      class="absolute right-0 z-20 mt-2 max-h-96 w-80 overflow-y-auto rounded-lg border border-govbr-border bg-white p-4 shadow-lg"
    >
      <p class="mb-3 text-sm font-semibold text-govbr-text">Selecione os indicadores visíveis</p>
      <div class="space-y-2">
        <label v-for="item in todos" :key="item.id" class="flex items-center gap-2 text-sm text-govbr-text">
          <input
            type="checkbox"
            :value="item.id"
            v-model="marcados"
            class="h-4 w-4 rounded border-govbr-border text-govbr-primary focus:ring-govbr-primary"
          />
          {{ item.label }}
        </label>
      </div>
      <div class="mt-4 flex items-center justify-between gap-3">
        <button class="text-sm font-bold text-govbr-primary hover:underline" @click="selecionarTodos">
          Selecionar todos
        </button>
        <button
          class="rounded-full bg-govbr-primary px-5 py-2 text-sm font-bold text-white hover:bg-govbr-primary-hover"
          @click="aplicar"
        >
          Aplicar
        </button>
      </div>
    </div>
  </div>
</template>
