<script setup lang="ts">
import BaseCard from '../../shared/components/BaseCard.vue'
import Button from '../../shared/components/Button.vue';
import type { AgendamentoGerenciamento } from '../types';

defineProps<{
  item: AgendamentoGerenciamento;
}>();

const emit = defineEmits<{
  verMais: [item: AgendamentoGerenciamento];
}>();
</script>

<template>
  <BaseCard :item="item">

    <div class="flex flex-col w-full gap-2">
      <p class="text-sm -mt-2 mb-2">
        <span class="font-semibold text-govbr-text">Responsável</span>:
        <span class="text-govbr-text-secondary">{{ item.funcionarioAtribuido }}</span>
      </p>

      <div class="flex items-center gap-6">
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