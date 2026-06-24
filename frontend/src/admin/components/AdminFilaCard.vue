<script setup lang="ts">
import BaseCard from '../../shared/components/BaseCard.vue'
import Button from '../../shared/components/Button.vue';
import type { AgendamentoItem } from '../../funcionario/types';

const props = defineProps<{
  agendamento: AgendamentoItem;
}>();

const emit = defineEmits<{
  verMais: [agendamento: AgendamentoItem];
}>();
</script>

<template>
  <BaseCard :item="agendamento">
    
    <div class="ml-auto">
      <Button
        variant="secondary"
        @click="emit('verMais', agendamento)"
      >
        Ver mais
      </Button>
    </div>
    
  </BaseCard>
</template>