import { createI18n } from "vue-i18n";
import es from "./locales/es.json";
import en from "./locales/en.json";

export const i18n = createI18n({
  legacy: false,        // para usar composable useI18n
  locale: "es",         // idioma por defecto
  fallbackLocale: "en", // por si falta alguna cadena
  messages: {
    es,
    en,
  },
});
