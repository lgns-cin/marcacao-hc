<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount } from 'vue';
import { MagnifyingGlassIcon, ChevronDownIcon } from '@heroicons/vue/24/outline';
import type { Funcionario } from '../../admin/types';

import Button from './Button.vue';

const props = defineProps<{
  modelValue: string;
  opcoes: Funcionario[];
  placeholder?: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [valor: string];
}>();

const aberto = ref(false);
const raiz = ref<HTMLElement | null>(null);

const nomeSelecionado = computed(() => props.opcoes.find((f) => f.username === props.modelValue)?.nome ?? '');

function fecharSeClicarFora(event: MouseEvent) {
  if (raiz.value && !raiz.value.contains(event.target as Node)) {
    aberto.value = false;
  }
}

watch(aberto, (estaAberto) => {
  if (estaAberto) {
    document.addEventListener('click', fecharSeClicarFora);
  } else {
    document.removeEventListener('click', fecharSeClicarFora);
  }
});

function selecionar(funcionario: Funcionario) {
  emit('update:modelValue', funcionario.username);
  aberto.value = false;
}

onBeforeUnmount(() => document.removeEventListener('click', fecharSeClicarFora));
</script>

<template>
  <div ref="raiz">
    <Button
      type="button"
      variant="secondary"
      @click="aberto = !aberto"
    >
      <span class="flex items-center gap-2 truncate">
        <MagnifyingGlassIcon class="h-4 w-4 shrink-0 text-govbr-text-secondary" />
        <span :class="nomeSelecionado ? 'text-govbr-text' : 'italic text-govbr-text-secondary'">
          {{ nomeSelecionado || props.placeholder || 'Selecione um funcionário' }}
        </span>
      </span>
      <ChevronDownIcon class="h-4 w-4 shrink-0 text-govbr-primary" />
    </Button>

    <ul
      v-if="aberto"
      class="mt-1 overflow-hidden rounded border border-govbr-border bg-white shadow-sm"
    >
      <li
        v-for="funcionario in props.opcoes"
        :key="funcionario.username"
        class="cursor-pointer px-3 py-3 text-sm text-govbr-text hover:bg-govbr-bg"
        :class="{ 'bg-govbr-bg': funcionario.username === modelValue }"
        @click="selecionar(funcionario)"
      >
        {{ funcionario.nome }}
      </li>
    </ul>
  </div>
</template>
