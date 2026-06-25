<script setup lang="ts">
import { ref, watch } from 'vue';
import {
  ClockIcon,
  ArrowLeftIcon,
  InformationCircleIcon,
} from '@heroicons/vue/24/outline';
import { UserGroupIcon } from '@heroicons/vue/20/solid';
import Modal from '../../shared/components/Modal.vue';
import BaseModalDetails from '../../shared/components/BaseModalDetails.vue';
import SeletorMotivo from './SeletorMotivo.vue';
import { MOTIVOS_DEVOLUCAO, MOTIVOS_PROBLEMA } from '../types';
import type { MinhaAreaItem } from '../types';
import Button from '../../shared/components/Button.vue';

type Visao = 'detalhes' | 'reportarProblema' | 'devolverAFila';

const props = defineProps<{
  show: boolean;
  item: MinhaAreaItem | null;
  visaoInicial?: Visao;
}>();

const emit = defineEmits<{
  close: [];
  aguardarConfirmacao: [id: number];
  devolverAFila: [id: number, motivo: string];
  reportarProblema: [id: number, motivo: string];
  finalizar: [id: number];
}>();

const visao = ref<Visao>('detalhes');
const motivoProblema = ref('');
const motivoDevolucao = ref('');

watch(
  () => props.show,
  (aberto) => {
    if (aberto) {
      visao.value = props.visaoInicial ?? 'detalhes';
      motivoProblema.value = '';
      motivoDevolucao.value = '';
    }
  }
);

function fechar() {
  emit('close');
}

function voltarParaDetalhes() {
  visao.value = 'detalhes';
}

function handleAguardarConfirmacao() {
  if (props.item) emit('aguardarConfirmacao', props.item.id);
}

function handleEnviarProblema() {
  if (props.item && motivoProblema.value) {
    emit('reportarProblema', props.item.id, motivoProblema.value);
    voltarParaDetalhes();
  }
}

function handleConfirmarDevolucao() {
  if (props.item && motivoDevolucao.value) {
    emit('devolverAFila', props.item.id, motivoDevolucao.value);
  }
}

function handleFinalizar() {
  if (props.item) emit('finalizar', props.item.id);
}
</script>

<template>
  <Modal :show="show" @close="fechar">
    <template #header>
      <div v-if="item" class="flex w-full items-center justify-between gap-3">
        <span class="flex items-center gap-2 truncate">
          <UserGroupIcon class="h-6 w-6 shrink-0 text-govbr-text" />
          {{ item.nome }}
        </span>

        <Button v-if="visao !== 'detalhes'" variant="primary" @click="voltarParaDetalhes">
          <ArrowLeftIcon class="h-5 w-5 ml-2" />
        </Button>
      </div>
    </template>

    <div v-if="item" class="space-y-4">
      <BaseModalDetails :item="item" :mostrar-descricao="visao === 'detalhes'">

        <div v-if="visao === 'detalhes' && item.estado === 'AGUARDANDO_CONFIRMACAO'" class="mt-6 space-y-2">
          <p class="font-semibold text-govbr-text">Finalizar Agendamento, o exame foi:</p>
          <div class="flex items-center gap-3">
            <Button variant="tertiary" @click="handleFinalizar">
              Confirmado
            </Button>
          </div>
        </div>

        <div v-else-if="visao === 'reportarProblema'" class="space-y-3 pt-2">
          <p class="font-semibold text-govbr-text text-[18px]">Informações sobre o Reporte de Problema:</p>
          <div>
            <label class="mb-1 block text-[16px] font-semibold text-govbr-text">Descreva qual o problema*</label>
            <SeletorMotivo v-model="motivoProblema" :opcoes="MOTIVOS_PROBLEMA" />
          </div>
        </div>

        <div v-else-if="visao === 'devolverAFila'" class="space-y-3 pt-2">
          <p class="font-semibold text-govbr-text text-[18px]">Informações sobre o Devolver à fila:</p>
          <div class="flex items-start gap-2 rounded bg-govbr-primary px-4 py-3 text-[16px] text-semibold text-white">
            <InformationCircleIcon class="mt-0.5 h-5 w-5 shrink-0" />
            <p>
              Utilize esta opção apenas para devolver a solicitação à fila geral. Para inconsistências nos dados
              ou erros no sistema, utilize a opção "Reportar Problema".
            </p>
          </div>
          <div>
            <label class="mb-1 block text-[16px] font-semibold text-govbr-text">Motivo*</label>
            <SeletorMotivo v-model="motivoDevolucao" :opcoes="MOTIVOS_DEVOLUCAO" />
          </div>
        </div>

      </BaseModalDetails>
    </div>

    <template #footer>
      <template v-if="visao === 'detalhes'">
        <Button
          v-if="item?.estado === 'EM_ANDAMENTO' || item?.estado === 'AGUARDANDO_CONFIRMACAO'"
          variant="tertiary"
          @click="visao = 'reportarProblema'"
        >
          Reportar Problema
        </Button>
        <Button variant="secondary" @click="fechar">
          Fechar
        </Button>
        <Button
          v-if="item?.estado === 'EM_ANDAMENTO'"
          variant="primary"
          @click="handleAguardarConfirmacao"
        >
          <ClockIcon class="h-5 w-5" />
          Aguardar confirmação do Paciente
        </Button>
      </template>

      <template v-else-if="visao === 'reportarProblema'">
        <Button variant="tertiary" @click="voltarParaDetalhes">
          Cancelar
        </Button>
        <Button
          variant="primary"
          :disabled="!motivoProblema"
          @click="handleEnviarProblema"
        >
          Enviar
        </Button>
      </template>

      <template v-else-if="visao === 'devolverAFila'">
        <Button
          variant="secondary"
          :disabled="!motivoDevolucao"
          @click="handleConfirmarDevolucao"
        >
          Confirmar devolução
        </Button>
        <Button variant="primary" @click="fechar">
          Fechar
        </Button>
      </template>
    </template>
  </Modal>
</template>
