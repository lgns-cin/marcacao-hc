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
import type { GraficoMotivosDevolucao } from '../types';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const props = defineProps<{
  grafico: GraficoMotivosDevolucao;
}>();

const chartData = computed(() => ({
  labels: props.grafico.dados.map((d) => d.motivo),
  datasets: [
    {
      label: 'Pacientes',
      backgroundColor: '#7C3AED',
      data: props.grafico.dados.map((d) => d.quantidade),
    },
  ],
}));

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
};
</script>

<template>
  <div class="rounded-lg border border-govbr-border bg-white p-6">
    <div class="flex items-center gap-2">
      <ClipboardDocumentListIcon class="h-5 w-5 text-govbr-primary" />
      <h2 class="text-lg font-bold text-govbr-text">{{ grafico.titulo }}</h2>
    </div>
    <p class="text-sm text-govbr-text-secondary">{{ grafico.subtitulo }}</p>
    <div class="mt-4 h-80">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>
