<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue';
import { MagnifyingGlassIcon, ChevronDownIcon } from '@heroicons/vue/24/outline';
import Button from '../../shared/components/Button.vue';

const props = defineProps<{
  modelValue: string;
  opcoes: string[];
  placeholder?: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [valor: string];
}>();

const aberto = ref(false);
const raiz = ref<HTMLElement | null>(null);

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

function selecionar(opcao: string) {
  emit('update:modelValue', opcao);
  aberto.value = false;
}

onBeforeUnmount(() => document.removeEventListener('click', fecharSeClicarFora));
</script>

<template>
  <div ref="raiz">
    <Button variant="tertiary" class="border border-govbr-border" @click="aberto = !aberto">
      <span class="flex items-center gap-2 truncate">
        <MagnifyingGlassIcon class="h-4 w-4 shrink-0 text-govbr-text-secondary" />
        <span :class="modelValue ? 'text-govbr-text' : 'italic text-govbr-text-secondary'">
          {{ modelValue || props.placeholder || 'Selecione a opção' }}
        </span>
      </span>
      <ChevronDownIcon class="h-4 w-4 shrink-0 text-govbr-primary" />
    </Button>

    <ul
      v-if="aberto"
      class="mt-1 overflow-hidden rounded border border-govbr-border bg-white shadow-sm"
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
