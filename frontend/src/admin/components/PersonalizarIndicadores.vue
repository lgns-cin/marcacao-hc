<script setup lang="ts">
import { ref, watch } from 'vue';
import Button from '../../shared/components/Button.vue';

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
  <!-- TO DO: retirar a personalização de indicadores -->
  <div class="relative">
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
        <Button
          variant="secondary"
          @click="selecionarTodos"
        >
          Selecionar todos
        </Button>
        <Button
          variant="primary"
          @click="aplicar"
        >
          Aplicar
        </Button>
      </div>
    </div>
  </div>
</template>
