<!-- src/views/LoginView.vue -->
<template>
  <div class="login-page">
    <div class="login-card">
      <h1>Gestor de Personal</h1>
      <p class="subtitle">Inicia sesión para continuar</p>

      <form @submit.prevent="handleSubmit">
        <label>
          Email
          <input
            v-model="email"
            type="email"
            required
            placeholder="admin@admin.com"
          />
        </label>

        <label>
          Contraseña
          <input
            v-model="password"
            type="password"
            required
            placeholder="••••••••"
          />
        </label>

        <button type="submit" :disabled="loading">
          {{ loading ? "Entrando..." : "Entrar" }}
        </button>

        <p v-if="error" class="error">
          {{ error }}
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/authStore";

const email = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

const router = useRouter();
const authStore = useAuthStore();

async function handleSubmit() {
  error.value = "";
  loading.value = true;

  try {
    await authStore.login(email.value, password.value);
    await router.push({ name: "dashboard" });
  } catch (err) {
    console.error(err);
    error.value = "Credenciales incorrectas o error de conexión.";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #0f172a;
}

.login-card {
  background: #020617;
  color: #e5e7eb;
  padding: 2rem 2.5rem;
  border-radius: 1rem;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.8);
  width: 100%;
  max-width: 400px;
}

h1 {
  margin: 0 0 0.25rem;
  font-size: 1.6rem;
}

.subtitle {
  margin-bottom: 1.5rem;
  color: #9ca3af;
  font-size: 0.9rem;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

label {
  display: flex;
  flex-direction: column;
  font-size: 0.85rem;
  color: #d1d5db;
}

input {
  margin-top: 0.25rem;
  padding: 0.6rem 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid #1f2937;
  background: #020617;
  color: #e5e7eb;
}

input:focus {
  outline: none;
  border-color: #3b82f6;
}

button {
  margin-top: 0.5rem;
  padding: 0.7rem;
  border-radius: 0.5rem;
  border: none;
  background: #3b82f6;
  color: white;
  font-weight: 600;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: default;
}

.error {
  margin-top: 0.5rem;
  color: #fca5a5;
  font-size: 0.85rem;
}
</style>
