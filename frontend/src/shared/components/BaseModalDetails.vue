<script setup lang="ts">
import { computed } from 'vue';
import { ClockIcon } from '@heroicons/vue/24/outline';

// Esse componente é uma base utilizada na tela do funcionário e admin(modal)
// Foi criada para facilitar a manutenção e padronização

// Tipagem focada para aceitar os dados das três telas
const props = defineProps<{
  item: {
    prontuario: string;
    diasNaFila: number;
    status: string;
    exames: string[];
    unidadeExecutora: string;
    unidadeSolicitante: string;
    dataRetorno: string;
    localizacao: string;
    idade: number;
    estado?: string;
    resultado?: string;
  };
}>();

// Identifica se o agendamento já foi finalizado
const finalizado = computed(() => props.item.estado === 'FINALIZADO');

// mapeamento das cores
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
      <p class="text-[16px] text-govbr-text-secondary">
        N° do Prontuário: <span class="text-govbr-text font-medium">{{ item.prontuario }}</span>
      </p>
      
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
        {{ item.resultado }}
      </span>
    </div>

    <div class="flex flex-wrap gap-2">
      <span
        v-for="exame in item.exames"
        :key="exame"
        class="rounded border border-govbr-border px-3 py-1 text-sm font-semibold text-govbr-text bg-gray-50"
      >
        {{ exame }}
      </span>
    </div>

    <dl class="space-y-3 text-[16px] pt-2">
      <!-- Não mostrar a unidade executora por enquanto
      <div>
        <dt class="inline font-semibold text-govbr-text">Unidade Executora: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ item.unidadeExecutora }}</dd>
      </div>
      -->
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