<script setup lang="ts">
import { ref, watch } from 'vue';
import {
  UserGroupIcon,
  ClockIcon,
  CheckIcon,
  XMarkIcon,
  ExclamationCircleIcon,
} from '@heroicons/vue/24/outline';
import Modal from '../../shared/components/Modal.vue';
import SeletorMotivo from '../../funcionario/components/SeletorMotivo.vue';
import SeletorFuncionario from './SeletorFuncionario.vue';
import { MOTIVOS_DEVOLUCAO } from '../../funcionario/types';
import type { AgendamentoItem } from '../../funcionario/types';
import type { Funcionario } from '../types';

type ItemModal = AgendamentoItem & {
  responsavel: string;
  problema_motivo?: string | null;
  problema_detalhes?: string | null;
};

type Painel = 'nenhum' | 'devolver' | 'reatribuir';

const props = defineProps<{
  show: boolean;
  item: ItemModal | null;
  funcionarios: Funcionario[];
  permitirAcoes?: boolean;
  painelInicial?: Painel;
}>();

const emit = defineEmits<{
  close: [];
  resolver: [id: number];
  devolver: [id: number, motivo: string];
  reatribuir: [id: number, funcionario: string];
}>();

const painel = ref<Painel>('nenhum');
const motivoDevolucao = ref('');
const funcionarioSelecionado = ref('');

watch(
  () => props.show,
  (aberto) => {
    if (aberto) {
      painel.value = props.painelInicial ?? 'nenhum';
      motivoDevolucao.value = '';
      funcionarioSelecionado.value = '';
    }
  }
);

function fechar() {
  emit('close');
}

function abrirPainel(novoPainel: Painel) {
  painel.value = novoPainel;
}

function fecharPainel() {
  painel.value = 'nenhum';
}

function confirmarDevolucao() {
  if (props.item && motivoDevolucao.value) {
    emit('devolver', props.item.id, motivoDevolucao.value);
  }
}

function confirmarReatribuicao() {
  if (props.item && funcionarioSelecionado.value) {
    emit('reatribuir', props.item.id, funcionarioSelecionado.value);
  }
}

function handleResolver() {
  if (props.item) emit('resolver', props.item.id);
}
</script>

<template>
  <Modal :show="show" @close="fechar">
    <template #header>
      <span v-if="item" class="flex items-center gap-2">
        <UserGroupIcon class="h-6 w-6 text-govbr-text" />
        {{ item.nome }}
      </span>
    </template>

    <div v-if="item" class="space-y-4">
      <p class="text-sm">
        <span class="font-semibold text-govbr-text">Responsável</span>:
        <span class="text-govbr-text-secondary">{{ item.responsavel }}</span>
      </p>

      <div class="flex flex-wrap items-center justify-between gap-2">
        <p class="text-sm text-govbr-text-secondary">
          N° do Prontuário: <span class="text-govbr-text">{{ item.prontuario }}</span>
        </p>
        <div class="flex items-center gap-2">
          <span class="flex items-center gap-1 text-sm text-govbr-text-secondary">
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

      <!-- Problema reportado (somente leitura) -->
      <div v-if="item.problema_motivo" class="space-y-2">
        <p class="font-semibold text-govbr-text">Informações sobre o Reporte do Problema:</p>
        <ul class="list-disc space-y-1 pl-5 text-sm">
          <li><span class="font-semibold text-govbr-text">Motivo</span>: <span class="text-govbr-text-secondary">{{ item.problema_motivo }}</span></li>
          <li v-if="item.problema_detalhes"><span class="font-semibold text-govbr-text">Detalhes</span>: <span class="text-govbr-text-secondary">{{ item.problema_detalhes }}</span></li>
        </ul>
      </div>

      <!-- Painel: Devolver à fila -->
      <div v-else-if="painel === 'devolver'" class="space-y-2 rounded border border-govbr-border bg-govbr-bg p-4">
        <label class="mb-1 block text-sm font-semibold text-govbr-text">Motivo*</label>
        <div class="flex items-center gap-2">
          <div class="flex-1">
            <SeletorMotivo v-model="motivoDevolucao" :opcoes="MOTIVOS_DEVOLUCAO" />
          </div>
          <button
            class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-govbr-error text-govbr-error hover:bg-govbr-error-bg"
            @click="fecharPainel"
          >
            <XMarkIcon class="h-5 w-5" />
          </button>
          <button
            class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-govbr-success text-govbr-success hover:bg-green-50 disabled:cursor-not-allowed disabled:opacity-40"
            :disabled="!motivoDevolucao"
            @click="confirmarDevolucao"
          >
            <CheckIcon class="h-5 w-5" />
          </button>
        </div>
      </div>

      <!-- Painel: Reatribuir -->
      <div v-else-if="painel === 'reatribuir'" class="space-y-2 rounded border border-govbr-border bg-govbr-bg p-4">
        <label class="mb-1 block text-sm font-semibold text-govbr-text">Selecionar Funcionário</label>
        <div class="flex items-center gap-2">
          <div class="flex-1">
            <SeletorFuncionario v-model="funcionarioSelecionado" :opcoes="funcionarios" />
          </div>
          <button
            class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-govbr-error text-govbr-error hover:bg-govbr-error-bg"
            @click="fecharPainel"
          >
            <XMarkIcon class="h-5 w-5" />
          </button>
          <button
            class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-govbr-success text-govbr-success hover:bg-green-50 disabled:cursor-not-allowed disabled:opacity-40"
            :disabled="!funcionarioSelecionado"
            @click="confirmarReatribuicao"
          >
            <CheckIcon class="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>

    <template #footer>
      <template v-if="item?.problema_motivo">
        <button
          class="rounded-full border border-govbr-primary px-5 py-2 text-sm font-bold text-govbr-primary hover:bg-govbr-bg"
          @click="fechar"
        >
          Fechar
        </button>
        <button
          class="flex items-center gap-2 rounded-full bg-govbr-primary px-5 py-2 text-sm font-bold text-white hover:bg-govbr-primary-hover"
          @click="handleResolver"
        >
          <CheckIcon class="h-5 w-5" />
          Resolvido
        </button>
      </template>
      <template v-else-if="permitirAcoes === false">
        <button
          class="rounded-full bg-govbr-primary px-5 py-2 text-sm font-bold text-white hover:bg-govbr-primary-hover"
          @click="fechar"
        >
          Fechar
        </button>
      </template>
      <template v-else>
        <button
          class="mr-auto flex items-center gap-1 text-sm font-bold text-govbr-primary hover:underline"
          @click="abrirPainel('devolver')"
        >
          <ClockIcon class="h-4 w-4" />
          Devolver à fila
        </button>
        <button
          class="flex items-center gap-1 rounded-full border border-govbr-primary px-5 py-2 text-sm font-bold text-govbr-primary hover:bg-govbr-bg"
          @click="abrirPainel('reatribuir')"
        >
          <ExclamationCircleIcon class="h-4 w-4" />
          Reatribuir
        </button>
        <button
          class="rounded-full bg-govbr-primary px-5 py-2 text-sm font-bold text-white hover:bg-govbr-primary-hover"
          @click="fechar"
        >
          Fechar
        </button>
      </template>
    </template>
  </Modal>
</template>
