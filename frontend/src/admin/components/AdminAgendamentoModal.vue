<script setup lang="ts">
import { ref, watch } from 'vue';
import {
  ClockIcon,
  ExclamationCircleIcon,
} from '@heroicons/vue/24/outline';
import { UserGroupIcon } from '@heroicons/vue/24/solid';
import Modal from '../../shared/components/Modal.vue';
import BaseModalDetails from '../../shared/components/BaseModalDetails.vue';
import SeletorMotivo from '../../shared/components/SeletorMotivo.vue';
import SeletorFuncionario from '../../shared/components/SeletorFuncionario.vue';
import { MOTIVOS_DEVOLUCAO } from '../../shared/constants';
import type { AgendamentoItem } from '../../funcionario/types';
import type { Funcionario } from '../types';
import Button from '../../shared/components/Button.vue';

type ItemModal = AgendamentoItem & {
  funcionarioAtribuido: string;
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
      <BaseModalDetails :item="item">
        <div v-if="item.problema_motivo" class="space-y-2 pt-2">
          <p class="font-semibold text-govbr-text">Informações sobre o Reporte do Problema:</p>
          <ul class="list-disc space-y-1 pl-5 text-[16px]">
            <li><span class="font-semibold text-govbr-text">Motivo</span>: <span class="text-govbr-text-secondary">{{ item.problema_motivo }}</span></li>
            <li v-if="item.problema_detalhes"><span class="font-semibold text-govbr-text">Detalhes</span>: <span class="text-govbr-text-secondary">{{ item.problema_detalhes }}</span></li>
          </ul>
        </div>

        <div v-if="painel === 'devolver'" class="space-y-3 rounded border border-govbr-border bg-govbr-bg p-4 mt-4">
          <label class="block text-sm font-semibold text-govbr-text">Motivo*</label>
          <SeletorMotivo v-model="motivoDevolucao" :opcoes="MOTIVOS_DEVOLUCAO" />
          <div class="flex items-center gap-2">
            <Button variant="secondary" @click="fecharPainel">
              Cancelar
            </Button>
            <Button variant="primary" :disabled="!motivoDevolucao" @click="confirmarDevolucao">
              Confirmar
            </Button>
          </div>
        </div>

        <div v-else-if="painel === 'reatribuir'" class="space-y-3 rounded border border-govbr-border bg-govbr-bg p-4 mt-4">
          <label class="block text-sm font-semibold text-govbr-text">Selecionar Funcionário</label>
          <SeletorFuncionario v-model="funcionarioSelecionado" :opcoes="funcionarios" />
          <div class="flex items-center gap-2">
            <Button variant="secondary" @click="fecharPainel">
              Cancelar
            </Button>
            <Button variant="primary" :disabled="!funcionarioSelecionado" @click="confirmarReatribuicao">
              Confirmar
            </Button>
          </div>
        </div>
      </BaseModalDetails>
    </div>

    <template #footer>
      <template v-if="permitirAcoes === false">
        <Button variant="primary" @click="fechar">Fechar</Button>
      </template>
      <template v-else-if="item?.problema_motivo">
        <Button variant="tertiary" @click="abrirPainel('devolver')">
          Devolver à fila
        </Button>
        <Button variant="secondary" @click="handleResolver">
          Remover
        </Button>
      </template>
      <template v-else>
        <Button variant="secondary" @click="abrirPainel('devolver')">
          <ClockIcon class="h-4 w-4" />
          Devolver à fila
        </Button>
        <Button variant="secondary" @click="abrirPainel('reatribuir')">
          <ExclamationCircleIcon class="h-4 w-4" />
          Reatribuir
        </Button>
        <Button variant="primary" @click="fechar">Fechar</Button>
      </template>
    </template>
  </Modal>
</template>
