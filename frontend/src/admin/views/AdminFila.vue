<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useToast } from 'vue-toastification';
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/vue/24/outline';
import { useAdminStore } from '../../stores/admin';
import AdminFilaCard from '../components/AdminFilaCard.vue';
import AdminFilaDetailModal from '../components/AdminFilaDetailModal.vue';
import FilaFiltros from '../../funcionario/components/FilaFiltros.vue';
import type { AgendamentoItem } from '../../funcionario/types';
import Button from '../../shared/components/Button.vue';

const adminStore = useAdminStore();
const toast = useToast();

const filtrosExpandidos = ref(false);
const modalAberto = ref(false);
const agendamentoSelecionado = ref<AgendamentoItem | null>(null);

function abrirDetalhes(agendamento: AgendamentoItem) {
  agendamentoSelecionado.value = agendamento;
  modalAberto.value = true;
}

function fecharDetalhes() {
  modalAberto.value = false;
}

async function carregarFila() {
  try {
    await adminStore.fetchFila();
  } catch (error) {
    toast.error('Não foi possível carregar a fila de agendamento.');
  }
}

const INTERVALO_ATUALIZACAO_MS = 10000;
let intervaloAtualizacao: ReturnType<typeof setInterval> | undefined;

onMounted(() => {
  carregarFila();
  intervaloAtualizacao = setInterval(() => {
    if (!modalAberto.value) adminStore.fetchFila({ silencioso: true });
  }, INTERVALO_ATUALIZACAO_MS);
});

onUnmounted(() => {
  clearInterval(intervaloAtualizacao);
});
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold text-govbr-text">Fila de Agendamento</h1>
    <p class="mt-1 text-govbr-text-secondary">Realize o filtro por tipo de exame e localização</p>

    <div class="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
      <div class="relative flex-1">
        <input
          :value="adminStore.filtrosFila.busca"
          type="text"
          placeholder="Busque por nome ou n° do prontuário"
          class="w-full rounded border border-govbr-border bg-white px-4 py-3 pr-10 text-sm placeholder-govbr-text-secondary focus:outline-none focus:ring-1 focus:ring-govbr-primary"
          @input="adminStore.setBuscaFila(($event.target as HTMLInputElement).value)"
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
      :filtros="adminStore.filtrosFila"
      @aplicar="adminStore.aplicarFiltrosFila"
      @limpar="adminStore.limparFiltrosFila"
    />

    <p v-if="adminStore.isLoadingFila" class="mt-8 text-govbr-text-secondary">Carregando fila de agendamento...</p>

    <p v-else-if="adminStore.filaFiltrada.length === 0" class="mt-8 text-govbr-text-secondary">
      Nenhum paciente encontrado para os filtros selecionados.
    </p>

    <div v-else class="mt-6 grid gap-4 sm:grid-cols-2">
      <AdminFilaCard
        v-for="agendamento in adminStore.filaFiltrada"
        :key="agendamento.id"
        :agendamento="agendamento"
        @ver-mais="abrirDetalhes"
      />
    </div>

    <AdminFilaDetailModal
      :show="modalAberto"
      :agendamento="agendamentoSelecionado"
      @close="fecharDetalhes"
    />
  </div>
</template>
