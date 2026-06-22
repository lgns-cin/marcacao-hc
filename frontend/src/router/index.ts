import { createRouter, createWebHistory, NavigationGuardNext, RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import FormLayout from '../shared/layouts/FormLayout.vue';
import FormInicio from '../form/FormInicio.vue';
import FormProntuario from '../form/FormProntuario.vue';
import FormSolicitacao from '../form/FormSolicitacao.vue';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'FormInicio',
    component: FormInicio,
    meta: {
      layout: FormLayout
    }
  },
  {
    path: '/prontuario',
    name: 'FormProntuario',
    component: FormProntuario,
    meta: {
      layout: FormLayout
    }
  },
  {
    path: '/solicitacao',
    name: 'FormSolicitacao',
    component: FormSolicitacao,
    meta: {
      layout: FormLayout
    }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, _from, next: NavigationGuardNext) => {
  // Pinia store must be used inside a function to ensure it's initialized
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' });
  } else {
    next();
  }
});

export default router;
