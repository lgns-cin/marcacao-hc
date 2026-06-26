<script setup lang="ts">
import LayoutPainelBase from './LayoutPainelBase.vue';
import { ChevronRightIcon } from '@heroicons/vue/24/outline';

const navItems = [
  { name: 'AdminVisaoGeral', label: 'Visão geral' },
  { name: 'AdminPendencias', label: 'Gestão de Problemas' },
  { name: 'AdminAgendamentos', label: 'Gestão de Agendamentos' },
];
</script>

<template>
  <LayoutPainelBase :nav-items="navItems" :fluid-content="true">
    
    <template #footer-links>
      <router-link
        :to="{ name: 'FilaAgendamento' }"
        class="flex items-center justify-between border-t border-govbr-border px-6 py-4 text-base font-medium text-govbr-primary transition-colors hover:bg-govbr-bg"
      >
        Área do Funcionário
        <ChevronRightIcon class="h-5 w-5" />
      </router-link>
    </template>

  </LayoutPainelBase>
</template>