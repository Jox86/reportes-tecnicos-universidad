// src/pages/Ranking.jsx
import { useEffect, useState } from "react";
import {
  Trophy,
  Star,
  TrendingUp,
  Clock,
  Medal,
  User,
  ShieldCheck,
  LogIn,
} from "lucide-react";
import api from "../api/client";

const TITULOS = {
  5: "Maestro Técnico",
  4: "Experto",
  3: "Avanzado",
  2: "Competente",
  1: "Aprendiz",
  0: "Novato",
};

export default function Ranking() {
  const [ranking, setRanking] = useState([]);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    api.get("/estadisticas/ranking/")
      .then(({ data }) => setRanking(data || []))
      .catch(() => setRanking([]))
      .finally(() => setCargando(false));
  }, []);

  // ¿Ya se animó esta sesión?
  const yaAnimo = sessionStorage.getItem("ranking_animado") === "1";
  if (!cargando && !yaAnimo && ranking.length > 0) {
    sessionStorage.setItem("ranking_animado", "1");
  }

  return (
    <div className="ranking-page">
      <header className="encabezado-lista">
        <div>
          <h1 className="titulo-pagina">
            <Trophy size={22} /> Ranking de Técnicos
          </h1>
          <p className="subtitulo-pagina">
            Clasificación según reportes resueltos y tiempo de resolución.
            Los técnicos sin reportes aparecen ordenados por su último inicio de sesión.
          </p>
        </div>
      </header>

      {cargando ? (
        <p>Cargando ranking…</p>
      ) : ranking.length === 0 ? (
        <div className="tarjeta">
          <p className="sin-datos">Aún no hay técnicos registrados en el sistema.</p>
        </div>
      ) : (
        <div className="ranking-cards">
          {ranking.map((t, index) => {
            const estrellas = t.estrellas ?? 0;
            const esTop1 = index === 0 && t.reportes_resueltos > 0;
            const sinReportes = t.reportes_resueltos === 0;

            return (
              <div
                key={t.id}
                className={`ranking-card ${esTop1 ? "ranking-card--top" : ""} ${sinReportes ? "ranking-card--sin-datos" : ""}`}
              >
                <div className="ranking-card__posicion">
                  {index === 0 && <Medal size={28} color="#f59e0b" />}
                  {index === 1 && <Medal size={28} color="#94a3b8" />}
                  {index === 2 && <Medal size={28} color="#a16207" />}
                  {index > 2 && (
                    <span className="ranking-card__num">#{index + 1}</span>
                  )}
                </div>

                <div className="ranking-card__avatar">
                  {(t.nombre || "?").charAt(0).toUpperCase()}
                </div>

                <div className="ranking-card__info">
                  <h3>
                    {t.nombre}
                    {t.es_admin && (
                      <span className="ranking-card__badge-admin" title="Administrador">
                        <ShieldCheck size={12} />
                      </span>
                    )}
                  </h3>
                  <span className="ranking-card__titulo">
                    {sinReportes ? "Sin reportes aún" : TITULOS[estrellas]}
                  </span>

                  <div
                    className={`ranking-card__estrellas ${
                      esTop1 && !yaAnimo ? "animar" : ""
                    }`}
                  >
                    {[1, 2, 3, 4, 5].map((n) => (
                      <Star
                        key={n}
                        size={18}
                        className={n <= estrellas ? "estrella-activa" : "estrella-inactiva"}
                        style={esTop1 && !yaAnimo ? { animationDelay: `${n * 0.15}s` } : {}}
                        fill={n <= estrellas ? "#f59e0b" : "none"}
                        stroke={n <= estrellas ? "#f59e0b" : "#cbd5e1"}
                      />
                    ))}
                  </div>
                </div>

                <div className="ranking-card__stats">
                  {t.reportes_resueltos > 0 ? (
                    <div className="stat">
                      <TrendingUp size={16} />
                      <span>{t.reportes_resueltos}</span>
                      <small>resueltos</small>
                    </div>
                  ) : (
                    <div className="stat stat--vacio">
                      <User size={16} />
                      <small>Sin asignaciones</small>
                    </div>
                  )}

                  {t.tiempo_promedio_horas != null && (
                    <div className="stat">
                      <Clock size={16} />
                      <span>{t.tiempo_promedio_horas}h</span>
                      <small>promedio</small>
                    </div>
                  )}

                  {sinReportes && t.ultimo_login && (
                    <div className="stat stat--login">
                      <LogIn size={16} />
                      <small>{formatearUltimoLogin(t.ultimo_login)}</small>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ============================================================
// Utilidad: formatear fecha de último login
// ============================================================
function formatearUltimoLogin(isoString) {
  if (!isoString) return "Nunca";
  const fecha = new Date(isoString);
  const ahora = new Date();
  const diffMs = ahora - fecha;
  const diffSeg = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSeg / 60);
  const diffHoras = Math.floor(diffMin / 60);
  const diffDias = Math.floor(diffHoras / 24);

  if (diffSeg < 60) return "hace unos segundos";
  if (diffMin < 60) return `hace ${diffMin} min`;
  if (diffHoras < 24) return `hace ${diffHoras} h`;
  if (diffDias < 30) return `hace ${diffDias} día${diffDias > 1 ? "s" : ""}`;
  return fecha.toLocaleDateString("es-CO");
}