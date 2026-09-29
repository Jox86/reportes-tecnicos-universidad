// src/pages/Login.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Lock, User, ArrowRight, Loader2, ShieldCheck } from "lucide-react";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setCargando(true);
    try {
      await login(username, password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(
        err.response?.status === 401
          ? "Credenciales incorrectas. Verifica tu usuario institucional."
          : "No se pudo conectar con el servidor. Intenta de nuevo."
      );
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="login-container">
      <div className="login-branding">
        <div className="branding-content">
          <div className="branding-logo">🛠️</div>
          <h1>Sistema de Reportes Técnicos</h1>
          <p>Gestión eficiente de incidentes y mantenimiento institucional.</p>
          <div className="ldap-badge">
            <ShieldCheck size={18} />
            <span>Autenticación vía LDAP Institucional</span>
          </div>
        </div>
        <div className="branding-footer">
          <p>© {new Date().getFullYear()} Universidad. Todos los derechos reservados.</p>
        </div>
      </div>

      <div className="login-form-section">
        <div className="login-form-wrapper">
          <div className="login-header">
            <h2>Bienvenido de nuevo</h2>
            <p>Ingresa tus credenciales institucionales.</p>
          </div>

          <form onSubmit={onSubmit} className="login-form">
            <div className="input-group">
              <label>Usuario Institucional</label>
              <div className="input-with-icon">
                <User size={20} className="input-icon" />
                <input
                  type="text"
                  placeholder="Ej. juan.perez"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoFocus
                  required
                />
              </div>
            </div>

            <div className="input-group">
              <label>Contraseña</label>
              <div className="input-with-icon">
                <Lock size={20} className="input-icon" />
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            {error && <div className="alerta alerta--error">{error}</div>}

            <button className="btn btn--primario btn--block" type="submit" disabled={cargando}>
              {cargando ? (
                <>
                  <Loader2 className="animate-spin" size={20} /> Validando en LDAP...
                </>
              ) : (
                <>
                  Iniciar Sesión <ArrowRight size={20} />
                </>
              )}
            </button>
          </form>
          
          <div className="login-footer-note">
            <p>Si eres administrador del sistema, usa tu cuenta local de Django.</p>
          </div>
        </div>
      </div>
    </div>
  );
}