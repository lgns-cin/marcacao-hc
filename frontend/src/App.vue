<template>
  <component :is="layout">
    <router-view />
  </component>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
import { computed, onMounted } from 'vue';
import { useAuthStore } from './stores/auth';

const route = useRoute();

const layout = computed(() => route.meta.layout);

const authStore = useAuthStore();
onMounted(async () => {
  await authStore.initializeAuth();
});
</script>
