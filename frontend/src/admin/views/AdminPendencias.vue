<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useToast } from 'vue-toastification';
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/vue/24/outline';
import { useAdminStore } from '../../stores/admin';
import PendenciaCard from '../components/PendenciaCard.vue';
import AdminAgendamentoModal from '../components/AdminAgendamentoModal.vue';
import FilaFiltros from '../../funcionario/components/FilaFiltros.vue';
import type { PendenciaItem } from '../types';
import Button from '../../shared/components/Button.vue';

const adminStore = useAdminStore();
const toast = useToast();

const filtrosExpandidos = ref(false);
const modalAberto = ref(false);
const pendenciaSelecionada = ref<PendenciaItem | null>(null);

function abrirDetalhes(pendencia: PendenciaItem) {
  pendenciaSelecionada.value = pendencia;
  modalAberto.value = true;
}

function fecharDetalhes() {
  modalAberto.value = false;
}

async function carregarPendencias() {
  try {
    await adminStore.fetchPendencias();
  } catch (error) {
    toast.error('Não foi possível carregar as pendências.');
  }
}

async function carregarFuncionarios() {
  try {
    await adminStore.fetchFuncionarios();
  } catch (error) {
    toast.error('Não foi possível carregar a lista de funcionários.');
  }
}

async function resolverPendencia(id: number) {
  try {
    await adminStore.resolverPendencia(id);
    toast.success('Pendência resolvida com sucesso.');
    modalAberto.value = false;
  } catch (error) {
    toast.error('Não foi possível resolver esta pendência.');
  }
}

async function devolverAFila(id: number, motivo: string) {
  try {
    await adminStore.devolverAFilaAdmin(id, motivo);
    toast.success('Solicitação devolvida à fila com sucesso.');
    modalAberto.value = false;
    await carregarPendencias();
  } catch (error) {
    toast.error('Não foi possível devolver esta solicitação à fila.');
  }
}

async function reatribuir(id: number, funcionario: string) {
  try {
    await adminStore.reatribuirAgendamento(id, funcionario);
    toast.success('Solicitação reatribuída com sucesso.');
    modalAberto.value = false;
    await carregarPendencias();
  } catch (error) {
    toast.error('Não foi possível reatribuir esta solicitação.');
  }
}

const INTERVALO_ATUALIZACAO_MS = 10000;
let intervaloAtualizacao: ReturnType<typeof setInterval> | undefined;

onMounted(() => {
  carregarPendencias();
  carregarFuncionarios();
  intervaloAtualizacao = setInterval(() => {
    if (!modalAberto.value) adminStore.fetchPendencias({ silencioso: true });
  }, INTERVALO_ATUALIZACAO_MS);
});

onUnmounted(() => {
  clearInterval(intervaloAtualizacao);
});
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold text-govbr-text">Gestão de Pendências</h1>
    <p class="mt-1 text-govbr-text-secondary">Acompanhe casos que exigem intervenção para evitar atrasos no atendimento</p>

    <div class="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
      <div class="relative flex-1">
        <input
          :value="adminStore.filtrosPendencias.busca"
          type="text"
          placeholder="Busque por nome ou n° do prontuário"
          class="w-full rounded border border-govbr-border bg-white px-4 py-3 pr-10 text-sm placeholder-govbr-text-secondary focus:outline-none focus:ring-1 focus:ring-govbr-primary"
          @input="adminStore.setBuscaPendencias(($event.target as HTMLInputElement).value)"
        />
        <MagnifyingGlassIcon class="absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-govbr-primary" />
      </div>

      <Button
        variant="primary"
        @click="filtrosExpandidos = !filtrosExpandidos"
      >
        <FunnelIcon class="h-5 w-5" />
        {{ filtrosExpandidos ? 'Ocultar Filtros' : 'Expandir Filtros' }}
      </Button>
    </div>

    <FilaFiltros
      v-if="filtrosExpandidos"
      :filtros="adminStore.filtrosPendencias"
      @aplicar="adminStore.aplicarFiltrosPendencias"
      @limpar="adminStore.limparFiltrosPendencias"
    />

    <p v-if="adminStore.isLoadingPendencias" class="mt-8 text-govbr-text-secondary">Carregando pendências...</p>

    <p v-else-if="adminStore.pendenciasFiltradas.length === 0" class="mt-8 text-govbr-text-secondary">
      Nenhuma pendência encontrada para os filtros selecionados.
    </p>

    <div v-else class="mt-6 grid gap-4 sm:grid-cols-2">
      <PendenciaCard
        v-for="pendencia in adminStore.pendenciasFiltradas"
        :key="pendencia.id"
        :pendencia="pendencia"
        @ver-mais="abrirDetalhes"
      />
    </div>

    <AdminAgendamentoModal
      :show="modalAberto"
      :item="pendenciaSelecionada"
      :funcionarios="adminStore.funcionarios"
      @close="fecharDetalhes"
      @resolver="resolverPendencia"
      @devolver="devolverAFila"
      @reatribuir="reatribuir"
    />
  </div>
</template>
