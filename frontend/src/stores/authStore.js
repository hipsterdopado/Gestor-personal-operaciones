// src/stores/authStore.js
import { defineStore } from "pinia";
import { login as apiLogin } from "../service/authService";

const TOKEN_KEY = "gp_access_token";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    setToken(token) {
      this.token = token;
      if (token) {
        localStorage.setItem(TOKEN_KEY, token);
      } else {
        localStorage.removeItem(TOKEN_KEY);
      }
    },

    async login(email, password) {
      // Llama al backend
      const data = await apiLogin(email, password);
      this.setToken(data.access_token);
    },

    logout() {
      this.setToken(null);
    },
  },
});
