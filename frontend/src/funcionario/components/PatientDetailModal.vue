<script setup lang="ts">
import { UserGroupIcon, ClockIcon, ArrowDownTrayIcon } from '@heroicons/vue/24/outline';
import Modal from '../../shared/components/Modal.vue';
import type { AgendamentoItem } from '../types';
import GovButton from './GovButton.vue';

const props = defineProps<{
  show: boolean;
  agendamento: AgendamentoItem | null;
}>();

const emit = defineEmits<{
  close: [];
  puxar: [id: number];
}>();

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

    <div v-if="agendamento" class="space-y-4">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <p class="text-sm text-govbr-text-secondary">
          N° do Prontuário: <span class="text-govbr-text">{{ agendamento.prontuario }}</span>
        </p>
        <div class="flex items-center gap-2">
          <span class="flex items-center gap-1 text-sm text-govbr-text-secondary">
            <ClockIcon class="h-4 w-4" />
            há {{ agendamento.diasNaFila }}d na fila
          </span>
          <span class="rounded-full bg-govbr-error-bg px-2.5 py-0.5 text-xs font-bold text-govbr-error">
            {{ agendamento.status }}
          </span>
        </div>
      </div>

      <div class="flex flex-wrap gap-2">
        <span
          v-for="exame in agendamento.exames"
          :key="exame"
          class="rounded border border-govbr-border px-3 py-1 text-sm font-semibold text-govbr-text"
        >
          {{ exame }}
        </span>
      </div>

      <dl class="space-y-3 text-sm">
        <div>
          <dt class="inline font-semibold text-govbr-text">Unidade Executora:</dt>
          <dd class="inline text-govbr-text-secondary"> {{ agendamento.unidadeExecutora }}</dd>
        </div>
        <div>
          <dt class="inline font-semibold text-govbr-text">Unidade Solicitante:</dt>
          <dd class="inline text-govbr-text-secondary"> {{ agendamento.unidadeSolicitante }}</dd>
        </div>
        <div>
          <dt class="inline font-semibold text-govbr-text">Data de retorno:</dt>
          <dd class="inline text-govbr-text-secondary"> {{ agendamento.dataRetorno }}</dd>
        </div>
        <div>
          <dt class="inline font-semibold text-govbr-text">Localização:</dt>
          <dd class="inline text-govbr-text-secondary"> {{ agendamento.localizacao }}</dd>
        </div>
        <div>
          <dt class="inline font-semibold text-govbr-text">Idade:</dt>
          <dd class="inline text-govbr-text-secondary"> {{ agendamento.idade }} anos</dd>
        </div>
      </dl>
    </div>

    <template #footer>
      <GovButton variant="tertiary" @click="emit('close')">
        Fechar
      </GovButton>
      <GovButton variant="primary" @click="handlePuxar">
        <ArrowDownTrayIcon class="h-5 w-5 stroke-2" />
        Puxar
      </GovButton>
    </template>
  </Modal>
</template>
