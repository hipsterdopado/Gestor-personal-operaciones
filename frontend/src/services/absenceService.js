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
