import { createRouter, createWebHistory, NavigationGuardNext, RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import FormLayout from '../shared/layouts/FormLayout.vue';
import FuncionarioLayout from '../shared/layouts/FuncionarioLayout.vue';
import LoginLayout from '../shared/layouts/LoginLayout.vue';
import FormInicio from '../form/FormInicio.vue';
import FormProntuario from '../form/FormProntuario.vue';
import FormSolicitacao from '../form/FormSolicitacao.vue';
import FilaAgendamento from '../funcionario/views/FilaAgendamento.vue';
import MinhaArea from '../funcionario/views/MinhaArea.vue';
import LoginView from '../auth/views/LoginView.vue';

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: {
      layout: LoginLayout
    }
  },
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
  },
  {
    path: '/funcionario',
    name: 'FilaAgendamento',
    component: FilaAgendamento,
    meta: {
      layout: FuncionarioLayout,
      requiresAuth: true
    }
  },
  {
    path: '/funcionario/minha-area',
    name: 'MinhaArea',
    component: MinhaArea,
    meta: {
      layout: FuncionarioLayout,
      requiresAuth: true
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
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'FilaAgendamento' });
  } else {
    next();
  }
});

export default router;
