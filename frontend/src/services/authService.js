import axios from "axios";
import { API_BASE_URL } from "../config/apiConfig";

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Login contra FastAPI
// IMPORTANTE: el backend espera username + password en formulario
export async function login(email, password) {
  const formData = new URLSearchParams();
  // El backend usa "username", pero nosotros le pasamos el email ahí
  formData.append("username", email);
  formData.append("password", password);

  const response = await api.post("/api/auth/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  // Devuelve { access_token, token_type }
  return response.data;
}
