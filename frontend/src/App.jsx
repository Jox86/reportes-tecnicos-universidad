// src/App.jsx
import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";
import { useAuth } from "./context/AuthContext";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Estadisticas from "./pages/Estadisticas";
import Ranking from "./pages/Ranking"; // ← NUEVA
import ReportesList from "./pages/reportes/ReportesList";
import ReporteDetail from "./pages/reportes/ReporteDetail";
import ReporteForm from "./pages/reportes/ReporteForm";

const ROLES_GESTION = ["Administrador", "Tecnico"];

export default function App() {
  const { usuario, cargando } = useAuth();

  if (cargando) {
    return (
      <div className="pantalla-carga-global">
        <div className="spinner"></div>
        <p>Cargando sistema...</p>
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={usuario ? <Navigate to="/" replace /> : <Login />} />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="reportes" element={<ReportesList />} />
        <Route
          path="reportes/nuevo"
          element={
            <ProtectedRoute rolesPermitidos={ROLES_GESTION}>
              <ReporteForm />
            </ProtectedRoute>
          }
        />
        <Route
          path="reportes/:id/editar"
          element={
            <ProtectedRoute rolesPermitidos={ROLES_GESTION}>
              <ReporteForm modoEdicion />
            </ProtectedRoute>
          }
        />
        <Route path="reportes/:id" element={<ReporteDetail />} />
        <Route path="estadisticas" element={<Estadisticas />} />
        <Route path="ranking" element={<Ranking />} /> {/* ← NUEVA */}
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}