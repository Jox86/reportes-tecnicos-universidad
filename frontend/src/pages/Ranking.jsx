// src/pages/Ranking.jsx
import { useEffect, useState } from "react";
import { Trophy, Star, Award, TrendingUp, Clock, Medal } from "lucide-react";
import api from "../api/client";

// Escala de estrellas según reportes resueltos
function calcularEstrellas(resueltos) {
  if (resueltos >= 20) return 5;
  if (resueltos >= 15) return 4;
  if (resueltos >= 10) return 3;
  if (resueltos >= 5) return 2;
  if (resueltos >= 1) return 1;
  return 0;
}

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
            Clasificación automática según reportes resueltos y tiempo de resolución.
          </p>
        </div>
      </header>

      {cargando ? (
        <p>Cargando ranking…</p>
      ) : ranking.length === 0 ? (
        <div className="tarjeta">
          <p className="sin-datos">Aún no hay técnicos con reportes resueltos.</p>
        </div>
      ) : (
        <div className="ranking-cards">
          {ranking.map((t, index) => {
            const estrellas = calcularEstrellas(t.reportes_resueltos);
            const esTop1 = index === 0;

            return (
              <div
                key={t.id}
                className={`ranking-card ${esTop1 ? "ranking-card--top" : ""}`}
              >
                <div className="ranking-card__posicion">
                  {index === 0 && <Medal size={28} color="#f59e0b" />}
                  {index === 1 && <Medal size={28} color="#94a3b8" />}
                  {index === 2 && <Medal size={28} color="#a16207" />}
                  {index > 2 && <span className="ranking-card__num">#{index + 1}</span>}
                </div>

                <div className="ranking-card__avatar">
                  {(t.nombre || "?").charAt(0).toUpperCase()}
                </div>

                <div className="ranking-card__info">
                  <h3>{t.nombre}</h3>
                  <span className="ranking-card__titulo">{TITULOS[estrellas]}</span>

                  <div className={`ranking-card__estrellas ${esTop1 && !yaAnimo ? "animar" : ""}`}>
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
                  <div className="stat">
                    <TrendingUp size={16} />
                    <span>{t.reportes_resueltos}</span>
                    <small>resueltos</small>
                  </div>
                  {t.tiempo_promedio_horas != null && (
                    <div className="stat">
                      <Clock size={16} />
                      <span>{t.tiempo_promedio_horas}h</span>
                      <small>promedio</small>
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