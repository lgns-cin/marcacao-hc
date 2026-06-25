<script setup lang="ts">
import { UserGroupIcon, ClockIcon, ArrowUturnLeftIcon } from '@heroicons/vue/24/outline';
import type { AgendamentoRemovido } from '../types';

defineProps<{
  item: AgendamentoRemovido;
}>();
</script>

<template>
  <div class="rounded-lg border border-govbr-border bg-white p-5">
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-center gap-2">
        <UserGroupIcon class="h-5 w-5 shrink-0 text-govbr-text" />
        <h3 class="text-lg font-bold text-govbr-text">{{ item.nome }}</h3>
      </div>
      <span class="flex shrink-0 items-center gap-1 text-sm text-govbr-text-secondary">
        <ClockIcon class="h-4 w-4" />
        há {{ item.diasNaFila }}d
      </span>
    </div>

    <p class="text-sm">
      <span class="font-semibold text-govbr-text">Responsável</span>:
      <span class="text-govbr-text-secondary">{{ item.responsavel }}</span>
    </p>
    <p class="mt-0.5 text-sm text-govbr-text-secondary">({{ item.prontuario }})</p>

    <div class="mt-3">
      <span class="rounded border border-govbr-border px-3 py-1 text-sm font-semibold text-govbr-text">
        {{ item.exame }}
      </span>
    </div>

    <div class="mt-3 flex items-center gap-2 rounded bg-govbr-bg px-3 py-2 text-sm text-govbr-text-secondary">
      <ArrowUturnLeftIcon class="h-4 w-4 shrink-0" />
      <span><span class="font-semibold text-govbr-text">Motivo:</span> {{ item.motivoDevolucao }}</span>
    </div>
  </div>
</template>
