<script setup lang="ts">
import { computed } from 'vue';
import { ClockIcon } from '@heroicons/vue/24/outline';

const props = defineProps<{
  item: {
    prontuario: string;
    numeroSolicitacao?: string;
    diasNaFila: number;
    status: string;
    exame: string;
    unidadeSolicitante: string;
    dataRetorno: string;
    localizacao: string;
    idade: number;
    estado?: string;
  };
}>();

const finalizado = computed(() =>
  props.item.estado === 'CONFIRMADO' || props.item.estado === 'PROBLEMA_REPORTADO'
);

const estadoLabel = computed(() => {
  if (props.item.estado === 'CONFIRMADO') return 'Confirmado';
  if (props.item.estado === 'PROBLEMA_REPORTADO') return 'Encerrado';
  return '';
});

const statusClasses = computed(() => {
  const cores = {
    ALTA: 'bg-govbr-error-bg text-govbr-error',
    MÉDIA: 'bg-amber-100 text-amber-800',
    BAIXA: 'bg-green-100 text-green-800'
  };
  return cores[props.item.status as keyof typeof cores] || 'bg-gray-100 text-gray-800';
});
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-2">      
      <div class="flex flex-wrap gap-2">
        <span class="rounded border border-govbr-border px-3 py-1 text-sm font-semibold text-govbr-text bg-gray-50">
          {{ item.exame }}
        </span>
      </div>

      <div v-if="!finalizado" class="flex items-center gap-2">
        <span class="flex items-center gap-1 text-[16px] text-govbr-text-secondary">
          <ClockIcon class="h-4 w-4" />
          há {{ item.diasNaFila }}d
        </span>
        <span :class="['rounded-full px-2.5 py-0.5 text-xs font-bold', statusClasses]">
          {{ item.status }}
        </span>
      </div>
      <span v-else class="rounded-full border border-govbr-border px-2.5 py-0.5 text-xs font-bold text-govbr-text-secondary">
        {{ estadoLabel }}
      </span>
    </div>

    <dl class="space-y-3 text-[16px] pt-2">
      <div>
        <dt v-if="item.numeroSolicitacao" class="inline font-semibold text-govbr-text">Solicitação: </dt>
        <dd v-if="item.numeroSolicitacao" class="inline text-govbr-text-secondary"> {{ item.numeroSolicitacao }}</dd>
      </div>
      <div>
        <dt class="inline font-semibold text-govbr-text">Prontuário: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ item.prontuario }}</dd>
      </div>
      <div>
        <dt class="inline font-semibold text-govbr-text">Exame: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ item.exame }}</dd>
      </div>
      <div>
        <dt class="inline font-semibold text-govbr-text">Unidade Solicitante: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ item.unidadeSolicitante }}</dd>
      </div>
      <div>
        <dt class="inline font-semibold text-govbr-text">Data de retorno: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ item.dataRetorno }}</dd>
      </div>
      <div>
        <dt class="inline font-semibold text-govbr-text">Localização: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ item.localizacao }}</dd>
      </div>
      <div>
        <dt class="inline font-semibold text-govbr-text">Idade: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ item.idade }} anos</dd>
      </div>
    </dl>

    <slot></slot>
  </div>
</template>
