<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  Bars3Icon,
  XMarkIcon,
  BellIcon,
  ChevronDownIcon,
  ChevronRightIcon,
} from '@heroicons/vue/24/outline';
import { useAuthStore } from '../../stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const drawerOpen = ref(false);
const profileOpen = ref(false);

const iniciais = computed(() => {
  const nome = authStore.user?.givenName?.[0] || authStore.user?.username || 'Usuário';
  return nome
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((parte) => parte[0]?.toUpperCase())
    .join('');
});

const navItems = [
  { name: 'AdminVisaoGeral', label: 'Visão geral' },
  { name: 'AdminPendencias', label: 'Gestão de Pendências' },
  { name: 'AdminAgendamentos', label: 'Gerenciamento de Agendamentos' },
  { name: 'AdminFila', label: 'Fila de Agendamentos' },
];

async function handleLogout() {
  profileOpen.value = false;
  await authStore.logout(router);
}

watch(() => route.path, () => {
  drawerOpen.value = false;
  profileOpen.value = false;
});
</script>

<template>
  <div class="min-h-screen bg-govbr-bg">
    <!-- Header -->
    <header class="sticky top-0 z-30 flex items-center justify-between bg-white border-b border-govbr-border px-6 py-4">
      <div class="flex items-center gap-4">
        <button
          class="text-govbr-primary hover:text-govbr-primary-hover focus:outline-none"
          @click="drawerOpen = true"
        >
          <Bars3Icon class="h-7 w-7" />
        </button>
        <h1 class="text-2xl font-bold text-govbr-text">Hospital das Clínicas - UFPE</h1>
      </div>

      <div class="flex items-center gap-4">
        <button class="relative text-govbr-text hover:text-govbr-primary focus:outline-none">
          <BellIcon class="h-6 w-6" />
          <span class="absolute -top-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-govbr-error border-2 border-white" />
        </button>

        <div class="h-6 w-px bg-govbr-border" />

        <div class="relative">
          <button
            class="flex items-center gap-1 focus:outline-none"
            @click="profileOpen = !profileOpen"
          >
            <span class="flex h-9 w-9 items-center justify-center rounded-full bg-govbr-primary text-sm font-semibold text-white">
              {{ iniciais }}
            </span>
            <ChevronDownIcon class="h-4 w-4 text-govbr-text-secondary" />
          </button>

          <div v-if="profileOpen" class="fixed inset-0 z-10" @click="profileOpen = false" />

          <div
            v-if="profileOpen"
            class="absolute right-0 z-20 mt-2 w-56 rounded-md border border-govbr-border bg-white shadow-lg"
          >
            <p class="px-4 py-3 text-sm font-medium text-govbr-text border-b border-govbr-border truncate">
              {{ authStore.user?.givenName?.[0] || authStore.user?.username }}
            </p>
            <button
              class="w-full px-4 py-3 text-left text-sm text-govbr-error hover:bg-govbr-bg"
              @click="handleLogout"
            >
              Sair da Conta
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Drawer overlay -->
    <transition name="fade">
      <div
        v-if="drawerOpen"
        class="fixed inset-0 z-40 bg-gray-900/50"
        @click="drawerOpen = false"
      />
    </transition>

    <transition name="slide">
      <aside v-if="drawerOpen" class="fixed inset-y-0 left-0 z-50 w-full max-w-sm bg-white shadow-xl">
        <div class="flex items-center justify-between border-b border-govbr-border px-6 py-5">
          <div class="flex items-center gap-3">
            <img src="/hc-icon.png" alt="Hospital das Clínicas - UFPE" class="h-10 w-10 shrink-0 object-contain" />
            <span class="text-sm font-bold uppercase leading-tight text-govbr-text">
              Hospital<br />das Clínicas<br />UFPE
            </span>
          </div>
          <button class="text-govbr-text hover:text-govbr-primary focus:outline-none" @click="drawerOpen = false">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <nav class="py-2">
          <router-link
            v-for="item in navItems"
            :key="item.name"
            :to="{ name: item.name }"
            class="flex items-center justify-between px-6 py-4 text-base font-medium transition-colors"
            :class="route.name === item.name
              ? 'bg-govbr-primary text-white'
              : 'text-govbr-primary hover:bg-govbr-bg'"
          >
            {{ item.label }}
            <ChevronRightIcon class="h-5 w-5" />
          </router-link>

          <router-link
            :to="{ name: 'FilaAgendamento' }"
            class="flex items-center justify-between border-t border-govbr-border px-6 py-4 text-base font-medium text-govbr-primary transition-colors hover:bg-govbr-bg"
          >
            Área do Funcionário
            <ChevronRightIcon class="h-5 w-5" />
          </router-link>
        </nav>
      </aside>
    </transition>

    <!-- Content -->
    <main class="px-6 py-6 md:px-10 md:py-10">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-enter-active, .slide-leave-active { transition: transform 0.25s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(-100%); }
</style>
