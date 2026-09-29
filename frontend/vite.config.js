   import { defineConfig } from "vite";
   import react from "@vitejs/plugin-react";

   export default defineConfig({
     plugins: [react()],
     server: {
      host: '0.0.0.0', // Permite acceso desde la red local
      port: 5173,
       //host: true, // permite entrar por 10.6.45.217:5173
       proxy: {
         "/api": {
           target: "http://127.0.0.1:8000",
           changeOrigin: true, // evita el error DisallowedHost en Django
         },
       },
     },
   });