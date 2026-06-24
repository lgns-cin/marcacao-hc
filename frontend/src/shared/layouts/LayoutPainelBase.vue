<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import {
  Bars3Icon,
  XMarkIcon,
  ChevronRightIcon,
} from '@heroicons/vue/24/outline';
import ProfileDropdown from '../components/ProfileDropdown.vue';

// é importante para que o componente seja moldado tanto para a visão de Funcionário quanto de Admin
defineProps<{
  navItems: Array<{ name: string; label: string }>;
}>();

const route = useRoute();

// estados locais
const drawerOpen = ref(false); // Controla apenas a abertura do menu lateral deslizante

// Fecha o menu lateral automaticamente sempre que houver mudança de rota
watch(() => route.path, () => {
  drawerOpen.value = false;
});
</script>

<template>
  <div class="min-h-screen bg-white">
    <!--header padrão para funcionários e admins-->
    <header class="sticky top-0 z-30 flex items-center justify-between bg-white border-b border-govbr-border px-6 py-4">
      <div class="flex items-center gap-4">
        <button
          class="text-govbr-primary hover:text-govbr-primary-hover focus:outline-none cursor-pointer"
          @click="drawerOpen = true"
        >
          <Bars3Icon class="h-7 w-7" />
        </button>
        <h1 class="text-2xl font-bold text-govbr-text">Hospital das Clínicas - UFPE</h1>
      </div>

      <div class="flex items-center gap-4">
        <ProfileDropdown />
      </div>
    </header>

    <transition name="fade">
      <div v-if="drawerOpen" class="fixed inset-0 z-40 bg-gray-900/50" @click="drawerOpen = false" />
    </transition>

    <!--menu lateral deslizante-->
    <transition name="slide">
      <aside v-if="drawerOpen" class="fixed inset-y-0 left-0 z-50 w-full max-w-sm bg-white shadow-xl">
        <div class="flex items-center justify-between border-b border-govbr-border px-6 py-5">
          <div class="flex items-center gap-3">
            <img src="/hc-icon.png" alt="Hospital das Clínicas" class="h-10 w-10 shrink-0 object-contain" />
            <span class="text-sm font-bold uppercase leading-tight text-govbr-text">
              Hospital<br />das Clínicas<br />UFPE
            </span>
          </div>
          <button class="text-govbr-text hover:text-govbr-primary focus:outline-none" @click="drawerOpen = false">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <!--menu lateral com rotas-->
        <nav class="py-2">
          <router-link
            v-for="item in navItems"
            :key="item.name"
            :to="{ name: item.name }"
            class="flex items-center justify-between px-6 py-4 text-base font-medium transition-colors"
            :class="route.name === item.name ? 'bg-govbr-primary text-white' : 'text-govbr-primary hover:bg-govbr-bg'"
          >
            {{ item.label }}
            <ChevronRightIcon class="h-5 w-5" />
          </router-link>

          <slot name="footer-links"></slot>
        </nav>
      </aside>
    </transition>

    <main class="px-6 py-6 md:px-10 md:py-10 mx-auto max-w-[1400px]">
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