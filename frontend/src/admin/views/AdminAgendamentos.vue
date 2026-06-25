<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useToast } from 'vue-toastification';
import { MagnifyingGlassIcon, ClockIcon, CheckCircleIcon } from '@heroicons/vue/24/outline';
import { FunnelIcon } from '@heroicons/vue/20/solid';
import { useAdminStore } from '../../stores/admin';
import GerenciamentoCard from '../components/GerenciamentoCard.vue';
import AdminAgendamentoModal from '../components/AdminAgendamentoModal.vue';
import FilaFiltros from '../../funcionario/components/FilaFiltros.vue';
import type { AgendamentoGerenciamento } from '../types';

import Button from '../../shared/components/Button.vue';

const adminStore = useAdminStore();
const toast = useToast();

const abaAtiva = ref<'emAndamento' | 'concluido'>('emAndamento');
const filtrosExpandidos = ref(false);
const modalAberto = ref(false);
const itemSelecionado = ref<AgendamentoGerenciamento | null>(null);
const painelInicialModal = ref<'nenhum' | 'devolver'>('nenhum');

function abrirDetalhes(item: AgendamentoGerenciamento) {
  itemSelecionado.value = item;
  painelInicialModal.value = 'nenhum';
  modalAberto.value = true;
}

function abrirDevolverAFila(item: AgendamentoGerenciamento) {
  itemSelecionado.value = item;
  painelInicialModal.value = 'devolver';
  modalAberto.value = true;
}

function fecharDetalhes() {
  modalAberto.value = false;
}

async function carregarAgendamentos() {
  try {
    await adminStore.fetchAgendamentosGerenciamento();
  } catch (error) {
    toast.error('Não foi possível carregar os agendamentos.');
  }
}

async function carregarFuncionarios() {
  try {
    await adminStore.fetchFuncionarios();
  } catch (error) {
    toast.error('Não foi possível carregar a lista de funcionários.');
  }
}

async function devolverAFila(id: number, motivo: string) {
  try {
    await adminStore.devolverAFilaAdmin(id, motivo);
    toast.success('Solicitação devolvida à fila com sucesso.');
    modalAberto.value = false;
  } catch (error) {
    toast.error('Não foi possível devolver esta solicitação à fila.');
  }
}

async function reatribuir(id: number, funcionario: string) {
  try {
    await adminStore.reatribuirAgendamento(id, funcionario);
    toast.success('Solicitação reatribuída com sucesso.');
    modalAberto.value = false;
  } catch (error) {
    toast.error('Não foi possível reatribuir esta solicitação.');
  }
}

const INTERVALO_ATUALIZACAO_MS = 10000;
let intervaloAtualizacao: ReturnType<typeof setInterval> | undefined;

onMounted(() => {
  carregarAgendamentos();
  carregarFuncionarios();
  intervaloAtualizacao = setInterval(() => {
    if (!modalAberto.value) adminStore.fetchAgendamentosGerenciamento({ silencioso: true });
  }, INTERVALO_ATUALIZACAO_MS);
});

onUnmounted(() => {
  clearInterval(intervaloAtualizacao);
});
</script>

<template>
  <div>
    <h1 class="text-[2.4rem] text-govbr-text">Gerenciamento de Agendamentos</h1>
    <p class="text-[1.6rem] text-govbr-text-secondary">
      Visualize os exames em andamento e finalizados, acompanhando os responsáveis por cada etapa.
    </p>

    <div class="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="relative w-2/3">
        <input
          :value="adminStore.filtrosAgendamentos.busca"
          type="text"
          placeholder="Busque por nome ou n° do prontuário"
          class="w-full rounded bg-[#F8F8F8] px-4 py-3 pr-10 text-[14px] placeholder-govbr-text-secondary focus:outline-none focus:ring-1 focus:ring-govbr-primary"
          @input="adminStore.setBuscaAgendamentos(($event.target as HTMLInputElement).value)"
        />
        <MagnifyingGlassIcon class="absolute right-3 top-1/2 h-5 w-5 stroke-3 -translate-y-1/2 text-govbr-primary" />
      </div>

      <Button
        type="button"
        variant="primary"
        @click="filtrosExpandidos = !filtrosExpandidos"
      >
        <FunnelIcon class="h-5 w-5" />
        {{ filtrosExpandidos ? 'Ocultar Filtros' : 'Expandir Filtros' }}
      </Button>
    </div>

    <FilaFiltros
      v-if="filtrosExpandidos"
      :filtros="adminStore.filtrosAgendamentos"
      @aplicar="adminStore.aplicarFiltrosAgendamentos"
      @limpar="adminStore.limparFiltrosAgendamentos"
    />

    <div class="mt-6 flex items-center gap-6 border-b border-govbr-border">
      <Button
        variant="tertiary"
        @click="abaAtiva = 'emAndamento'"
      >
        <ClockIcon class="h-5 w-5" />
        Em andamento
      </Button>
      <Button
        variant="tertiary"
        @click="abaAtiva = 'concluido'"
      >
        <CheckCircleIcon class="h-5 w-5" />
        Finalizados
      </Button>
    </div>

    <p v-if="adminStore.isLoadingAgendamentos" class="mt-8 text-govbr-text-secondary">Carregando agendamentos...</p>

    <template v-else-if="abaAtiva === 'emAndamento'">
      <p v-if="adminStore.agendamentosEmAndamentoFiltrados.length === 0" class="mt-8 text-govbr-text-secondary">
        Nenhum agendamento em andamento encontrado.
      </p>
      <div v-else class="mt-6 grid gap-4 sm:grid-cols-2">
        <GerenciamentoCard
          v-for="item in adminStore.agendamentosEmAndamentoFiltrados"
          :key="item.id"
          :item="item"
          @ver-mais="abrirDetalhes"
          @devolver-a-fila="abrirDevolverAFila"
        />
      </div>
    </template>

    <template v-else>
      <p v-if="adminStore.agendamentosConcluidosFiltrados.length === 0" class="mt-8 text-govbr-text-secondary">
        Nenhum agendamento concluído encontrado.
      </p>
      <div v-else class="mt-6 grid gap-4 sm:grid-cols-2">
        <GerenciamentoCard
          v-for="item in adminStore.agendamentosConcluidosFiltrados"
          :key="item.id"
          :item="item"
          @ver-mais="abrirDetalhes"
          @devolver-a-fila="abrirDevolverAFila"
        />
      </div>
    </template>

    <AdminAgendamentoModal
      :show="modalAberto"
      :item="itemSelecionado"
      :funcionarios="adminStore.funcionarios"
      :permitir-acoes="itemSelecionado?.estado !== 'CONFIRMADO' && itemSelecionado?.estado !== 'PROBLEMA_REPORTADO'"
      :painel-inicial="painelInicialModal"
      @close="fecharDetalhes"
      @devolver="devolverAFila"
      @reatribuir="reatribuir"
    />
  </div>
</template>
