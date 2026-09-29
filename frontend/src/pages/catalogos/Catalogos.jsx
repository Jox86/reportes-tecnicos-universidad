import { useEffect, useState } from "react";
import api from "../../api/client";

const PESTAÑAS = ["Tipos de área", "Áreas", "Ubicaciones"];

export default function Catalogos() {
  const [pestaña, setPestaña] = useState(0);

  return (
    <div>
      <h1 className="titulo-pagina">Catálogos</h1>
      <p className="subtitulo-pagina">Datos base usados en los reportes: tipo de área, área y ubicación.</p>

      <div className="pestañas">
        {PESTAÑAS.map((p, i) => (
          <button
            key={p}
            className={`pestañas__item ${pestaña === i ? "pestañas__item--activo" : ""}`}
            onClick={() => setPestaña(i)}
          >
            {p}
          </button>
        ))}
      </div>

      {pestaña === 0 && <TiposArea />}
      {pestaña === 1 && <Areas />}
      {pestaña === 2 && <Ubicaciones />}
    </div>
  );
}

function TiposArea() {
  const [items, setItems] = useState([]);
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");

  const cargar = () => api.get("/tipos-area/").then(({ data }) => setItems(data.results || data));
  useEffect(() => {
    cargar();
  }, []);

  async function crear(e) {
    e.preventDefault();
    await api.post("/tipos-area/", { nombre, descripcion });
    setNombre("");
    setDescripcion("");
    cargar();
  }

  async function eliminar(id) {
    if (!confirm("¿Eliminar este tipo de área?")) return;
    await api.delete(`/tipos-area/${id}/`);
    cargar();
  }

  return (
    <div className="tarjeta">
      <form className="formulario formulario--linea" onSubmit={crear}>
        <input placeholder="Nombre" value={nombre} onChange={(e) => setNombre(e.target.value)} required />
        <input
          placeholder="Descripción (opcional)"
          value={descripcion}
          onChange={(e) => setDescripcion(e.target.value)}
        />
        <button className="btn btn--primario" type="submit">
          Agregar
        </button>
      </form>
      <table className="tabla">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Descripción</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((i) => (
            <tr key={i.id}>
              <td>{i.nombre}</td>
              <td>{i.descripcion || "—"}</td>
              <td>
                <button className="btn btn--fantasma btn--peligro" onClick={() => eliminar(i.id)}>
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Areas() {
  const [items, setItems] = useState([]);
  const [tipos, setTipos] = useState([]);
  const [form, setForm] = useState({ nombre: "", tipo_area: "", responsable: "" });

  const cargar = () => api.get("/areas/").then(({ data }) => setItems(data.results || data));
  useEffect(() => {
    cargar();
    api.get("/tipos-area/").then(({ data }) => setTipos(data.results || data));
  }, []);

  async function crear(e) {
    e.preventDefault();
    await api.post("/areas/", form);
    setForm({ nombre: "", tipo_area: "", responsable: "" });
    cargar();
  }

  async function eliminar(id) {
    if (!confirm("¿Eliminar esta área?")) return;
    await api.delete(`/areas/${id}/`);
    cargar();
  }

  return (
    <div className="tarjeta">
      <form className="formulario formulario--linea" onSubmit={crear}>
        <input
          placeholder="Nombre del área"
          value={form.nombre}
          onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
          required
        />
        <select
          value={form.tipo_area}
          onChange={(e) => setForm((f) => ({ ...f, tipo_area: e.target.value }))}
          required
        >
          <option value="">Tipo de área…</option>
          {tipos.map((t) => (
            <option key={t.id} value={t.id}>
              {t.nombre}
            </option>
          ))}
        </select>
        <input
          placeholder="Responsable (opcional)"
          value={form.responsable}
          onChange={(e) => setForm((f) => ({ ...f, responsable: e.target.value }))}
        />
        <button className="btn btn--primario" type="submit">
          Agregar
        </button>
      </form>
      <table className="tabla">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Tipo de área</th>
            <th>Responsable</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((i) => (
            <tr key={i.id}>
              <td>{i.nombre}</td>
              <td>{i.tipo_area_nombre}</td>
              <td>{i.responsable || "—"}</td>
              <td>
                <button className="btn btn--fantasma btn--peligro" onClick={() => eliminar(i.id)}>
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Ubicaciones() {
  const [items, setItems] = useState([]);
  const [areas, setAreas] = useState([]);
  const [form, setForm] = useState({ nombre: "", area: "", edificio: "", piso: "" });

  const cargar = () => api.get("/ubicaciones/").then(({ data }) => setItems(data.results || data));
  useEffect(() => {
    cargar();
    api.get("/areas/").then(({ data }) => setAreas(data.results || data));
  }, []);

  async function crear(e) {
    e.preventDefault();
    await api.post("/ubicaciones/", form);
    setForm({ nombre: "", area: "", edificio: "", piso: "" });
    cargar();
  }

  async function eliminar(id) {
    if (!confirm("¿Eliminar esta ubicación?")) return;
    await api.delete(`/ubicaciones/${id}/`);
    cargar();
  }

  return (
    <div className="tarjeta">
      <form className="formulario formulario--linea" onSubmit={crear}>
        <input
          placeholder="Nombre"
          value={form.nombre}
          onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
          required
        />
        <select value={form.area} onChange={(e) => setForm((f) => ({ ...f, area: e.target.value }))} required>
          <option value="">Área…</option>
          {areas.map((a) => (
            <option key={a.id} value={a.id}>
              {a.nombre}
            </option>
          ))}
        </select>
        <input
          placeholder="Edificio"
          value={form.edificio}
          onChange={(e) => setForm((f) => ({ ...f, edificio: e.target.value }))}
        />
        <input
          placeholder="Piso"
          value={form.piso}
          onChange={(e) => setForm((f) => ({ ...f, piso: e.target.value }))}
        />
        <button className="btn btn--primario" type="submit">
          Agregar
        </button>
      </form>
      <table className="tabla">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Área</th>
            <th>Edificio</th>
            <th>Piso</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((i) => (
            <tr key={i.id}>
              <td>{i.nombre}</td>
              <td>{i.area_nombre}</td>
              <td>{i.edificio || "—"}</td>
              <td>{i.piso || "—"}</td>
              <td>
                <button className="btn btn--fantasma btn--peligro" onClick={() => eliminar(i.id)}>
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
