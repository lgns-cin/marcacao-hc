<script setup lang="ts">
import { ref } from 'vue';
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline';
import type { FiltrosFila } from '../types';
import Button from '../../shared/components/Button.vue';

const REGIOES = ['Região Metropolitana', 'Agreste', 'Mata Sul', 'Mata Norte', 'Sertão'];
const TIPOS_EXAME = ['Tomografia', 'Ressonância', 'Mamografia', 'Endoscopia', 'Colonoscopia', 'Ultrassonografia', 'Espirometria'];
const FAIXAS_ETARIAS = [
  { value: 'Todas', label: 'Todas' },
  { value: '0-17', label: '0 a 17 anos' },
  { value: '18-59', label: '18 a 59 anos' },
  { value: '60+', label: '60 anos ou mais' },
];

const props = defineProps<{
  filtros: FiltrosFila;
}>();

const emit = defineEmits<{
  aplicar: [filtros: Partial<FiltrosFila>];
  limpar: [];
}>();

const regioesSelecionadas = ref<string[]>([...props.filtros.regioes]);
const tiposExameSelecionados = ref<string[]>([...props.filtros.tiposExame]);
const municipio = ref(props.filtros.municipio);
const faixaEtaria = ref(props.filtros.faixaEtaria);

function aplicar() {
  emit('aplicar', {
    regioes: regioesSelecionadas.value,
    tiposExame: tiposExameSelecionados.value,
    municipio: municipio.value,
    faixaEtaria: faixaEtaria.value,
  });
}

function limpar() {
  regioesSelecionadas.value = [];
  tiposExameSelecionados.value = [];
  municipio.value = '';
  faixaEtaria.value = 'Todas';
  emit('limpar');
}
</script>

<template>
  <div class="mt-4 grid gap-6 rounded-lg border border-govbr-border bg-white p-6 sm:grid-cols-2">
    <div>
      <p class="font-semibold text-govbr-text">Região</p>
      <p class="text-sm text-govbr-text-secondary">Selecione uma ou mais regiões.</p>
      <div class="mt-3 space-y-2">
        <label v-for="regiao in REGIOES" :key="regiao" class="flex items-center gap-2 text-sm text-govbr-text">
          <input type="checkbox" :value="regiao" v-model="regioesSelecionadas" class="h-4 w-4 rounded border-govbr-border text-govbr-primary focus:ring-govbr-primary" />
          {{ regiao }}
        </label>
      </div>
    </div>

    <div>
      <p class="font-semibold text-govbr-text">Tipo de Exame</p>
      <p class="text-sm text-govbr-text-secondary">Selecione uma ou mais regiões.</p>
      <div class="mt-3 grid grid-cols-2 gap-2">
        <label v-for="tipo in TIPOS_EXAME" :key="tipo" class="flex items-center gap-2 text-sm text-govbr-text">
          <input type="checkbox" :value="tipo" v-model="tiposExameSelecionados" class="h-4 w-4 rounded border-govbr-border text-govbr-primary focus:ring-govbr-primary" />
          {{ tipo }}
        </label>
      </div>
    </div>

    <div class="relative">
      <label class="mb-1 block text-sm font-semibold text-govbr-text">Município</label>
      <input
        v-model="municipio"
        type="text"
        placeholder="Digite o Município"
        class="w-full rounded border border-govbr-border px-3 py-2 pr-9 text-sm placeholder-govbr-text-secondary focus:outline-none focus:ring-1 focus:ring-govbr-primary"
      />
      <MagnifyingGlassIcon class="absolute right-3 top-9 h-4 w-4 text-govbr-text-secondary" />
    </div>

    <div>
      <label class="mb-1 block text-sm font-semibold text-govbr-text">Faixa etária</label>
      <select
        v-model="faixaEtaria"
        class="w-full rounded border border-govbr-primary px-3 py-2 text-sm text-govbr-text focus:outline-none focus:ring-1 focus:ring-govbr-primary"
      >
        <option v-for="faixa in FAIXAS_ETARIAS" :key="faixa.value" :value="faixa.value">{{ faixa.label }}</option>
      </select>
    </div>

    <div class="flex items-center gap-6 sm:col-span-2">
      <Button variant="primary" @click="aplicar">
        Aplicar Filtros
      </Button>

      <Button variant="tertiary" @click="limpar">
        Limpar
      </Button>
    </div>
  </div>
</template>
