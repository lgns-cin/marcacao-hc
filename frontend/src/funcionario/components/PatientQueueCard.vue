<script setup lang="ts">
import { computed } from 'vue';
import { UserGroupIcon, ArrowDownTrayIcon } from '@heroicons/vue/24/solid';
import { ClockIcon } from '@heroicons/vue/24/outline';
import type { AgendamentoItem } from '../types';
import GovButton from './GovButton.vue';

// Definição de Props com tipos estritos
// Lembrete: Props são de Pai para filho
const props = defineProps<{
  agendamento: AgendamentoItem;
}>();

// Definição de Emits autorizados
// Lembrete: Emits são de Filho para Pai
const emit = defineEmits<{
  puxar: [id: number];
  verMais: [agendamento: AgendamentoItem];
}>();

// mapeamento das cores de prioridade
const statusClasses = computed(() => {
  const cores = {
    ALTA: 'bg-govbr-error-bg text-govbr-error',
    MÉDIA: 'bg-amber-100 text-amber-800',
    BAIXA: 'bg-green-100 text-green-800'
  };
  
  return cores[props.agendamento.status as keyof typeof cores] || 'bg-gray-100 text-gray-800';
});
</script>

<template>
  <div 
    class="
      rounded-lg bg-white p-5
      shadow-[0_0_7.6px_rgba(0,0,0,0.15)]
      transition-shadow hover:shadow-xl
    "
  >
    <div class="flex items-start justify-between gap-3">
      
      <div class="flex items-center gap-2">
        <UserGroupIcon class="h-6 w-6 shrink-0 text-govbr-text" />
        <h3 class="text-lg font-bold text-govbr-text">{{ agendamento.nome }}</h3>
      </div>

      <div class="flex shrink-0 items-center gap-2 whitespace-nowrap">
        <span class="flex items-center gap-1 text-sm text-govbr-text-secondary">
          <ClockIcon class="h-4 w-4" />
          há {{ agendamento.diasNaFila }}d
        </span>
        <span :class="['rounded-full px-2.5 py-1.5 text-xs font-bold', statusClasses]">
          {{ agendamento.status }}
        </span>
      </div>
      
    </div>

    <p class="mt-1 text-[16px] text-govbr-text-secondary">({{ agendamento.prontuario }})</p>

    <div class="mt-3 flex flex-wrap gap-2">
      <span
        v-for="exame in agendamento.exames"
        :key="exame"
        class="
          rounded border border-govbr-border px-3 py-1 
          text-sm font-semibold text-govbr-text
        "
      >
        {{ exame }}
      </span>
    </div>

    <div class="mt-4 flex items-center gap-6">
      <GovButton variant="primary" @click="emit('puxar', agendamento.id)">
        <ArrowDownTrayIcon class="h-5 w-5 stroke-2" />
        Puxar
      </GovButton>

      <GovButton variant="tertiary" @click="emit('verMais', agendamento)">
        Ver mais
      </GovButton>
    </div>

  </div>
</template>