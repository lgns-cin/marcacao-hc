<script setup lang="ts">
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/vue/24/outline';
import type { Kpi } from '../types';

defineProps<{ kpi: Kpi }>();
</script>

<template>
  <div class="rounded-lg border border-govbr-border bg-white p-5">
    <span class="text-3xl font-extrabold text-govbr-text">
      {{ kpi.valor }}<span v-if="kpi.sufixo" class="text-lg font-bold"> {{ kpi.sufixo }}</span>
    </span>
    <p class="mt-1 text-sm text-govbr-text-secondary">{{ kpi.label }}</p>
    <span
      v-if="kpi.tendencia"
      :class="[
        'mt-2 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-bold',
        kpi.tendencia >= 0 ? 'bg-green-100 text-green-800' : 'bg-govbr-error-bg text-govbr-error'
      ]"
    >
      <ArrowUpIcon v-if="kpi.tendencia >= 0" class="h-3 w-3" />
      <ArrowDownIcon v-else class="h-3 w-3" />
      {{ Math.abs(kpi.tendencia) }}%
    </span>
  </div>
</template>
