<script setup lang="ts">
import { UserGroupIcon, ClockIcon } from '@heroicons/vue/24/outline';
import type { PendenciaItem } from '../types';

import Button from '../../shared/components/Button.vue';

const props = defineProps<{
  pendencia: PendenciaItem;
}>();

const emit = defineEmits<{
  verMais: [pendencia: PendenciaItem];
}>();

function handleVerMais() {
  emit('verMais', props.pendencia);
}
</script>

<template>
  <div class="rounded-lg border border-govbr-border bg-white p-5 transition-shadow hover:shadow-lg">
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-center gap-2">
        <UserGroupIcon class="h-5 w-5 shrink-0 text-govbr-text" />
        <h3 class="text-lg font-bold text-govbr-text">{{ pendencia.nome }}</h3>
      </div>
      <div class="flex shrink-0 items-center gap-2 whitespace-nowrap">
        <span class="flex items-center gap-1 text-sm text-govbr-text-secondary">
          <ClockIcon class="h-4 w-4" />
          há {{ pendencia.diasNaFila }}d
        </span>
        <span :class="[
          'rounded-full px-2.5 py-0.5 text-xs font-bold',
          pendencia.status === 'ALTA' ? 'bg-govbr-error-bg text-govbr-error' :
          pendencia.status === 'MÉDIA' ? 'bg-amber-100 text-amber-800' :
          'bg-green-100 text-green-800'
        ]">
          {{ pendencia.status }}
        </span>
      </div>
    </div>

    <p class="mt-1 text-sm text-govbr-text-secondary">({{ pendencia.prontuario }})</p>

    <span class="mt-3 inline-flex items-center gap-1 rounded-full border border-govbr-primary px-3 py-1 text-xs font-bold text-govbr-primary">
      <ClockIcon class="h-3.5 w-3.5" />
      Situação {{ pendencia.situacao === 'BLOQUEADO' ? 'Bloqueado' : 'Parado' }}
    </span>

    <div class="mt-3 flex flex-wrap gap-2">
      <span
        v-for="exame in pendencia.exames"
        :key="exame"
        class="rounded border border-govbr-border px-3 py-1 text-sm font-semibold text-govbr-text"
      >
        {{ exame }}
      </span>
    </div>

    <div class="mt-4 flex items-center justify-end">
      <Button
        variant="secondary"
        @click="handleVerMais"
      >
        Ver mais
      </Button>
    </div>
  </div>
</template>
