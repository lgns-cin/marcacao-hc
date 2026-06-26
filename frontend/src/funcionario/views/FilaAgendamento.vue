<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useToast } from 'vue-toastification';
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline';
import { FunnelIcon } from '@heroicons/vue/20/solid';
import { useFuncionarioStore } from '../../stores/funcionario';
import PatientQueueCard from '../components/PatientQueueCard.vue';
import PatientDetailModal from '../components/PatientDetailModal.vue';
import FilaFiltros from '../components/FilaFiltros.vue';
import type { AgendamentoItem } from '../types';
import Button from '../../shared/components/Button.vue';

// Plugins e stores
const funcionarioStore = useFuncionarioStore();
const toast = useToast();

// estados reativos
const filtrosExpandidos = ref(false);             // Controla a visibilidade do painel de filtros
const modalAberto = ref(false);                   // Controla a abertura/fechamento do modal de detalhes
const agendamentoSelecionado = ref<AgendamentoItem | null>(null); // Armazena o paciente clicado para ver detalhes

// manipulação do modal
function abrirDetalhes(agendamento: AgendamentoItem) {
  agendamentoSelecionado.value = agendamento; // Salva o registro clicado
  modalAberto.value = true;                    // Abre a janela do modal
}

function fecharDetalhes() {
  modalAberto.value = false; // Fecha a janela do modal
}

async function puxarAgendamento(id: number) {
  const statusCode = await funcionarioStore.puxarAgendamento(id);

  if (statusCode == 200) {
    toast.success('Paciente puxado para agendamento com sucesso.');
  } else if (statusCode == 409) {
    toast.error('Este paciente já foi atribuído a outro atendente.');
  } else {
    toast.error('Não foi possível puxar este agendamento.');
  }

  modalAberto.value = false;
  await carregarAgendamentos();
}

async function carregarAgendamentos() {
  const successful = await funcionarioStore.fetchAgendamentos();
  if (!successful) {
    toast.error('Não foi possível carregar a fila de agendamento.');
  }
}

// Atualização em segundo plano
const INTERVALO_ATUALIZACAO_MS = 10000;
let intervaloAtualizacao: ReturnType<typeof setInterval> | undefined;

async function atualizarEmSegundoPlano() {
  // Se o usuário estiver trabalhando com o modal aberto, não atualiza para não sumir com o dado na tela dele
  if (modalAberto.value) return;
  try {
    // Executa a busca em modo silencioso (sem disparar telas de loading/espinners pesados)
    await funcionarioStore.fetchAgendamentos({ silencioso: true });
  } catch (error) {
    // Falha silenciosa: a próxima rodada de polling tenta novamente automaticamente.
  }
}

// Ciclo de vida do componente
onMounted(() => {
  carregarAgendamentos(); // Busca os dados assim que o componente entra na tela
  // Inicia o contador cíclico para atualizações automatizadas
  intervaloAtualizacao = setInterval(atualizarEmSegundoPlano, INTERVALO_ATUALIZACAO_MS);
});

onUnmounted(() => {
  // Limpa o temporizador da memória quando o usuário muda de página, evitando vazamento de memória (memory leaks)
  clearInterval(intervaloAtualizacao);
});
</script>

<template>
  <div>
    <h1 class="text-[2.4rem] text-govbr-text">Fila de Agendamento</h1>
    <p class="text-[1.6rem] text-govbr-text-secondary">Realize o filtro por tipo de exame e localização</p>

    <div class="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      
      <div class="relative w-2/3">
        <input
          :value="funcionarioStore.filtros.busca"
          type="text"
          placeholder="Busque por nome ou n° do prontuário"
          class="w-full rounded bg-[#F8F8F8] px-4 py-3 pr-10 text-[14px] placeholder-govbr-text-secondary focus:outline-none focus:ring-1 focus:ring-govbr-primary"
          @input="funcionarioStore.setBusca(($event.target as HTMLInputElement).value)"
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
      :filtros="funcionarioStore.filtros"
      @aplicar="funcionarioStore.aplicarFiltros"
      @limpar="funcionarioStore.limparFiltros"
    />

    <p v-if="funcionarioStore.isLoading" class="mt-8 text-govbr-text-secondary">Carregando fila de agendamento...</p>

    <p v-else-if="funcionarioStore.agendamentosFiltrados.length === 0" class="mt-8 text-govbr-text-secondary">
      Nenhum paciente encontrado para os filtros selecionados.
    </p>

    <div v-else class="mt-6 grid gap-10 sm:grid-cols-2 lg:grid-cols-2">
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