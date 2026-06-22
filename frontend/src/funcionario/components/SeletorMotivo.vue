<script setup lang="ts">
import { ref } from 'vue';
import { MagnifyingGlassIcon, ChevronDownIcon } from '@heroicons/vue/24/outline';

const props = defineProps<{
  modelValue: string;
  opcoes: string[];
  placeholder?: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [valor: string];
}>();

const aberto = ref(false);

function selecionar(opcao: string) {
  emit('update:modelValue', opcao);
  aberto.value = false;
}
</script>

<template>
  <div class="relative">
    <button
      type="button"
      class="flex w-full items-center justify-between gap-2 rounded border border-govbr-border px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-govbr-primary"
      @click="aberto = !aberto"
    >
      <span class="flex items-center gap-2 truncate">
        <MagnifyingGlassIcon class="h-4 w-4 shrink-0 text-govbr-text-secondary" />
        <span :class="modelValue ? 'text-govbr-text' : 'italic text-govbr-text-secondary'">
          {{ modelValue || props.placeholder || 'Selecione a opção' }}
        </span>
      </span>
      <ChevronDownIcon class="h-4 w-4 shrink-0 text-govbr-primary" />
    </button>

    <div v-if="aberto" class="fixed inset-0 z-10" @click="aberto = false" />

    <ul
      v-if="aberto"
      class="absolute z-20 mt-1 w-full overflow-hidden rounded border border-govbr-border bg-white shadow-lg"
    >
      <li
        v-for="opcao in props.opcoes"
        :key="opcao"
        class="cursor-pointer px-3 py-3 text-sm text-govbr-text hover:bg-govbr-bg"
        :class="{ 'bg-govbr-bg': opcao === modelValue }"
        @click="selecionar(opcao)"
      >
        {{ opcao }}
      </li>
    </ul>
  </div>
</template>
