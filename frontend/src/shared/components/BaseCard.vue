<script setup lang="ts">
import { computed } from 'vue';
import { UserGroupIcon, ClockIcon } from '@heroicons/vue/24/solid';

// Componente base para o card de fila(funcionário e admin)
/**
 * Definição de props
 * usamos uma tipagem flexível para o 'item' para que ele consiga aceitar 
 * tanto a interface AgendamentoItem quanto a MinhaAreaItem
 */
const props = defineProps<{
  item: {
    nome: string;
    prontuario: string;
    status: string;
    diasNaFila: number;
    exames: string[];
    estado?: string;
    resultado?: string;
  };
}>();

// identifica se o item recebido está no estado FINALIZADO.
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
  <div class="rounded-lg bg-white p-5 shadow-[0_0_7.6px_rgba(0,0,0,0.15)] transition-shadow hover:shadow-xl">
    
    <div class="flex items-start justify-between gap-3">
      
      <div class="flex items-center gap-2">
        <UserGroupIcon class="h-6 w-6 shrink-0 text-govbr-text" />
        <h3 class="text-lg font-bold text-govbr-text">{{ item.nome }}</h3>
      </div>

      <div class="flex shrink-0 items-center gap-2 whitespace-nowrap">
        <template v-if="!finalizado">
          <span class="flex items-center gap-1 text-sm text-govbr-text-secondary">
            <ClockIcon class="h-4 w-4" />
            há {{ item.diasNaFila }}d
          </span>
          <span :class="['rounded-full px-2.5 py-1.5 text-xs font-bold', statusClasses]">
            {{ item.status }}
          </span>
        </template>

        <span 
          v-else 
          class="rounded-full border border-govbr-border px-2.5 py-0.5 text-xs font-bold text-govbr-text-secondary"
        >
          {{ item.resultado }}
        </span>
      </div>
    </div>

    <p class="mt-1 text-[16px] text-govbr-text-secondary">({{ item.prontuario }})</p>

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
      <slot :isFinalizado="finalizado"></slot>
    </div>

  </div>
</template>