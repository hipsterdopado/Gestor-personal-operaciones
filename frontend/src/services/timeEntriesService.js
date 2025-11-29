// src/services/timeEntriesService.js
import axios from "axios";
import { API_BASE_URL } from "../config/apiConfig";
import { useAuthStore } from "../stores/authStore";

function getAuthHeaders() {
  const authStore = useAuthStore();
  return {
    Authorization: `Bearer ${authStore.token}`,
  };
}

export async function fetchMyTimeEntries() {
  const response = await axios.get(`${API_BASE_URL}/api/time-entries/my`, {
    headers: getAuthHeaders(),
  });
  return response.data; // array de time entries
}

export async function clockIn(notes = "") {
  const response = await axios.post(
    `${API_BASE_URL}/api/time-entries/clock-in`,
    { notes },
    {
      headers: getAuthHeaders(),
    }
  );
  return response.data;
}

export async function clockOut() {
  const response = await axios.post(
    `${API_BASE_URL}/api/time-entries/clock-out`,
    {},
    {
      headers: getAuthHeaders(),
    }
  );
  return response.data;
}
