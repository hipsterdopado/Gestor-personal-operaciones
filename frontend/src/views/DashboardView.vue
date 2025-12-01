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
            {{ formatDateTime(lastEntry.clock_in) }}
            <br />
            <strong>Salida:</strong>
            {{ lastEntry.clock_out ? formatDateTime(lastEntry.clock_out) : "—" }}

          </p>

          <p class="small">
            Horas trabajadas hoy:
            <br />
            <strong>{{ formatHours(totalHoursToday) }}</strong>
          </p>

          <p class="small">
            Horas trabajadas esta semana:
            <br />
            <strong>{{ formatHours(totalHoursWeek) }}</strong>
          </p>

          <p class="small">
            Horas trabajadas este mes:
            <br />
            <strong>{{ formatHours(totalHoursMonth) }}</strong>
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
              <td>{{ formatDateTime(entry.clock_in) }}</td>
              <td>
                {{ entry.clock_out ? formatDateTime(entry.clock_out) : "—" }}
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
              <th>Mensaje</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="absence in absences" :key="absence.id">
              <td>{{ formatAbsenceType(absence.type) }}</td>
              <td>{{ formatDate(absence.start_date) }}</td>
              <td>{{ formatDate(absence.end_date) }}</td>
              <td>
                <span class="pill" :class="statusClass(absence.status)">
                  {{ humanStatus(absence.status) }}
                </span>
              </td>
              <td>{{ formatAbsenceMessage(absence) }}</td>
            </tr>
          </tbody>
        </table>
      </article>
      <!-- Histórico de horas mensuales -->
      <article class="card full">
        <h2>Histórico mensual de horas</h2>
        <p v-if="monthlyHoursHistory.length === 0" class="small">
          Aún no hay horas registradas
                    </p>

            <table v-else class="data-table">
              <thead>
                <tr>
                  <th>Mes</th>
                  <th>Horas trabajadas</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in monthlyHoursHistory" :key="item.key">
                  <td>{{ item.label }}</td>
                  <td>{{ formatHours(item.hours) }}</td>
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

function formatAbsenceType(type) {
  if (!type) return "";
  const key = `absence.type.${type}`;
  const translated = t(key);
  // Si no hay traducción, vue-i18n devuelve la propia clave
  return translated === key ? type : translated;
}

function formatAbsenceMessage(absence) {
  if (!absence) return "";

  const message =
    absence.review_message ??
    absence.manager_comment ??
    absence.comment ??
    absence.message ??
    null;

  if (!message || message.trim() === "") {
    return "—";
  }

  return message;
}

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
function formatDateTime(value) {
  if (!value) return "";
  return new Date(value).toLocaleString("es-ES", {
    dateStyle: "short",
    timeStyle: "medium",
  });
}

function formatDate(value) {
  if (!value) return "";
  return new Date(value).toLocaleDateString("es-ES", {
    dateStyle: "short",
  });
}

// --- Cálculo de horas trabajadas ---

function diffHours(start, end) {
  const ms = end.getTime() - start.getTime();
  if (!Number.isFinite(ms) || ms <= 0) return 0;
  return ms / (1000 * 60 * 60);
}

const hoursSummary = computed(() => {
  const entries = timeEntries.value || [];
  const now = new Date();

  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());

  // Lunes como inicio de semana
  const weekDay = todayStart.getDay(); // 0 = domingo, 1 = lunes...
  const diffToMonday = (weekDay + 6) % 7;
  const weekStart = new Date(todayStart);
  weekStart.setDate(todayStart.getDate() - diffToMonday);

  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

  let today = 0;
  let week = 0;
  let month = 0;

  const monthlyMap = new Map(); // key: YYYY-MM, value: horas

  for (const entry of entries) {
    if (!entry.clock_in) continue;

    const start = new Date(entry.clock_in);
    const end = entry.clock_out ? new Date(entry.clock_out) : now;
    const hours = diffHours(start, end);
    if (hours === 0) continue;

    // Día actual (entrada que empieza hoy)
    if (start >= todayStart) {
      today += hours;
    }

    // Semana actual
    if (start >= weekStart) {
      week += hours;
    }

    // Mes actual
    if (start >= monthStart) {
      month += hours;
    }

    // Histórico mensual
    const ymKey = `${start.getFullYear()}-${String(
      start.getMonth() + 1
    ).padStart(2, "0")}`;
    monthlyMap.set(ymKey, (monthlyMap.get(ymKey) || 0) + hours);
  }

  const monthsHistory = Array.from(monthlyMap.entries())
    .map(([key, hours]) => {
      const [year, monthIndex] = key.split("-");
      const date = new Date(Number(year), Number(monthIndex) - 1, 1);
      const label = date.toLocaleDateString("es-ES", {
        month: "long",
        year: "numeric",
      });
      return { key, label, hours };
    })
    // Ordenar de más reciente a más antiguo
    .sort((a, b) => b.key.localeCompare(a.key));

  return {
    today,
    week,
    month,
    monthsHistory,
  };
});

const totalHoursToday = computed(() => hoursSummary.value.today);
const totalHoursWeek = computed(() => hoursSummary.value.week);
const totalHoursMonth = computed(() => hoursSummary.value.month);
const monthlyHoursHistory = computed(() => hoursSummary.value.monthsHistory);

function formatHours(hours) {
  if (!Number.isFinite(hours) || hours <= 0) return "0 h";

  const rounded = Math.round(hours * 100) / 100;
  return (
    rounded.toLocaleString("es-ES", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }) + " h"
  );
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


