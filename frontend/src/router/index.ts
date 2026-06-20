import { createRouter, createWebHistory, NavigationGuardNext, RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const routes: RouteRecordRaw[] = [
  /*
  Exemplo:
  {
    path: "/caminho",
    name: "nome da rota",
    component: Componente,
    meta: {
      layout: ComponenteDeLayout
    }
  }
  */
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
