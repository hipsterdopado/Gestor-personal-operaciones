// src/services/absenceService.js
import axios from "axios";
import { API_BASE_URL } from "../config/apiConfig";
import { useAuthStore } from "../stores/authStore";

function getAuthHeaders() {
  const authStore = useAuthStore();
  return {
    Authorization: `Bearer ${authStore.token}`,
  };
}

export async function fetchMyAbsences() {
  const response = await axios.get(
    `${API_BASE_URL}/api/absence-requests/my`,
    {
      headers: getAuthHeaders(),
    }
  );
  return response.data; // array de ausencias
}

export async function createAbsenceRequest(payload) {
  // payload: { type, start_date, end_date, reason }
  const response = await axios.post(
    `${API_BASE_URL}/api/absence-requests/`,
    payload,
    {
      headers: {
        ...getAuthHeaders(),
        "Content-Type": "application/json",
      },
    }
  );
  return response.data;
}
