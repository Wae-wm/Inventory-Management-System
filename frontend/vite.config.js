import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// ตอนพัฒนา หน้าเว็บเรียก /api/... แล้ว Vite ส่งต่อไปที่ Backend (พอร์ต 8000)
// ทำให้เบราว์เซอร์เห็นว่าเป็นเว็บเดียวกัน จึงไม่ต้องตั้งค่า CORS ที่ Backend
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
