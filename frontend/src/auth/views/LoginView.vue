<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { LockClosedIcon, UserIcon } from '@heroicons/vue/24/outline';
import { useAuthStore } from '../../stores/auth';

const authStore = useAuthStore();
const router = useRouter();
const toast = useToast();

const username = ref('');
const password = ref('');
const lembrarMe = ref(false);
const carregando = ref(false);
const erro = ref('');

async function entrar() {
  if (!username.value || !password.value) {
    erro.value = 'Informe usuário e senha para continuar.';
    return;
  }

  erro.value = '';
  carregando.value = true;
  try {
    await authStore.login(username.value, password.value, lembrarMe.value);
    toast.success('Login realizado com sucesso.');
    router.push({ name: 'FilaAgendamento' });
  } catch (error) {
    erro.value = 'Usuário ou senha inválidos.';
  } finally {
    carregando.value = false;
  }
}
</script>

<template>
  <div class="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg">
    <div class="flex flex-col items-center gap-2 text-center">
      <img src="/hc-icon.png" alt="Hospital das Clínicas - UFPE" class="h-14 w-14 object-contain" />
      <h1 class="text-xl font-bold text-govbr-text">Hospital das Clínicas - UFPE</h1>
      <p class="text-sm text-govbr-text-secondary">Entre com seu usuário para acessar o sistema de agendamento.</p>
    </div>

    <form class="mt-8 flex flex-col gap-4" @submit.prevent="entrar">
      <div>
        <label for="username" class="mb-1 block text-sm font-semibold text-govbr-text">Usuário</label>
        <div class="relative">
          <UserIcon class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-govbr-text-secondary" />
          <input
            id="username"
            v-model="username"
            type="text"
            autocomplete="username"
            placeholder="Digite seu usuário"
            class="w-full rounded border border-govbr-border py-2 pl-10 pr-3 text-sm placeholder-govbr-text-secondary focus:outline-none focus:ring-1 focus:ring-govbr-primary"
          />
        </div>
      </div>

      <div>
        <label for="password" class="mb-1 block text-sm font-semibold text-govbr-text">Senha</label>
        <div class="relative">
          <LockClosedIcon class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-govbr-text-secondary" />
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="Digite sua senha"
            class="w-full rounded border border-govbr-border py-2 pl-10 pr-3 text-sm placeholder-govbr-text-secondary focus:outline-none focus:ring-1 focus:ring-govbr-primary"
          />
        </div>
      </div>

      <label class="flex items-center gap-2 text-sm text-govbr-text">
        <input v-model="lembrarMe" type="checkbox" class="h-4 w-4 rounded border-govbr-border text-govbr-primary focus:ring-govbr-primary" />
        Lembrar de mim
      </label>

      <p v-if="erro" class="rounded bg-govbr-error-bg px-3 py-2 text-sm text-govbr-error">{{ erro }}</p>

      <button
        type="submit"
        :disabled="carregando"
        class="mt-2 rounded-full bg-govbr-primary px-6 py-3 text-sm font-bold text-white hover:bg-govbr-primary-hover disabled:opacity-60"
      >
        {{ carregando ? 'Entrando...' : 'Entrar' }}
      </button>
    </form>
  </div>
</template>
