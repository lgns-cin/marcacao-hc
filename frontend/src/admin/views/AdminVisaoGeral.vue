<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue';
import { useToast } from 'vue-toastification';
import { useAdminStore } from '../../stores/admin';
import AdminKpiCard from '../components/AdminKpiCard.vue';
import BarrasEtapasChart from '../components/BarrasEtapasChart.vue';
import MotivosDevolucaoChart from '../components/MotivosDevolucaoChart.vue';

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
        <p class="text-[1.6rem] text-govbr-text-secondary">
          Visualize os indicadores da instituição · <span class="font-semibold">mês atual</span>
        </p>
      </div>
    </div>

    <p v-if="adminStore.isLoadingVisaoGeral" class="mt-8 text-govbr-text-secondary">Carregando indicadores...</p>

    <template v-else-if="adminStore.visaoGeral">
      <div class="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <AdminKpiCard v-for="kpi in adminStore.visaoGeral.kpis" :key="kpi.id" :kpi="kpi" />
      </div>

      <div class="mt-8 space-y-8">
        <template v-for="grafico in adminStore.visaoGeral.graficos" :key="grafico.titulo">
          <BarrasEtapasChart v-if="grafico.tipo === 'barras_horizontais'" :grafico="grafico" />
          <MotivosDevolucaoChart v-else :grafico="grafico" />
        </template>
      </div>

      <p
        v-if="adminStore.visaoGeral.kpis.length === 0 && adminStore.visaoGeral.graficos.length === 0"
        class="mt-8 text-govbr-text-secondary"
      >
        Nenhum indicador disponível para exibição.
      </p>
    </template>
  </div>
</template>
