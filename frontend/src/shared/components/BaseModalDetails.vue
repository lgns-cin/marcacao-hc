<script setup lang="ts">
import { computed } from 'vue';
import { ClockIcon } from '@heroicons/vue/24/outline';
import { nomeDoCodigo, categoriaDoCodigo } from '../utils/catalogoExames';
import { getStatusClasses } from '../utils/statusFormatting';

const props = defineProps<{
  item: {
    prontuario: string;
    solicitacao?: string;
    diasNaFila: number;
    status: string;
    exame: string;
    unidadeSolicitante: string;
    dataRetorno: string;
    localizacao: string;
    idade: number;
    telefone?: string;
    estadoAtribuicao?: string;
    resultado?: string;
    funcionarioAtribuido?: string;
  };
}>();

const finalizado = computed(() => props.item.estadoAtribuicao === 'FINALIZADO');
const resultadoLabel = computed(() => props.item.resultado === 'CONFIRMADO' ? 'Confirmado' : 'Problema Reportado' );
const statusClasses = computed(() => getStatusClasses(props.item.status));
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div class="flex flex-wrap gap-2">
        <span class="rounded border border-govbr-border px-3 py-1 text-sm font-semibold text-govbr-text bg-gray-50">
          {{ categoriaDoCodigo(item.exame) ?? item.exame }}
        </span>
      </div>

      <div v-if="!finalizado || resultadoLabel == 'Problema Reportado'" class="flex items-center gap-2">
        <span class="flex items-center gap-1 text-[16px] text-govbr-text-secondary">
          <ClockIcon class="h-4 w-4" />
          há {{ item.diasNaFila }}d
        </span>
        <span :class="['rounded-full px-2.5 py-0.5 text-xs font-bold', statusClasses]">
          {{ item.status }}
        </span>
      </div>
      <span 
      v-if="finalizado"
      class="rounded-full border border-govbr-border px-2.5 py-0.5 text-xs font-bold text-govbr-text-secondary">
          {{ resultadoLabel }}
      </span>
    </div>

    <dl class="space-y-3 text-[16px] pt-2">
      <div>
        <dt class="inline font-semibold text-govbr-text">Exame: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ nomeDoCodigo(item.exame) }}</dd>
      </div>
      <div v-if="item.funcionarioAtribuido">
        <dt class="inline font-semibold text-govbr-text">Responsável: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ item.funcionarioAtribuido }}</dd>
      </div>
      <div v-if="item.telefone">
        <dt class="inline font-semibold text-govbr-text">Telefone: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ item.telefone }}</dd>
      </div>
      <div v-if="item.solicitacao">
        <dt class="inline font-semibold text-govbr-text">Solicitação: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ item.solicitacao }}</dd>
      </div>
      <div>
        <dt class="inline font-semibold text-govbr-text">Prontuário: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ item.prontuario }}</dd>
      </div>
      <div>
        <dt class="inline font-semibold text-govbr-text">Unidade Solicitante: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ item.unidadeSolicitante }}</dd>
      </div>
      <div>
        <dt class="inline font-semibold text-govbr-text">Data de retorno: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ item.dataRetorno }}</dd>
      </div>
      <div>
        <dt class="inline font-semibold text-govbr-text">Localização: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ item.localizacao }}</dd>
      </div>
      <div>
        <dt class="inline font-semibold text-govbr-text">Idade: </dt>
        <dd class="inline text-govbr-text-secondary"> {{ item.idade }}</dd>
      </div>
    </dl>

    <slot></slot>
  </div>
</template>
