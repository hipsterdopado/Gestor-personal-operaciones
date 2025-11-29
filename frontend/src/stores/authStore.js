// src/stores/authStore.js
import { defineStore } from "pinia";
import { login as apiLogin } from "../services/authService";

const TOKEN_KEY = "gp_access_token";
const EMAIL_KEY = "gp_user_email";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || null,
    email: localStorage.getItem(EMAIL_KEY) || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    setSession(token, email) {
      this.token = token;
      this.email = email;

      if (token) {
        localStorage.setItem(TOKEN_KEY, token);
      } else {
        localStorage.removeItem(TOKEN_KEY);
      }

      if (email) {
        localStorage.setItem(EMAIL_KEY, email);
      } else {
        localStorage.removeItem(EMAIL_KEY);
      }
    },

    async login(email, password) {
      const data = await apiLogin(email, password);
      // Guardamos token y email
      this.setSession(data.access_token, email);
    },

    logout() {
      this.setSession(null, null);
    },
  },
});
