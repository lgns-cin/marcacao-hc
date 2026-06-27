<script setup lang="ts">
import { ref } from 'vue';
import {
  ExclamationTriangleIcon,
  ArrowUturnLeftIcon,
  ArrowsRightLeftIcon,
} from '@heroicons/vue/24/outline';
import { TrashIcon, UserGroupIcon } from '@heroicons/vue/20/solid';
import Button from '../../shared/components/Button.vue';
import SeletorMotivo from '../../shared/components/SeletorMotivo.vue';
import SeletorFuncionario from '../../shared/components/SeletorFuncionario.vue';
import { nomeDoCodigo } from '../../shared/utils/catalogoExames';
import { MOTIVOS_DEVOLUCAO } from '../../shared/constants';
import type { PendenciaItem, Funcionario } from '../types';

const props = defineProps<{
  pendencia: PendenciaItem;
  funcionarios: Funcionario[];
}>();

const emit = defineEmits<{
  remover: [id: number];
  devolver: [id: number, motivo: string];
  reatribuir: [id: number, funcionario: string];
  verMais: [pendencia: PendenciaItem];
}>();

// Painel de ação expandido inline no próprio card (sem abrir modal — menos cliques).
type Painel = 'nenhum' | 'devolver' | 'reatribuir';
const painel = ref<Painel>('nenhum');
const motivoDevolucao = ref('');
const funcionarioSelecionado = ref('');

function abrirPainel(novo: Painel) {
  painel.value = painel.value === novo ? 'nenhum' : novo;
  motivoDevolucao.value = '';
  funcionarioSelecionado.value = '';
}

function fecharPainel() {
  painel.value = 'nenhum';
}

function confirmarDevolucao() {
  if (motivoDevolucao.value) emit('devolver', props.pendencia.id, motivoDevolucao.value);
}

function confirmarReatribuicao() {
  if (funcionarioSelecionado.value) emit('reatribuir', props.pendencia.id, funcionarioSelecionado.value);
}

// Só mostra a linha de detalhes quando ela acrescenta algo ao motivo.
function temDetalhesExtras(p: PendenciaItem): boolean {
  return !!p.problema_detalhes && p.problema_detalhes !== p.problema_motivo;
}
</script>

<template>
  <div class="flex flex-col rounded-lg bg-white p-5 shadow-[0_0_7.6px_rgba(0,0,0,0.15)] transition-shadow hover:shadow-xl">
    <!-- Cabeçalho: paciente + situação -->
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-center gap-2">
        <UserGroupIcon class="h-6 w-6 shrink-0 text-govbr-text" />
        <h3 class="text-lg font-bold text-govbr-text">{{ pendencia.nome }}</h3>
      </div>
      <!-- 
      <span
        class="inline-flex shrink-0 items-center gap-1 whitespace-nowrap rounded-full px-3 py-1 text-xs font-bold"
        :class="pendencia.situacao === 'BLOQUEADO'
          ? 'bg-govbr-error-bg text-govbr-error'
          : 'bg-amber-100 text-amber-800'"
      >
        <component :is="pendencia.situacao === 'BLOQUEADO' ? LockClosedIcon : ClockIcon" class="h-3.5 w-3.5" />
        {{ pendencia.situacao === 'BLOQUEADO' ? 'Bloqueado' : 'Parado' }}
      </span>
      -->
    </div>

    <!-- Identificação secundária -->
    <p class="mt-1 text-sm text-govbr-text-secondary">
      Prontuário {{ pendencia.prontuario }} · {{ nomeDoCodigo(pendencia.exame) }} · há {{ pendencia.diasNaFila }}d
    </p>

    <!-- O PROBLEMA EM DESTAQUE — visível sem nenhum clique -->
    <div class="mt-3 flex items-start gap-2 rounded-md border-l-4 border-govbr-error bg-govbr-error-bg px-3 py-2.5">
      <ExclamationTriangleIcon class="mt-0.5 h-5 w-5 shrink-0 text-govbr-error" />
      <div class="min-w-0">
        <p class="text-sm font-bold text-govbr-text">{{ pendencia.problema_motivo || 'Problema não especificado' }}</p>
        <p v-if="temDetalhesExtras(pendencia)" class="mt-0.5 text-xs text-govbr-text-secondary">
          {{ pendencia.problema_detalhes }}
        </p>
      </div>
    </div>

    <!-- Responsável -->
    <p class="mt-3 text-sm text-govbr-text">
      <span class="font-semibold">Responsável: </span>
      <span class="text-govbr-text-secondary"> {{ pendencia.responsavel }}</span>
    </p>

    <!-- Painel inline de devolução -->
    <div v-if="painel === 'devolver'" class="mt-3 space-y-3 rounded border border-govbr-border bg-govbr-bg p-3">
      <label class="block text-sm font-semibold text-govbr-text">Motivo da devolução*</label>
      <SeletorMotivo v-model="motivoDevolucao" :opcoes="MOTIVOS_DEVOLUCAO" />
      <div class="flex items-center gap-2">
        <Button variant="secondary" @click="fecharPainel">Cancelar</Button>
        <Button variant="primary" :disabled="!motivoDevolucao" @click="confirmarDevolucao">Confirmar</Button>
      </div>
    </div>

    <!-- Painel inline de reatribuição -->
    <div v-else-if="painel === 'reatribuir'" class="mt-3 space-y-3 rounded border border-govbr-border bg-govbr-bg p-3">
      <label class="block text-sm font-semibold text-govbr-text">Reatribuir para</label>
      <SeletorFuncionario v-model="funcionarioSelecionado" :opcoes="funcionarios" />
      <div class="flex items-center gap-2">
        <Button variant="secondary" @click="fecharPainel">Cancelar</Button>
        <Button variant="primary" :disabled="!funcionarioSelecionado" @click="confirmarReatribuicao">Confirmar</Button>
      </div>
    </div>

    <!-- Ações diretas no card -->
    <div class="mt-4 flex flex-wrap items-center gap-4">
      <Button variant="primary" @click="emit('remover', pendencia.id)">
        <TrashIcon class="h-4 w-4" />
        Remover
      </Button>
      <Button variant="secondary" @click="abrirPainel('devolver')">
        <ArrowUturnLeftIcon class="h-4 w-4" />
        Devolver à fila
      </Button>
      <Button variant="secondary" @click="abrirPainel('reatribuir')">
        <ArrowsRightLeftIcon class="h-4 w-4" />
        Reatribuir
      </Button>
    </div>
  </div>
</template>
