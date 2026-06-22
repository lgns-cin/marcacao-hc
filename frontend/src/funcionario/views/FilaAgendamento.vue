<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'vue-toastification';
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/vue/24/outline';
import { useFuncionarioStore } from '../../stores/funcionario';
import PatientQueueCard from '../components/PatientQueueCard.vue';
import PatientDetailModal from '../components/PatientDetailModal.vue';
import FilaFiltros from '../components/FilaFiltros.vue';
import type { AgendamentoItem } from '../types';

const funcionarioStore = useFuncionarioStore();
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

async function puxarAgendamento(id: number) {
  try {
    await funcionarioStore.puxarAgendamento(id);
    toast.success('Paciente puxado para agendamento com sucesso.');
    modalAberto.value = false;
  } catch (error) {
    toast.error('Não foi possível puxar este agendamento.');
  }
}

async function carregarAgendamentos() {
  try {
    await funcionarioStore.fetchAgendamentos();
  } catch (error) {
    toast.error('Não foi possível carregar a fila de agendamento.');
  }
}

onMounted(() => {
  carregarAgendamentos();
});
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold text-govbr-text">Fila de Agendamento</h1>
    <p class="mt-1 text-govbr-text-secondary">Realize o filtro por tipo de exame e localização</p>

    <div class="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
      <div class="relative flex-1">
        <input
          :value="funcionarioStore.filtros.busca"
          type="text"
          placeholder="Busque por nome ou n° do prontuário"
          class="w-full rounded border border-govbr-border bg-white px-4 py-3 pr-10 text-sm placeholder-govbr-text-secondary focus:outline-none focus:ring-1 focus:ring-govbr-primary"
          @input="funcionarioStore.setBusca(($event.target as HTMLInputElement).value)"
        />
        <MagnifyingGlassIcon class="absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-govbr-primary" />
      </div>

      <button
        class="flex items-center justify-center gap-2 rounded-full bg-govbr-primary px-6 py-3 text-sm font-bold text-white hover:bg-govbr-primary-hover"
        @click="filtrosExpandidos = !filtrosExpandidos"
      >
        <FunnelIcon class="h-5 w-5" />
        {{ filtrosExpandidos ? 'Ocultar Filtros' : 'Expandir Filtros' }}
      </button>
    </div>

    <FilaFiltros
      v-if="filtrosExpandidos"
      :filtros="funcionarioStore.filtros"
      @aplicar="funcionarioStore.aplicarFiltros"
      @limpar="funcionarioStore.limparFiltros"
    />

    <p v-if="funcionarioStore.isLoading" class="mt-8 text-govbr-text-secondary">Carregando fila de agendamento...</p>

    <p v-else-if="funcionarioStore.agendamentosFiltrados.length === 0" class="mt-8 text-govbr-text-secondary">
      Nenhum paciente encontrado para os filtros selecionados.
    </p>

    <div v-else class="mt-6 grid gap-4 sm:grid-cols-2">
      <PatientQueueCard
        v-for="agendamento in funcionarioStore.agendamentosFiltrados"
        :key="agendamento.id"
        :agendamento="agendamento"
        @puxar="puxarAgendamento"
        @ver-mais="abrirDetalhes"
      />
    </div>

    <PatientDetailModal
      :show="modalAberto"
      :agendamento="agendamentoSelecionado"
      @close="fecharDetalhes"
      @puxar="puxarAgendamento"
    />
  </div>
</template>
