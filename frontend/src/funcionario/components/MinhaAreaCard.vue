<script setup lang="ts">
import BaseCard from './BaseCard.vue';
import GovButton from './GovButton.vue';
import type { MinhaAreaItem } from '../types';

//  Recebe o objeto específico desta tela através da prop meuItem
defineProps<{
  meuItem: MinhaAreaItem;
}>();

// os eventos que esta tela avisa para o componente Pai
const emit = defineEmits<{
  verMais: [item: MinhaAreaItem];
  devolverAFila: [item: MinhaAreaItem];
}>();
</script>

<template>
  <BaseCard :item="meuItem" v-slot="slotProps">
    
    <GovButton 
      v-if="!slotProps.isFinalizado" 
      variant="tertiary" 
      @click="emit('devolverAFila', meuItem)"
    >
      Devolver à fila
    </GovButton>

    <GovButton 
      variant="primary" 
      @click="emit('verMais', meuItem)"
    >
      Ver mais
    </GovButton>
    
  </BaseCard>
</template>