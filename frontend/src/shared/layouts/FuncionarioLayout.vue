<script setup lang="ts">
import LayoutPainelBase from './LayoutPainelBase.vue';
import { useAuthStore } from '../../stores/auth';
import { ChevronRightIcon } from '@heroicons/vue/24/outline';

const authStore = useAuthStore();

const navItems = [
  { name: 'FilaAgendamento', label: 'Fila de Agendamento' },
  { name: 'MinhaArea', label: 'Minha Área' },
];
</script>

<template>
  <LayoutPainelBase :nav-items="navItems" :fluid-content="false">
    
    <template #footer-links>
      <router-link
        v-if="authStore.isAdmin"
        :to="{ name: 'AdminVisaoGeral' }"
        class="flex items-center justify-between border-t border-govbr-border px-6 py-4 text-base font-medium text-govbr-primary transition-colors hover:bg-govbr-bg"
      >
        Central Administrativa
        <ChevronRightIcon class="h-5 w-5" />
      </router-link>
    </template>

  </LayoutPainelBase>
</template>