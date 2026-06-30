<script setup lang="ts">
import { computed } from 'vue';
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { ClipboardDocumentListIcon } from '@heroicons/vue/24/outline';
import type { GraficoBarrasEtapas } from '../types';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const props = defineProps<{
  grafico: GraficoBarrasEtapas;
}>();

const chartData = computed(() => ({
  labels: props.grafico.dados.map((d) => d.categoria),
  datasets: [
    { label: 'Concluídos', backgroundColor: '#168821', data: props.grafico.dados.map((d) => d.concluidos) },
    { label: 'Em Andamento', backgroundColor: '#FFCD07', data: props.grafico.dados.map((d) => d.emAgendamento) },
    { label: 'A agendar', backgroundColor: '#E52207', data: props.grafico.dados.map((d) => d.pendentes) },
  ],
}));

const chartOptions = {
  indexAxis: 'y' as const,
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: { stacked: true },
    y: { stacked: true },
  },
  plugins: {
    legend: { position: 'top' as const, align: 'start' as const },
  },
};
</script>

<template>
  <div class="rounded-lg border border-govbr-border bg-white p-6">
    <div class="flex items-center gap-2">
      <ClipboardDocumentListIcon class="h-5 w-5 text-govbr-primary" />
      <h2 class="text-lg font-bold text-govbr-text">{{ grafico.titulo }}</h2>
    </div>
    <p class="text-sm text-govbr-text-secondary">{{ grafico.subtitulo }}</p>
    <div class="mt-4" :style="{ height: `${grafico.dados.length * 60 + 40}px` }">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>
