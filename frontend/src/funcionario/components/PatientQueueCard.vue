<script setup lang="ts">
import BaseCard from './BaseCard.vue';
import GovButton from '../../shared/components/GovButton.vue';
import { ArrowDownTrayIcon } from '@heroicons/vue/24/solid';
import type { AgendamentoItem } from '../types';

//  Recebe o objeto específico da fila através da prop 'agendamento'
defineProps<{
  agendamento: AgendamentoItem;
}>();

//  os eventos que esta tela avisa para o componente Pai
const emit = defineEmits<{
  puxar: [id: number];
  verMais: [agendamento: AgendamentoItem];
}>();
</script>

<template>
  <BaseCard :item="agendamento">
    
    <GovButton variant="primary" @click="emit('puxar', agendamento.id)">
      <ArrowDownTrayIcon class="h-5 w-5 stroke-2" />
      Puxar
    </GovButton>

    <GovButton variant="tertiary" @click="emit('verMais', agendamento)">
      Ver mais
    </GovButton>
    
  </BaseCard>
</template>