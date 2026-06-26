<script setup lang="ts">
import BaseCard from '../../shared/components/BaseCard.vue';
import Button from '../../shared/components/Button.vue';
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline';
import type { AgendamentoRemovido } from '../types';

defineProps<{
  item: AgendamentoRemovido;
}>();

const emit = defineEmits<{
  verMais: [item: AgendamentoRemovido];
}>();
</script>

<template>
  <BaseCard :item="item">
    <div class="flex flex-col w-full gap-4">
      <p class="text-sm -mt-2 mb-2">
        <span class="font-semibold text-govbr-text">Responsável</span>:
        <span class="text-govbr-text-secondary">{{ item.responsavel }}</span>
      </p>

      <div class="space-y-1 rounded bg-govbr-bg px-3 py-2 text-sm text-govbr-text-secondary">
        <div class="flex items-center gap-2">
          <ExclamationTriangleIcon class="h-4 w-4 shrink-0" />
          <span><span class="font-semibold text-govbr-text">Motivo:</span> {{ item.problema_motivo }}</span>
        </div>
        <p v-if="item.problema_detalhes" class="pl-6">
          <span class="font-semibold text-govbr-text">Detalhes:</span> {{ item.problema_detalhes }}
        </p>
      </div>

      <div class="flex items-center gap-6">
        <Button variant="primary" @click="emit('verMais', item)">
          Ver mais
        </Button>
      </div>
    </div>
  </BaseCard>
</template>
