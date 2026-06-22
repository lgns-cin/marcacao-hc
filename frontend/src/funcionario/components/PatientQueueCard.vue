<script setup lang="ts">
import { UserGroupIcon, ClockIcon, ArrowDownTrayIcon } from '@heroicons/vue/24/outline';
import type { AgendamentoItem } from '../types';

const props = defineProps<{
  agendamento: AgendamentoItem;
}>();

const emit = defineEmits<{
  puxar: [id: number];
  verMais: [agendamento: AgendamentoItem];
}>();

function handlePuxar() {
  emit('puxar', props.agendamento.id);
}

function handleVerMais() {
  emit('verMais', props.agendamento);
}
</script>

<template>
  <div class="rounded-lg border border-govbr-border bg-white p-5 transition-shadow hover:shadow-lg">
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-center gap-2">
        <UserGroupIcon class="h-5 w-5 shrink-0 text-govbr-text" />
        <h3 class="text-lg font-bold text-govbr-text">{{ agendamento.nome }}</h3>
      </div>
      <div class="flex shrink-0 items-center gap-2 whitespace-nowrap">
        <span class="flex items-center gap-1 text-sm text-govbr-text-secondary">
          <ClockIcon class="h-4 w-4" />
          há {{ agendamento.diasNaFila }}d
        </span>
        <span class="rounded-full bg-govbr-error-bg px-2.5 py-0.5 text-xs font-bold text-govbr-error">
          {{ agendamento.status }}
        </span>
      </div>
    </div>

    <p class="mt-1 text-sm text-govbr-text-secondary">({{ agendamento.prontuario }})</p>

    <div class="mt-3 flex flex-wrap gap-2">
      <span
        v-for="exame in agendamento.exames"
        :key="exame"
        class="rounded border border-govbr-border px-3 py-1 text-sm font-semibold text-govbr-text"
      >
        {{ exame }}
      </span>
    </div>

    <div class="mt-4 flex items-center gap-6">
      <button
        class="flex items-center gap-2 rounded-full bg-govbr-primary px-5 py-2 text-sm font-bold text-white hover:bg-govbr-primary-hover"
        @click="handlePuxar"
      >
        <ArrowDownTrayIcon class="h-5 w-5" />
        Puxar
      </button>
      <button class="text-sm font-bold text-govbr-primary hover:underline" @click="handleVerMais">
        Ver mais
      </button>
    </div>
  </div>
</template>
