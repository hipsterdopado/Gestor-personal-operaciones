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

      <!-- Crear nueva ausencia -->
      <article class="card">
        <h2>{{ t("absence.form.title") }}</h2>

        <form class="absence-form" @submit.prevent="onCreateAbsence">
          <label>
            {{ t("absence.form.field.type") }}
            <select v-model="newAbsenceType">
              <option value="vacation">{{ t("absence.type.vacation") }}</option>
              <option value="sick">{{ t("absence.type.sick") }}</option>
              <option value="other">{{ t("absence.type.other") }}</option>
            </select>
          </label>

          <div class="dates-row">
            <label>
              {{ t("absence.form.field.from") }}
              <input v-model="newAbsenceStart" type="date" required />
            </label>

            <label>
              {{ t("absence.form.field.to") }}
              <input v-model="newAbsenceEnd" type="date" required />
            </label>
          </div>

          <label>
            {{ t("absence.form.field.reason") }}
            <textarea
              v-model="newAbsenceReason"
              rows="3"
              :placeholder="t('absence.form.placeholder.reason')"
            />
          </label>

          <button type="submit" class="primary" :disabled="creatingAbsence">
            {{ creatingAbsence ? t("absence.form.submitting") : t("absence.form.submit") }}
          </button>

          <p v-if="createAbsenceError" class="error">
            {{ createAbsenceError }}
          </p>
          <p v-if="createAbsenceSuccess" class="success">
            {{ createAbsenceSuccess }}
          </p>
        </form>
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
              <td>{{ t(`absence.type.${absence.type}`) }}</td>
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
import { fetchMyAbsences, createAbsenceRequest } from "../services/absenceService";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

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

const newAbsenceType = ref("vacation");
const newAbsenceStart = ref("");
const newAbsenceEnd = ref("");
const newAbsenceReason = ref("");
const creatingAbsence = ref(false);
const createAbsenceError = ref("");
const createAbsenceSuccess = ref("");

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

async function onCreateAbsence() {
  createAbsenceError.value = "";
  createAbsenceSuccess.value = "";
  creatingAbsence.value = true;

  try {
    if (!newAbsenceStart.value || !newAbsenceEnd.value) {
      throw new Error("Debes indicar fecha de inicio y fin.");
    }

    const payload = {
      type: newAbsenceType.value,
      start_date: newAbsenceStart.value,
      end_date: newAbsenceEnd.value,
      reason: newAbsenceReason.value || null,
    };

    await createAbsenceRequest(payload);
    createAbsenceSuccess.value = "Solicitud creada correctamente.";
    // recargar lista de ausencias
    await loadAbsences();
    // limpiar formulario
    newAbsenceType.value = "vacation";
    newAbsenceStart.value = "";
    newAbsenceEnd.value = "";
    newAbsenceReason.value = "";

  } catch (err) {
    console.error(err);
    createAbsenceError.value =
        err?.response?.data?.detail || t("absence.form.error");
  } finally {
    creatingAbsence.value = false;
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

onMounted(() => {
  loadTimeEntries();
  loadAbsences();
});
</script>

<style scoped lang="scss" src="../styles/dashboard.scss"></style>


