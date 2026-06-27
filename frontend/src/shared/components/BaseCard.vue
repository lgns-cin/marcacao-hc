<script setup lang="ts">
import { computed } from 'vue';
import { UserGroupIcon, ClockIcon } from '@heroicons/vue/24/solid';
import { categoriaDoCodigo } from '../utils/catalogoExames';
import { isFinalizado, getEstadoLabel, getStatusClasses } from '../utils/statusFormatting';

const props = defineProps<{
  item: {
    nome: string;
    prontuario: string;
    solicitacao: string;
    status: string;
    diasNaFila: number;
    exame: string;
    estado?: string;
  };
}>();

const finalizado = computed(() => isFinalizado(props.item.estado));
const estadoLabel = computed(() => getEstadoLabel(props.item.estado));
const statusClasses = computed(() => getStatusClasses(props.item.status));
</script>

<template>
  <div class="rounded-lg bg-white p-5 shadow-[0_0_7.6px_rgba(0,0,0,0.15)] transition-shadow hover:shadow-xl">

    <div class="flex items-start justify-between gap-3">

      <div class="flex items-center gap-2">
        <UserGroupIcon class="h-6 w-6 shrink-0 text-govbr-text" />
        <h3 class="text-lg font-bold text-govbr-text">{{ item.nome }}</h3>
      </div>

      <div class="flex shrink-0 items-center gap-2 whitespace-nowrap">
        <template v-if="!finalizado">
          <span class="flex items-center gap-1 text-sm text-govbr-text-secondary">
            <ClockIcon class="h-4 w-4" />
            há {{ item.diasNaFila }}d
          </span>
          <template v-if="item.status">
            <span :class="['rounded-full px-2.5 py-1.5 text-xs font-bold', statusClasses]">
              {{ item.status }}
            </span>
          </template>
        </template>

        <span
          v-else
          class="rounded-full border border-govbr-border px-2.5 py-0.5 text-xs font-bold text-govbr-text-secondary"
        >
          {{ estadoLabel }}
        </span>
      </div>
    </div>

    <p class="mt-1 text-[16px] text-govbr-text-secondary">Prontuário: {{ item.prontuario }}</p>
    <p class="text-[16px] text-govbr-text-secondary">Solicitação: {{ item.solicitacao }}</p>

    <div class="mt-3">
      <span class="rounded border border-govbr-border px-3 py-1 text-sm font-semibold text-govbr-text">
        {{ categoriaDoCodigo(item.exame) ?? item.exame }}
      </span>
    </div>

    <div class="mt-4 flex items-center gap-6">
      <slot :isFinalizado="finalizado"></slot>
    </div>

  </div>
</template>
