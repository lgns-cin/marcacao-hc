import { createRouter, createWebHistory, NavigationGuardNext, RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import FormLayout from '../shared/layouts/FormLayout.vue';
import FuncionarioLayout from '../shared/layouts/FuncionarioLayout.vue';
import LoginLayout from '../shared/layouts/LoginLayout.vue';
import AdminLayout from '../shared/layouts/AdminLayout.vue';
import FormInicio from '../form/FormInicio.vue';
import FormProntuario from '../form/FormProntuario.vue';
import FormSolicitacao from '../form/FormSolicitacao.vue';
import FormContato from '../form/FormContato.vue';
import FormSubmit from '../form/FormSubmit.vue';
import FilaAgendamento from '../funcionario/views/FilaAgendamento.vue';
import MinhaArea from '../funcionario/views/MinhaArea.vue';
import LoginView from '../auth/views/LoginView.vue';
import AdminVisaoGeral from '../admin/views/AdminVisaoGeral.vue';
import AdminPendencias from '../admin/views/AdminPendencias.vue';
import AdminAgendamentos from '../admin/views/AdminAgendamentos.vue';

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
    path: '/contato',
    name: 'FormContato',
    component: FormContato,
    meta: {
      layout: FormLayout
    }
  },
  {
    path: '/submit',
    name: 'FormSubmit',
    component: FormSubmit,
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
  },
  {
    path: '/admin',
    name: 'AdminVisaoGeral',
    component: AdminVisaoGeral,
    meta: {
      layout: AdminLayout,
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/admin/pendencias',
    name: 'AdminPendencias',
    component: AdminPendencias,
    meta: {
      layout: AdminLayout,
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/admin/agendamentos',
    name: 'AdminAgendamentos',
    component: AdminAgendamentos,
    meta: {
      layout: AdminLayout,
      requiresAuth: true,
      requiresAdmin: true
    }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// A navegação inicial do router é resolvida antes do App.vue montar, então
// sem isso o guard avaliaria isAdmin/isAuthenticated com o usuário ainda não
// carregado (fetchUser ainda em voo) em qualquer reload de página.
let authReadyPromise: Promise<void> | null = null;

router.beforeEach(async (to, _from, next: NavigationGuardNext) => {
  // Pinia store must be used inside a function to ensure it's initialized
  const authStore = useAuthStore();

  if (!authReadyPromise) {
    authReadyPromise = authStore.initializeAuth();
  }
  await authReadyPromise;

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' });
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'FilaAgendamento' });
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'FilaAgendamento' });
  } else {
    next();
  }
});

export default router;
