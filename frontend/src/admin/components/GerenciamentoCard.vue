<script setup lang="ts">
import { computed } from 'vue';
import { UserGroupIcon, ClockIcon } from '@heroicons/vue/24/outline';
import type { AgendamentoGerenciamento } from '../types';

const props = defineProps<{
  item: AgendamentoGerenciamento;
}>();

const emit = defineEmits<{
  verMais: [item: AgendamentoGerenciamento];
  devolverAFila: [item: AgendamentoGerenciamento];
}>();

const finalizado = computed(() => props.item.estado === 'FINALIZADO');

function handleVerMais() {
  emit('verMais', props.item);
}

function handleDevolverAFila() {
  emit('devolverAFila', props.item);
}
</script>

<template>
  <div class="rounded-lg border border-govbr-border bg-white p-5 transition-shadow hover:shadow-lg">
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-center gap-2">
        <UserGroupIcon class="h-5 w-5 shrink-0 text-govbr-text" />
        <h3 class="text-lg font-bold text-govbr-text">{{ item.nome }}</h3>
      </div>
      <div class="flex shrink-0 items-center gap-2 whitespace-nowrap">
        <template v-if="!finalizado">
          <span class="flex items-center gap-1 text-sm text-govbr-text-secondary">
            <ClockIcon class="h-4 w-4" />
            há {{ item.diasNaFila }}d
          </span>
          <span :class="[
            'rounded-full px-2.5 py-0.5 text-xs font-bold',
            item.status === 'ALTA' ? 'bg-govbr-error-bg text-govbr-error' :
            item.status === 'MÉDIA' ? 'bg-amber-100 text-amber-800' :
            'bg-green-100 text-green-800'
          ]">
            {{ item.status }}
          </span>
        </template>
        <span v-else class="rounded-full border border-govbr-border px-2.5 py-0.5 text-xs font-bold text-govbr-text-secondary">
          {{ item.resultado }}
        </span>
      </div>
    </div>

    <p class="text-sm">
      <span class="font-semibold text-govbr-text">Responsável</span>:
      <span class="text-govbr-text-secondary">{{ item.responsavel }}</span>
    </p>
    <p class="mt-1 text-sm text-govbr-text-secondary">({{ item.prontuario }})</p>

    <div class="mt-3 flex flex-wrap gap-2">
      <span
        v-for="exame in item.exames"
        :key="exame"
        class="rounded border border-govbr-border px-3 py-1 text-sm font-semibold text-govbr-text"
      >
        {{ exame }}
      </span>
    </div>

    <div class="mt-4 flex items-center gap-6">
      <button
        v-if="!finalizado"
        class="flex items-center gap-1 text-sm font-bold text-govbr-primary hover:underline"
        @click="handleDevolverAFila"
      >
        <ClockIcon class="h-4 w-4" />
        Devolver à fila
      </button>
      <button
        class="ml-auto rounded-full bg-govbr-primary px-5 py-2 text-sm font-bold text-white hover:bg-govbr-primary-hover"
        @click="handleVerMais"
      >
        Ver mais
      </button>
    </div>
  </div>
</template>
