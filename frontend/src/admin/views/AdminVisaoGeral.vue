<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue';
import { useToast } from 'vue-toastification';
import { useAdminStore } from '../../stores/admin';
import AdminKpiCard from '../components/AdminKpiCard.vue';
import BarrasEtapasChart from '../components/BarrasEtapasChart.vue';
import MotivosDevolucaoChart from '../components/MotivosDevolucaoChart.vue';
import PersonalizarIndicadores from '../components/PersonalizarIndicadores.vue';
import { PERIODOS_VISAO_GERAL } from '../types';
import type { PeriodoVisaoGeral } from '../types';

const adminStore = useAdminStore();
const toast = useToast();

async function carregar() {
  try {
    await adminStore.fetchVisaoGeral();
  } catch (error) {
    toast.error('Não foi possível carregar a visão geral.');
  }
}

const INTERVALO_ATUALIZACAO_MS = 30000;
let intervaloAtualizacao: ReturnType<typeof setInterval> | undefined;

onMounted(() => {
  carregar();
  intervaloAtualizacao = setInterval(() => adminStore.fetchVisaoGeral({ silencioso: true }), INTERVALO_ATUALIZACAO_MS);
});

onUnmounted(() => {
  clearInterval(intervaloAtualizacao);
});
</script>

<template>
  <div>
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="text-[2.4rem] text-govbr-text">Central Administrativa</h1>
        <p class="text-[1.6rem] text-govbr-text-secondary">Visualize os indicadores da instituição</p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <label class="flex items-center gap-2 text-sm font-semibold text-govbr-text">
          Período:
          <select
            :value="adminStore.periodoVisaoGeral"
            class="rounded border border-govbr-border bg-white px-3 py-2 text-sm font-normal text-govbr-text focus:outline-none focus:ring-1 focus:ring-govbr-primary"
            @change="adminStore.definirPeriodoVisaoGeral(($event.target as HTMLSelectElement).value as PeriodoVisaoGeral)"
          >
            <option v-for="p in PERIODOS_VISAO_GERAL" :key="p.id" :value="p.id">{{ p.label }}</option>
          </select>
        </label>
        <PersonalizarIndicadores
          v-if="adminStore.visaoGeral"
          :todos="adminStore.todosIndicadores"
          :selecionados="adminStore.indicadoresVisiveis"
          @aplicar="adminStore.definirIndicadoresVisiveis"
        />
      </div>
    </div>

    <p v-if="adminStore.isLoadingVisaoGeral" class="mt-8 text-govbr-text-secondary">Carregando indicadores...</p>

    <template v-else-if="adminStore.visaoGeral">
      <div v-if="adminStore.kpisVisiveis.length > 0" class="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <AdminKpiCard v-for="kpi in adminStore.kpisVisiveis" :key="kpi.id" :kpi="kpi" />
      </div>

      <div class="mt-8 space-y-8">
        <template v-for="grafico in adminStore.graficosVisiveis" :key="grafico.id">
          <BarrasEtapasChart v-if="grafico.tipo === 'barras_horizontais'" :grafico="grafico" />
          <MotivosDevolucaoChart v-else :grafico="grafico" />
        </template>
      </div>

      <p
        v-if="adminStore.kpisVisiveis.length === 0 && adminStore.graficosVisiveis.length === 0"
        class="mt-8 text-govbr-text-secondary"
      >
        Nenhum indicador selecionado. Use "Personalizar Indicadores" para exibir KPIs e gráficos.
      </p>
    </template>
  </div>
</template>
