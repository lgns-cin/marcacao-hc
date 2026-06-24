<script setup lang="ts">
import { ref, watch } from 'vue';
import {
  ClockIcon,
  ArrowLeftIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
} from '@heroicons/vue/24/outline';
import { UserGroupIcon } from '@heroicons/vue/20/solid';
import Modal from '../../shared/components/Modal.vue';
import SeletorMotivo from './SeletorMotivo.vue';
import { MOTIVOS_DEVOLUCAO, MOTIVOS_PROBLEMA } from '../types';
import type { MinhaAreaItem, ResultadoFinalizacao } from '../types';
import GovButton from '../../shared/components/GovButton.vue';

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
  finalizar: [id: number, resultado: ResultadoFinalizacao];
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

function handleFinalizar(resultado: ResultadoFinalizacao) {
  if (props.item) emit('finalizar', props.item.id, resultado);
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

        <GovButton
          v-if="visao === 'detalhes' && item.estado === 'AGUARDANDO_CONFIRMACAO'"
          variant="tertiary"
          @click="visao = 'reportarProblema'"
        >
          Reportar Problema
        </GovButton>

        <GovButton v-else-if="visao !== 'detalhes'" variant="primary" @click="voltarParaDetalhes">
          <ArrowLeftIcon class="h-5 w-5" />
          Voltar
        </GovButton>
      </div>
    </template>

    <div v-if="item" class="space-y-4">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <p class="text-[16px] text-govbr-text-secondary">
          N° do Prontuário: <span class="text-govbr-text">{{ item.prontuario }}</span>
        </p>
        <div v-if="item.estado !== 'FINALIZADO'" class="flex items-center gap-2">
          <span class="flex items-center gap-1 text-[16px] text-govbr-text-secondary">
            <ClockIcon class="h-4 w-4" />
            há {{ item.diasNaFila }}d
          </span>
          <span :class="[
            'rounded-full px-2.5 py-0.5 text-xs font-bold',
            item.status === 'ALTA' ? 'bg-govbr-error-bg text-govbr-error' :
            item.status === 'MÉDIA' ? 'bg-amber-100 text-amber-800' :
            'bg-green-100 text-green-800'
          ]">
            {{ item.status }}
          </span>
        </div>
        <span v-else class="rounded-full border border-govbr-border px-2.5 py-0.5 text-xs font-bold text-govbr-text-secondary">
          {{ item.resultado }}
        </span>
      </div>

      <div class="flex flex-wrap gap-2">
        <span
          v-for="exame in item.exames"
          :key="exame"
          class="rounded border border-govbr-border px-3 py-1 text-sm font-semibold text-govbr-text"
        >
          {{ exame }}
        </span>
      </div>

      <!-- Detalhes do agendamento -->
      <dl v-if="visao === 'detalhes'" class="space-y-3 text-[16px]">
        <div>
          <dt class="inline font-semibold text-govbr-text">Unidade Executora: </dt>
          <dd class="inline text-govbr-text-secondary"> {{ item.unidadeExecutora }}</dd>
        </div>
        <div>
          <dt class="inline font-semibold text-govbr-text">Unidade Solicitante: </dt>
          <dd class="inline text-govbr-text-secondary"> {{ item.unidadeSolicitante }}</dd>
        </div>
        <div>
          <dt class="inline font-semibold text-govbr-text">Data de retorno: </dt>
          <dd class="inline text-govbr-text-secondary"> {{ item.dataRetorno }}</dd>
        </div>
        <div>
          <dt class="inline font-semibold text-govbr-text">Localização: </dt>
          <dd class="inline text-govbr-text-secondary"> {{ item.localizacao }}</dd>
        </div>
        <div>
          <dt class="inline font-semibold text-govbr-text">Idade: </dt>
          <dd class="inline text-govbr-text-secondary"> {{ item.idade }} anos</dd>
        </div>

        <div v-if="item.estado === 'AGUARDANDO_CONFIRMACAO'" class="mt-6 space-y-2">
          <p class="font-semibold text-govbr-text">Finalizar Agendamento, o exame foi:</p>
          <div class="flex items-center gap-3">
            <GovButton variant="tertiary" @click="handleFinalizar('CONFIRMADO')">
              Confirmado
            </GovButton>
            <GovButton variant="tertiary" @click="handleFinalizar('CANCELADO')">
              Cancelado
            </GovButton>
          </div>
        </div>
      </dl>

      <!-- Reportar Problema -->
      <div v-else-if="visao === 'reportarProblema'" class="space-y-3">
        <p class="font-semibold text-govbr-text">Informações sobre o Reporte de Problema:</p>
        <div>
          <label class="mb-1 block text-sm font-semibold text-govbr-text">Descreva qual o problema*</label>
          <SeletorMotivo v-model="motivoProblema" :opcoes="MOTIVOS_PROBLEMA" />
        </div>
      </div>

      <!-- Devolver à fila -->
      <div v-else-if="visao === 'devolverAFila'" class="space-y-3">
        <p class="font-semibold text-govbr-text">Informações sobre o Devolver à fila:</p>
        <div class="flex items-start gap-2 rounded bg-govbr-primary px-4 py-3 text-sm text-white">
          <InformationCircleIcon class="mt-0.5 h-5 w-5 shrink-0" />
          <p>
            Utilize esta opção apenas para devolver a solicitação à fila geral. Para inconsistências nos dados
            ou erros no sistema, utilize a opção "Reportar Problema".
          </p>
        </div>
        <div>
          <label class="mb-1 block text-sm font-semibold text-govbr-text">Motivo*</label>
          <SeletorMotivo v-model="motivoDevolucao" :opcoes="MOTIVOS_DEVOLUCAO" />
        </div>
      </div>
    </div>

    <template #footer>
      <template v-if="visao === 'detalhes'">
        <GovButton
          v-if="item?.estado === 'EM_ANDAMENTO'"
          variant="tertiary"
          @click="visao = 'reportarProblema'"
        >
          Reportar Problema
        </GovButton>
        <GovButton
          variant="secondary"
          @click="fechar"
        >
          Fechar
        </GovButton>
        <GovButton
          v-if="item?.estado === 'EM_ANDAMENTO'"
          variant="primary"
          @click="handleAguardarConfirmacao"
        >
          <ClockIcon class="h-5 w-5" />
          Aguardar confirmação do Paciente
        </GovButton>
      </template>

      <template v-else-if="visao === 'reportarProblema'">
        <GovButton
          variant="tertiary"
          @click="voltarParaDetalhes"
        >
          Cancelar
        </GovButton>
        <GovButton
          variant="primary"
          :disabled="!motivoProblema"
          @click="handleEnviarProblema"
        >
          Enviar
        </GovButton>
      </template>

      <template v-else-if="visao === 'devolverAFila'">
        <GovButton
          variant="secondary"
          :disabled="!motivoDevolucao"
          @click="handleConfirmarDevolucao"
        >
          Confirmar devolução
        </GovButton>
        <GovButton
          variant="primary"
          @click="fechar"
        >
          Fechar
        </GovButton>
      </template>
    </template>
  </Modal>
</template>
