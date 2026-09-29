// src/pages/reportes/ReporteForm.jsx
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../../api/client";
import { useAuth } from "../../context/AuthContext";
import { PRIORIDADES, TIPOS_TAREA } from "../../constants";
import { Plus, Trash2, Search, User } from "lucide-react";

const VACIO = {
  tipo_tarea: "activos_fijos",
  tipo_tarea_otro: "",
  descripcion: "",
  solucion: "",
  area: "",
  ubicacion: "",
  usuario_nombre: "",
  usuario_correo: "",
  usuario_cargo: "",
  equipos: [],
  prioridad: "media",
  tecnico_asignado: "",
};

export default function ReporteForm({ modoEdicion }) {
  const { id } = useParams();
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const esAdmin = usuario.is_superuser || usuario.roles.includes("Administrador");

  const [datos, setDatos] = useState(VACIO);
  const [areas, setAreas] = useState([]);
  const [tecnicos, setTecnicos] = useState([]);
  const [errores, setErrores] = useState({});
  const [guardando, setGuardando] = useState(false);
  const [buscandoUsuario, setBuscandoUsuario] = useState(false);

  useEffect(() => {
    api.get("/areas/").then(({ data }) => setAreas(data.results || data));
    if (esAdmin) {
      api.get("/tecnicos/").then(({ data }) => setTecnicos(data.results || data));
    }
    if (modoEdicion && id) {
      api.get(`/reportes/${id}/`).then(({ data }) => {
        setDatos({
          ...VACIO,
          ...data,
          area: data.area,
          ubicacion: data.ubicacion || "",
          equipos: data.equipos || [],
          tipo_tarea_otro: data.tipo_tarea_otro || "",
        });
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, modoEdicion]);

  function actualizar(campo, valor) {
    setDatos((d) => ({ ...d, [campo]: valor }));
  }

  // --- Búsqueda LDAP ---
  async function buscarUsuarioLDAP() {
    if (!datos.usuario_nombre) return;
    setBuscandoUsuario(true);
    try {
      const { data } = await api.get("/ldap/buscar/", { params: { q: datos.usuario_nombre } });
      if (data && data.length > 0) {
        const u = data[0];
        setDatos((d) => ({
          ...d,
          usuario_nombre: u.nombre_completo || u.username,
          usuario_correo: u.email || "",
          usuario_cargo: u.cargo || "",
        }));
      } else {
        alert("Usuario no encontrado en LDAP. Puedes llenar los datos manualmente.");
      }
    } catch (err) {
      alert("Error al buscar en LDAP. Llena los datos manualmente.");
    } finally {
      setBuscandoUsuario(false);
    }
  }

  // --- Manejo de equipos ---
  function agregarEquipo() {
    setDatos((d) => ({
      ...d,
      equipos: [...d.equipos, { codigo_activo: "", marca: "", modelo: "", serie: "" }],
    }));
  }

  function actualizarEquipo(index, campo, valor) {
    setDatos((d) => {
      const nuevos = [...d.equipos];
      nuevos[index] = { ...nuevos[index], [campo]: valor };
      return { ...d, equipos: nuevos };
    });
  }

  function eliminarEquipo(index) {
    setDatos((d) => ({
      ...d,
      equipos: d.equipos.filter((_, i) => i !== index),
    }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setGuardando(true);
    setErrores({});
    const payload = { ...datos };
    if (!payload.tecnico_asignado) delete payload.tecnico_asignado;
    if (payload.tipo_tarea !== "otros") delete payload.tipo_tarea_otro;

    try {
      if (modoEdicion) {
        await api.patch(`/reportes/${id}/`, payload);
        navigate(`/reportes/${id}`);
      } else {
        const { data } = await api.post("/reportes/", payload);
        // Redirigir al detalle del reporte recién creado
        navigate(`/reportes/${data.id}`);
      }
    } catch (err) {
      setErrores(err.response?.data || { general: "No se pudo guardar el reporte." });
    } finally {
      setGuardando(false);
    }
  }

  return (
    <div>
      <h1 className="titulo-pagina">{modoEdicion ? "Editar reporte" : "Nuevo reporte"}</h1>
      <p className="subtitulo-pagina">Completa los datos imprescindibles: área, ubicación y usuario.</p>

      <form className="tarjeta formulario formulario--ancho" onSubmit={onSubmit}>
        <div className="formulario__fila">
          <label>
            Tipo de tarea
            <select value={datos.tipo_tarea} onChange={(e) => actualizar("tipo_tarea", e.target.value)}>
              {TIPOS_TAREA.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </label>
          <label>
            Prioridad
            <select value={datos.prioridad} onChange={(e) => actualizar("prioridad", e.target.value)}>
              {PRIORIDADES.map((p) => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
          </label>
        </div>

        {datos.tipo_tarea === "otros" && (
          <label>
            Especifica el tipo de tarea
            <input
              type="text"
              value={datos.tipo_tarea_otro}
              onChange={(e) => actualizar("tipo_tarea_otro", e.target.value)}
              placeholder="Ej. Mantenimiento preventivo"
              required
            />
          </label>
        )}

        <div className="formulario__fila">
          <label>
            Área
            <select value={datos.area} onChange={(e) => actualizar("area", e.target.value)} required>
              <option value="">Selecciona un área…</option>
              {areas.map((a) => (
                <option key={a.id} value={a.id}>{a.nombre} ({a.tipo_area_nombre})</option>
              ))}
            </select>
          </label>
          <label>
            Ubicación (opcional)
            <input
              type="text"
              value={datos.ubicacion}
              onChange={(e) => actualizar("ubicacion", e.target.value)}
              placeholder="Ej. Edificio A, piso 3, oficina 302"
            />
          </label>
        </div>

        <h3>Usuario afectado (opcional)</h3>
        <div className="formulario__fila">
          <label>
            Nombre o usuario LDAP
            <div style={{ display: "flex", gap: 8 }}>
              <input
                type="text"
                value={datos.usuario_nombre}
                onChange={(e) => actualizar("usuario_nombre", e.target.value)}
                placeholder="Ej. juan.perez"
              />
              <button type="button" className="btn btn--secundario" onClick={buscarUsuarioLDAP} disabled={buscandoUsuario}>
                <Search size={16} /> {buscandoUsuario ? "..." : "Buscar"}
              </button>
            </div>
          </label>
          <label>
            Cargo / dependencia
            <input
              type="text"
              value={datos.usuario_cargo}
              onChange={(e) => actualizar("usuario_cargo", e.target.value)}
            />
          </label>
        </div>
        <label>
          Correo (para notificarle la resolución)
          <input
            type="email"
            value={datos.usuario_correo}
            onChange={(e) => actualizar("usuario_correo", e.target.value)}
          />
        </label>

        <h3>Equipos / activos</h3>
        {datos.equipos.map((eq, idx) => (
          <div key={idx} className="formulario__fila" style={{ border: "1px solid #eee", padding: 10, borderRadius: 8, marginBottom: 8 }}>
            <label>
              Código de activo
              <input type="text" value={eq.codigo_activo} onChange={(e) => actualizarEquipo(idx, "codigo_activo", e.target.value)} />
            </label>
            <label>
              Marca
              <input type="text" value={eq.marca} onChange={(e) => actualizarEquipo(idx, "marca", e.target.value)} />
            </label>
            <label>
              Modelo
              <input type="text" value={eq.modelo} onChange={(e) => actualizarEquipo(idx, "modelo", e.target.value)} />
            </label>
            <label>
              N.º de serie
              <input type="text" value={eq.serie} onChange={(e) => actualizarEquipo(idx, "serie", e.target.value)} />
            </label>
            <button type="button" className="btn btn--peligro" onClick={() => eliminarEquipo(idx)} style={{ alignSelf: "end" }}>
              <Trash2 size={16} />
            </button>
          </div>
        ))}
        <button type="button" className="btn btn--secundario" onClick={agregarEquipo}>
          <Plus size={16} /> Agregar otro equipo
        </button>

        <label>
          Descripción del problema / tarea
          <textarea
            rows={4}
            value={datos.descripcion}
            onChange={(e) => actualizar("descripcion", e.target.value)}
            required
          />
        </label>

        {modoEdicion && (
          <label>
            Solución / notas técnicas
            <textarea rows={3} value={datos.solucion} onChange={(e) => actualizar("solucion", e.target.value)} />
          </label>
        )}

        {esAdmin && (
          <label>
            Técnico asignado
            <select value={datos.tecnico_asignado} onChange={(e) => actualizar("tecnico_asignado", e.target.value)}>
              <option value="">Sin asignar</option>
              {tecnicos.map((t) => (
                <option key={t.id} value={t.id}>{t.nombre_completo}</option>
              ))}
            </select>
          </label>
        )}

        {errores.general && <div className="alerta alerta--error">{errores.general}</div>}

        <div className="formulario__acciones">
          <button className="btn btn--primario" type="submit" disabled={guardando}>
            {guardando ? "Guardando…" : modoEdicion ? "Guardar cambios" : "Crear reporte"}
          </button>
        </div>
      </form>
    </div>
  );
}

function CampoError({ error }) {
  if (!error) return null;
  return <div className="alerta alerta--error">{Array.isArray(error) ? error.join(", ") : error}</div>;
}