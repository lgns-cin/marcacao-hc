<script setup lang="ts">
import { computed } from 'vue';
import type { Kpi } from '../types';

const props = defineProps<{ kpi: Kpi }>();

// formatação baseada no tipo de dado que vem do backend
const valorFormatado = computed(() => {
  if (props.kpi.valor === undefined || props.kpi.valor === null) return '0';

  switch (props.kpi.formato) {
    case 'porcentagem':
      return `${props.kpi.valor}%`;
    case 'dias':
      // Se for 1, exibe no singular "1 dia", se for mais, "X dias"
      return Number(props.kpi.valor) === 1 ? '1 dia' : `${props.kpi.valor} dias`;
    case 'numero':
    default:
      return props.kpi.valor; // Retorna o número puro (int ou float)
  }
});
</script>

<template>
  <div class="rounded-lg border border-govbr-border bg-white p-5">
    <span class="text-3xl font-extrabold text-govbr-text">
      {{ valorFormatado }}
    </span>
    <p class="mt-1 text-[16px] font-semibold">{{ kpi.titulo }}</p>
    <p class="text-[14px] text-govbr-text-secondary/70">no mês atual</p>
  </div>
</template>