<template>
  <div class="dashboard">
    <header>
      <h1>Dashboard</h1>
      <button @click="handleLogout">Cerrar sesión</button>
    </header>

    <main>
      <p>Has iniciado sesión correctamente. 🎉</p>
      <p>Aquí luego mostraremos fichajes, ausencias, etc.</p>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/authStore";

const router = useRouter();
const authStore = useAuthStore();

function handleLogout() {
  authStore.logout();
  router.push({ name: "login" });
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  padding: 1.5rem 2rem;
  background: #020617;
  color: #e5e7eb;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

button {
  padding: 0.5rem 0.9rem;
  border-radius: 0.5rem;
  border: none;
  background: #ef4444;
  color: white;
  cursor: pointer;
}
</style>
