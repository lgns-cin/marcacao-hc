<script setup lang="ts">
import BaseCard from '../../shared/components/BaseCard.vue'
import Button from '../../shared/components/Button.vue';
import { ClockIcon } from '@heroicons/vue/24/outline';
import type { PendenciaItem } from '../types';

defineProps<{
  pendencia: PendenciaItem;
}>();

const emit = defineEmits<{
  verMais: [pendencia: PendenciaItem];
}>();
</script>

<template>
  <BaseCard :item="pendencia">
    
    <div class="flex w-full items-center justify-between gap-4">
      <span class="inline-flex items-center gap-1 rounded-full border border-govbr-primary px-3 py-1 text-xs font-bold text-govbr-primary">
        <ClockIcon class="h-3.5 w-3.5" />
        Situação {{ pendencia.situacao === 'BLOQUEADO' ? 'Bloqueado' : 'Parado' }}
      </span>

      <Button
        class="ml-auto"
        variant="secondary"
        @click="emit('verMais', pendencia)"
      >
        Ver mais
      </Button>
    </div>
    
  </BaseCard>
</template>