// src/hooks/useContador.js
// Anima un número desde 0 hasta su valor final (respeta "reducir movimiento").
import { useEffect, useState } from "react";

export default function useContador(objetivo, duracion = 900) {
  const destino = Number(objetivo);
  const valido = objetivo !== null && objetivo !== undefined && objetivo !== "" && Number.isFinite(destino);
  const [valor, setValor] = useState(valido ? 0 : objetivo);

  useEffect(() => {
    if (!valido) {
      setValor(objetivo);
      return undefined;
    }
    const reducir = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    if (reducir) {
      setValor(destino);
      return undefined;
    }
    const entero = Number.isInteger(destino);
    const inicio = performance.now();
    let raf;
    const paso = (ahora) => {
      const p = Math.min((ahora - inicio) / duracion, 1);
      const suave = 1 - Math.pow(1 - p, 3);
      const actual = destino * suave;
      setValor(entero ? Math.round(actual) : Math.round(actual * 10) / 10);
      if (p < 1) raf = requestAnimationFrame(paso);
    };
    raf = requestAnimationFrame(paso);
    return () => cancelAnimationFrame(raf);
  }, [objetivo, duracion]); // eslint-disable-line react-hooks/exhaustive-deps

  return valor;
}