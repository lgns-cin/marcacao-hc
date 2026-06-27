<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'vue-toastification';
import { MagnifyingGlassIcon, ClockIcon, CheckCircleIcon, InboxIcon, ChevronDownIcon } from '@heroicons/vue/24/outline';
import { FunnelIcon } from '@heroicons/vue/20/solid';
import { useFuncionarioStore } from '../../stores/funcionario';
import { useAutoRefresh } from '../../composables/useAutoRefresh';
import MinhaAreaCard from '../components/MinhaAreaCard.vue';
import MinhaAreaDetailModal from '../components/MinhaAreaDetailModal.vue';
import FilaFiltros from '../../shared/components/FilaFiltros.vue';
import type { MinhaAreaItem } from '../types';

import Button from '../../shared/components/Button.vue';

const funcionarioStore = useFuncionarioStore();
const toast = useToast();

const filtrosExpandidos = ref(false);
const modalAberto = ref(false);
const itemSelecionado = ref<MinhaAreaItem | null>(null);
const visaoInicialModal = ref<'detalhes' | 'devolverAFila'>('detalhes');

// Finalizados ocupam muito espaço: recolhidos por padrão e limitados a alguns itens.
const finalizadosExpandido = ref(false);
const mostrarTodosFinalizados = ref(false);
const LIMITE_FINALIZADOS = 10;
const finalizadosVisiveis = computed(() =>
  mostrarTodosFinalizados.value
    ? funcionarioStore.itensFinalizados
    : funcionarioStore.itensFinalizados.slice(0, LIMITE_FINALIZADOS)
);

function abrirDetalhes(item: MinhaAreaItem) {
  itemSelecionado.value = item;
  visaoInicialModal.value = 'detalhes';
  modalAberto.value = true;
}

function abrirDevolverAFila(item: MinhaAreaItem) {
  itemSelecionado.value = item;
  visaoInicialModal.value = 'devolverAFila';
  modalAberto.value = true;
}

function fecharDetalhes() {
  modalAberto.value = false;
}

async function aguardarConfirmacao(id: number) {
  try {
    await funcionarioStore.aguardarConfirmacao(id);
    toast.success('Aguardando confirmação do paciente.');
    modalAberto.value = false;
  } catch (error) {
    toast.error('Não foi possível atualizar este agendamento.');
  }
}

async function devolverAFila(id: number, motivo: string) {
  try {
    await funcionarioStore.devolverAFila(id, motivo);
    toast.success('Solicitação devolvida à fila com sucesso.');
    modalAberto.value = false;
  } catch (error) {
    toast.error('Não foi possível devolver esta solicitação à fila.');
  }
}

async function reportarProblema(id: number, motivo: string, detalhes: string) {
  try {
    await funcionarioStore.reportarProblema(id, motivo, detalhes);
    toast.success('Problema reportado com sucesso.');
  } catch (error) {
    toast.error('Não foi possível reportar o problema.');
  }
}

async function finalizar(id: number) {
  try {
    await funcionarioStore.finalizarAgendamento(id);
    toast.success('Agendamento finalizado com sucesso.');
    modalAberto.value = false;
  } catch (error) {
    toast.error('Não foi possível finalizar este agendamento.');
  }
}

async function carregarMinhaArea() {
  try {
    await funcionarioStore.fetchMinhaArea();
  } catch {
    toast.error('Não foi possível carregar a sua área.');
  }
}

onMounted(() => carregarMinhaArea());

useAutoRefresh(
  () => funcionarioStore.fetchMinhaArea({ silencioso: true }),
  10000,
  modalAberto,
);
</script>

<template>
  <div>
    <h1 class="text-[2.4rem] text-govbr-text">Minha Área</h1>
    <p class="text-[1.6rem] text-govbr-text-secondary">Realize o filtro por tipo de exame e localização</p>

    <div class="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="relative w-2/3">
        <input
          :value="funcionarioStore.filtrosMinhaArea.busca"
          type="text"
          placeholder="Busque por nome ou n° do prontuário"
          class="w-full rounded bg-[#F8F8F8] px-4 py-3 pr-10 text-sm placeholder-govbr-text-secondary focus:outline-none focus:ring-1 focus:ring-govbr-primary"
          @input="funcionarioStore.setBuscaMinhaArea(($event.target as HTMLInputElement).value)"
        />
        <MagnifyingGlassIcon class="absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 stroke-2 text-govbr-primary" />
      </div>

      <Button variant="primary" @click="filtrosExpandidos = !filtrosExpandidos">
        <FunnelIcon class="h-5 w-5" />
        {{ filtrosExpandidos ? 'Ocultar Filtros' : 'Expandir Filtros' }}
      </Button>
    </div>

    <FilaFiltros
      v-if="filtrosExpandidos"
      :filtros="funcionarioStore.filtrosMinhaArea"
      @aplicar="funcionarioStore.aplicarFiltrosMinhaArea"
      @limpar="funcionarioStore.limparFiltrosMinhaArea"
    />

    <p v-if="funcionarioStore.isLoadingMinhaArea" class="mt-8 text-govbr-text-secondary">Carregando sua área...</p>

    <div v-else-if="funcionarioStore.minhaArea.length === 0" class="mt-10 flex justify-center">
      <div class="flex flex-col items-center gap-4 rounded-lg border border-govbr-border bg-white px-10 py-10 text-center">
        <p class="font-medium text-govbr-text">Você ainda não possui solicitações atribuídas.</p>
        <InboxIcon class="h-24 w-24 text-govbr-border" />
      </div>
    </div>

    <div v-else class="mt-8 space-y-10">
      <section>
        <div class="flex items-center gap-2 border-b border-govbr-border pb-3">
          <ClockIcon class="h-5 w-5 text-govbr-primary" />
          <h2 class="text-lg font-bold text-govbr-text">Em andamento</h2>
          <p class="text-sm text-govbr-text-secondary">Solicitações sob sua responsabilidade que ainda precisam ser agendadas.</p>
        </div>

        <p v-if="funcionarioStore.itensEmAndamento.length === 0" class="mt-4 rounded-lg border border-govbr-border bg-white px-5 py-4 text-sm text-govbr-text-secondary">
          Nenhum exame em andamento.
        </p>
        <div v-else class="mt-4 grid gap-4 sm:grid-cols-2">
          <MinhaAreaCard
            v-for="item in funcionarioStore.itensEmAndamento"
            :key="item.id"
            :meuItem="item"
            @ver-mais="abrirDetalhes"
            @devolver-a-fila="abrirDevolverAFila"
          />
        </div>
      </section>

      <section>
        <div class="flex items-center gap-2 border-b border-govbr-border pb-3">
          <ClockIcon class="h-5 w-5 text-govbr-primary" />
          <h2 class="text-lg font-bold text-govbr-text">Aguardando Confirmação</h2>
          <span
            v-if="funcionarioStore.itensAguardandoConfirmacao.length > 0"
            class="flex h-5 w-5 items-center justify-center rounded-full bg-govbr-primary text-xs font-bold text-white"
          >
            {{ funcionarioStore.itensAguardandoConfirmacao.length }}
          </span>
          <p class="text-sm text-govbr-text-secondary">Solicitações já agendadas que aguardam confirmação do paciente.</p>
        </div>

        <p v-if="funcionarioStore.itensAguardandoConfirmacao.length === 0" class="mt-4 rounded-lg border border-govbr-border bg-white px-5 py-4 text-sm text-govbr-text-secondary">
          Nenhuma solicitação aguardando confirmação.
        </p>
        <div v-else class="mt-4 grid gap-4 sm:grid-cols-2">
          <MinhaAreaCard
            v-for="item in funcionarioStore.itensAguardandoConfirmacao"
            :key="item.id"
            :meuItem="item"
            @ver-mais="abrirDetalhes"
            @devolver-a-fila="abrirDevolverAFila"
          />
        </div>
      </section>

      <section>
        <button
          type="button"
          class="flex w-full items-center gap-2 border-b border-govbr-border pb-3 text-left"
          @click="finalizadosExpandido = !finalizadosExpandido"
        >
          <CheckCircleIcon class="h-5 w-5 shrink-0 text-govbr-primary" />
          <h2 class="text-lg font-bold text-govbr-text">Finalizados</h2>
          <span class="rounded-full bg-govbr-bg px-2 py-0.5 text-xs font-bold text-govbr-text-secondary">
            {{ funcionarioStore.itensFinalizados.length }}
          </span>
          <p class="hidden text-sm text-govbr-text-secondary sm:block">Solicitações finalizadas, confirmadas ou encerradas.</p>
          <ChevronDownIcon
            class="ml-auto h-5 w-5 shrink-0 text-govbr-text-secondary transition-transform"
            :class="{ 'rotate-180': finalizadosExpandido }"
          />
        </button>

        <template v-if="finalizadosExpandido">
          <p v-if="funcionarioStore.itensFinalizados.length === 0" class="mt-4 rounded-lg border border-govbr-border bg-white px-5 py-4 text-sm text-govbr-text-secondary">
            Nenhum exame finalizado.
          </p>
          <template v-else>
            <div class="mt-4 grid gap-4 sm:grid-cols-2">
              <MinhaAreaCard
                v-for="item in finalizadosVisiveis"
                :key="item.id"
                :meuItem="item"
                @ver-mais="abrirDetalhes"
                @devolver-a-fila="abrirDevolverAFila"
              />
            </div>
            <button
              v-if="funcionarioStore.itensFinalizados.length > LIMITE_FINALIZADOS"
              type="button"
              class="mt-4 text-sm font-bold text-govbr-primary hover:underline"
              @click="mostrarTodosFinalizados = !mostrarTodosFinalizados"
            >
              {{ mostrarTodosFinalizados ? 'Ver menos' : `Ver todos (${funcionarioStore.itensFinalizados.length})` }}
            </button>
          </template>
        </template>
      </section>
    </div>

    <MinhaAreaDetailModal
      v-if="itemSelecionado" 
      :show="modalAberto"
      :item="itemSelecionado"
      :visao-inicial="visaoInicialModal"
      @close="fecharDetalhes"
      @aguardar-confirmacao="aguardarConfirmacao"
      @devolver-a-fila="devolverAFila"
      @reportar-problema="reportarProblema"
      @finalizar="finalizar"
    />
  </div>
</template>