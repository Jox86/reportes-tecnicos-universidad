# apps/exports/pdf.py
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generar_pdf_reporte_individual(reporte):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"<b>Reporte {reporte.codigo}</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    datos = [
        ["Campo", "Valor"],
        ["Tipo de Tarea", reporte.tipo_tarea.nombre if reporte.tipo_tarea else ""],
        ["Área", reporte.area.nombre if reporte.area else ""],
        ["Ubicación", reporte.ubicacion or "—"],
        ["Usuario Afectado", reporte.usuario_nombre or "—"],
        ["Correo", reporte.usuario_correo or "—"],
        ["Cargo", reporte.usuario_cargo or "—"],
        ["Prioridad", reporte.get_prioridad_display()],
        ["Estado", reporte.get_estado_display()],
        ["Técnico Asignado", reporte.tecnico_nombre or "Sin asignar"],
        ["Fecha Creación", reporte.fecha_creacion.strftime("%Y-%m-%d %H:%M") if reporte.fecha_creacion else "—"],
        ["Fecha Resolución", reporte.fecha_resolucion.strftime("%Y-%m-%d %H:%M") if reporte.fecha_resolucion else "—"],
        ["Tiempo (h)", str(reporte.tiempo_resolucion_horas or "—")],
    ]
    tabla = Table(datos, colWidths=[150, 350])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(tabla)
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Descripción</b>", styles["Heading3"]))
    story.append(Paragraph(reporte.descripcion or "—", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Solución / Notas técnicas</b>", styles["Heading3"]))
    story.append(Paragraph(reporte.solucion or "Sin registrar aún.", styles["BodyText"]))
    story.append(Spacer(1, 12))

    if reporte.equipos.exists():
        story.append(Paragraph("<b>Equipos / Activos</b>", styles["Heading3"]))
        eq_data = [["Código", "Marca", "Modelo", "Serie"]]
        for eq in reporte.equipos.all():
            eq_data.append([eq.codigo_activo or "—", eq.marca or "—", eq.modelo or "—", eq.serie or "—"])
        eq_tabla = Table(eq_data)
        eq_tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(eq_tabla)

    doc.build(story)
    buffer.seek(0)
    return buffer


# Alias para compatibilidad
generar_pdf_reporte = generar_pdf_reporte_individual