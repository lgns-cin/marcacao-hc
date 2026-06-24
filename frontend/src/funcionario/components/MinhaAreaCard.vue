<script setup lang="ts">
import BaseCard from '../../shared/components/BaseCard.vue';
import Button from '../../shared/components/Button.vue';
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
    
    <Button 
      v-if="!slotProps.isFinalizado" 
      variant="tertiary" 
      @click="emit('devolverAFila', meuItem)"
    >
      Devolver à fila
    </Button>

    <Button 
      variant="primary" 
      @click="emit('verMais', meuItem)"
    >
      Ver mais
    </Button>
    
  </BaseCard>
</template>