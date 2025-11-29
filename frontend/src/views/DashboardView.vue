<!-- src/views/DashboardView.vue -->
<template>
  <div class="dashboard">
    <header class="top-bar">
      <div>
        <h1>Panel de control</h1>
        <p class="subtitle">
          Hola
          <strong>{{ authStore.email || "usuario" }}</strong>,
          aquí tienes un resumen rápido de tu actividad.
        </p>
      </div>

      <button class="logout-btn" @click="handleLogout">
        Cerrar sesión
      </button>
    </header>

    <section class="grid">
      <!-- Estado actual -->
      <article class="card">
        <h2>Estado actual</h2>

        <p v-if="loadingTimeEntries">Cargando fichajes...</p>
        <p v-else-if="timeEntries.length === 0">
          Aún no tienes ningún fichaje registrado.
        </p>
        <template v-else>
          <p class="status-text">
            <span
              class="pill"
              :class="{
                open: !!openEntry,
                closed: !openEntry,
              }"
            >
              {{ openEntry ? "En jornada" : "Fuera de jornada" }}
            </span>
          </p>

          <p class="small">
            Último fichaje:
            <br />
            <strong>Entrada:</strong>
            {{ formatDate(lastEntry.clock_in) }}
            <br />
            <strong>Salida:</strong>
            {{ lastEntry.clock_out ? formatDate(lastEntry.clock_out) : "—" }}
          </p>
        </template>

        <div class="actions">
          <button
            class="primary"
            @click="onClockIn"
            :disabled="!!openEntry || actionLoading"
          >
            {{ actionLoading && actionType === "in" ? "Fichando..." : "Fichar entrada" }}
          </button>

          <button
            class="secondary"
            @click="onClockOut"
            :disabled="!openEntry || actionLoading"
          >
            {{ actionLoading && actionType === "out" ? "Fichando..." : "Fichar salida" }}
          </button>
        </div>

        <p v-if="actionError" class="error">{{ actionError }}</p>
      </article>

      <!-- Mis fichajes recientes -->
      <article class="card">
        <h2>Mis fichajes recientes</h2>

        <p v-if="loadingTimeEntries">Cargando...</p>
        <p v-else-if="timeEntries.length === 0">
          No hay fichajes que mostrar todavía.
        </p>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>Entrada</th>
              <th>Salida</th>
              <th>Notas</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in timeEntries.slice(0, 5)" :key="entry.id">
              <td>{{ formatDate(entry.clock_in) }}</td>
              <td>
                {{ entry.clock_out ? formatDate(entry.clock_out) : "—" }}
              </td>
              <td>{{ entry.notes || "—" }}</td>
            </tr>
          </tbody>
        </table>
      </article>

      <!-- Mis ausencias -->
      <article class="card full">
        <h2>Mis solicitudes de ausencia</h2>

        <p v-if="loadingAbsences">Cargando ausencias...</p>
        <p v-else-if="absences.length === 0">
          No tienes solicitudes de ausencia registradas.
        </p>

        <table v-else class="data-table">
          <thead>
            <tr>
              <th>Tipo</th>
              <th>Desde</th>
              <th>Hasta</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="absence in absences" :key="absence.id">
              <td>{{ absence.type }}</td>
              <td>{{ formatDate(absence.start_date) }}</td>
              <td>{{ formatDate(absence.end_date) }}</td>
              <td>
                <span class="pill" :class="statusClass(absence.status)">
                  {{ humanStatus(absence.status) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </article>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/authStore";
import {
  fetchMyTimeEntries,
  clockIn,
  clockOut,
} from "../services/timeEntriesService";
import { fetchMyAbsences } from "../services/absenceService";

const router = useRouter();
const authStore = useAuthStore();

// Estado fichajes
const timeEntries = ref([]);
const loadingTimeEntries = ref(false);

// Estado ausencias
const absences = ref([]);
const loadingAbsences = ref(false);

// Acciones fichar
const actionLoading = ref(false);
const actionType = ref(null); // "in" | "out"
const actionError = ref("");

// Derivados
const openEntry = computed(() =>
  timeEntries.value.find((e) => !e.clock_out) || null
);

const lastEntry = computed(() => {
  if (timeEntries.value.length === 0) return null;
  // asumiendo que vienen ordenados, si no, ordenamos por clock_in
  return timeEntries.value[0];
});

// Helpers
function formatDate(value) {
  if (!value) return "";
  return new Date(value).toLocaleString();
}

function humanStatus(status) {
  if (!status) return "";
  const map = {
    pending: "Pendiente",
    approved: "Aprobada",
    rejected: "Rechazada",
  };
  return map[status] || status;
}

function statusClass(status) {
  return {
    pending: status === "pending",
    approved: status === "approved",
    rejected: status === "rejected",
  };
}

// Acciones
async function loadTimeEntries() {
  loadingTimeEntries.value = true;
  try {
    const data = await fetchMyTimeEntries();
    // ordenamos de más reciente a más antiguo por clock_in
    timeEntries.value = [...data].sort(
      (a, b) => new Date(b.clock_in) - new Date(a.clock_in)
    );
  } catch (err) {
    console.error("Error cargando fichajes", err);
  } finally {
    loadingTimeEntries.value = false;
  }
}

async function loadAbsences() {
  loadingAbsences.value = true;
  try {
    const data = await fetchMyAbsences();
    absences.value = [...data].sort(
      (a, b) => new Date(b.start_date) - new Date(a.start_date)
    );
  } catch (err) {
    console.error("Error cargando ausencias", err);
  } finally {
    loadingAbsences.value = false;
  }
}

async function onClockIn() {
  actionError.value = "";
  actionType.value = "in";
  actionLoading.value = true;
  try {
    await clockIn();
    await loadTimeEntries();
  } catch (err) {
    console.error(err);
    actionError.value = "No se ha podido fichar la entrada.";
  } finally {
    actionLoading.value = false;
    actionType.value = null;
  }
}

async function onClockOut() {
  actionError.value = "";
  actionType.value = "out";
  actionLoading.value = true;
  try {
    await clockOut();
    await loadTimeEntries();
  } catch (err) {
    console.error(err);
    actionError.value = "No se ha podido fichar la salida.";
  } finally {
    actionLoading.value = false;
    actionType.value = null;
  }
}

function handleLogout() {
  authStore.logout();
  router.push({ name: "login" });
}

// Cargar datos al entrar en el dashboard
onMounted(() => {
  loadTimeEntries();
  loadAbsences();
});
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  padding: 1.5rem 2rem;
  background: #020617;
  color: #e5e7eb;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.subtitle {
  margin-top: 0.25rem;
  color: #9ca3af;
  font-size: 0.9rem;
}

.logout-btn {
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  border: 1px solid #4b5563;
  background: transparent;
  color: #e5e7eb;
  cursor: pointer;
  font-size: 0.85rem;
}

.logout-btn:hover {
  background: #111827;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.25rem;
}

.card {
  background: #020617;
  border-radius: 1rem;
  padding: 1.25rem 1.5rem;
  border: 1px solid #1f2937;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.7);
}

.card.full {
  grid-column: 1 / -1;
}

.card h2 {
  margin: 0 0 0.75rem;
  font-size: 1.1rem;
}

.status-text {
  margin: 0.5rem 0 0.75rem;
}

.small {
  font-size: 0.85rem;
  color: #9ca3af;
}

.actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

button.primary,
button.secondary {
  flex: 1;
  padding: 0.6rem 0.8rem;
  border-radius: 0.7rem;
  border: none;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
}

button.primary {
  background: #3b82f6;
  color: white;
}

button.secondary {
  background: #111827;
  color: #e5e7eb;
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

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.data-table th,
.data-table td {
  padding: 0.4rem 0.3rem;
  border-bottom: 1px solid #111827;
}

.data-table th {
  text-align: left;
  color: #9ca3af;
  font-weight: 500;
}

.data-table tr:last-child td {
  border-bottom: none;
}

.pill {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.75rem;
}

.pill.open {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
}

.pill.closed {
  background: rgba(148, 163, 184, 0.15);
  color: #e5e7eb;
}

.pill.pending {
  background: rgba(234, 179, 8, 0.15);
  color: #facc15;
}

.pill.approved {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
}

.pill.rejected {
  background: rgba(248, 113, 113, 0.15);
  color: #fca5a5;
}

@media (max-width: 640px) {
  .dashboard {
    padding: 1rem;
  }
}
</style>
