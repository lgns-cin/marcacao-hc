<script setup lang="ts">
import { ArrowDownTrayIcon } from '@heroicons/vue/24/outline';
import { UserGroupIcon } from '@heroicons/vue/24/solid';
import Modal from '../../shared/components/Modal.vue';
import BaseModalDetails from '../../shared/components/BaseModalDetails.vue';
import type { AgendamentoItem } from '../types';
import Button from '../../shared/components/Button.vue';

// Definindo as propriedades do componente
const props = defineProps<{
  show: boolean;
  agendamento: AgendamentoItem | null;
}>();

const emit = defineEmits<{
  close: []; // é só um sinal de alerta
  puxar: [id: number];
}>();

// emitindo um evento para o componente pai para puxar o agendamento
function handlePuxar() {
  if (props.agendamento) emit('puxar', props.agendamento.id);
}
</script>

<template>
  <Modal :show="show" @close="emit('close')">
    <template #header>
      <span v-if="agendamento" class="flex items-center gap-2">
        <UserGroupIcon class="h-6 w-6 text-govbr-text" />
        {{ agendamento.nome }}
      </span>
    </template>

    <BaseModalDetails v-if="agendamento" :item="agendamento" />

    <template #footer>
      <Button variant="tertiary" @click="emit('close')">
        Fechar
      </Button>
      <Button variant="primary" @click="handlePuxar">
        <ArrowDownTrayIcon class="h-5 w-5 stroke-2" />
        Puxar
      </Button>
    </template>
  </Modal>
</template>