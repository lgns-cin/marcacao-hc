<script setup lang="ts">
import { UserGroupIcon, ClockIcon } from '@heroicons/vue/24/outline';
import type { AgendamentoItem } from '../../funcionario/types';

const props = defineProps<{
  agendamento: AgendamentoItem;
}>();

const emit = defineEmits<{
  verMais: [agendamento: AgendamentoItem];
}>();

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
        <span :class="[
          'rounded-full px-2.5 py-0.5 text-xs font-bold',
          agendamento.status === 'ALTA' ? 'bg-govbr-error-bg text-govbr-error' :
          agendamento.status === 'MÉDIA' ? 'bg-amber-100 text-amber-800' :
          'bg-green-100 text-green-800'
        ]">
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

    <div class="mt-4 flex items-center justify-end">
      <button class="text-sm font-bold text-govbr-primary hover:underline" @click="handleVerMais">
        Ver mais
      </button>
    </div>
  </div>
</template>
