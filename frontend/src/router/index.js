import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/authStore";

import LoginView from "../views/LoginView.vue";
import DashboardView from "../views/DashboardView.vue";

const routes = [
  {
    path: "/login",
    name: "login",
    component: LoginView,
  },
  {
    path: "/",
    redirect: "/dashboard",
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: DashboardView,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Guard global: protege rutas que tengan meta.requiresAuth = true
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: "login" });
  } else if (to.name === "login" && authStore.isAuthenticated) {
    // Si ya estás logueado y vas al login, redirige al dashboard
    next({ name: "dashboard" });
  } else {
    next();
  }
});

export default router;
