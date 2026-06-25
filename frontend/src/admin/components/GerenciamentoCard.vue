<script setup lang="ts">
import BaseCard from '../../shared/components/BaseCard.vue'
import Button from '../../shared/components/Button.vue';
import { ClockIcon } from '@heroicons/vue/24/outline';
import type { AgendamentoGerenciamento } from '../types';

defineProps<{
  item: AgendamentoGerenciamento;
}>();

const emit = defineEmits<{
  verMais: [item: AgendamentoGerenciamento];
  devolverAFila: [item: AgendamentoGerenciamento];
}>();
</script>

<template>
  <BaseCard :item="item" v-slot="slotProps">
    
    <div class="flex flex-col w-full gap-4">
      <p class="text-sm -mt-2 mb-2">
        <span class="font-semibold text-govbr-text">Responsável</span>:
        <span class="text-govbr-text-secondary">{{ item.responsavel }}</span>
      </p>

      <div class="flex items-center gap-6">
        <Button
          v-if="!slotProps.isFinalizado"
          variant="secondary"
          @click="emit('devolverAFila', item)"
        >
          <ClockIcon class="h-4 w-4" />
          Devolver à fila
        </Button>
        
        <Button
          variant="primary"
          @click="emit('verMais', item)"
        >
          Ver mais
        </Button>
      </div>
    </div>
    
  </BaseCard>
</template>