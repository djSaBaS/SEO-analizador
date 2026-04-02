"""Vistas Django para flujo interno de auditorías SEO."""

# Importa datetime para mostrar fechas legibles en dashboard.
from datetime import datetime

# Importa Path para resolver rutas de salida en disco.
from pathlib import Path

# Importa FileResponse para descargas seguras de entregables.
from django.http import FileResponse, Http404, HttpRequest, HttpResponse

# Importa helpers de render y redirección de Django.
from django.shortcuts import get_object_or_404, redirect, render

# Importa utilidades de URL para redirecciones nombradas.
from django.urls import reverse

# Importa decorador para exigir método HTTP en vistas.
from django.views.decorators.http import require_GET, require_http_methods

# Importa formulario de captura de auditorías.
from seo_auditor.web.apps.auditorias.forms import NuevaAuditoriaForm

# Importa modelo de persistencia de ejecuciones web.
from seo_auditor.web.apps.auditorias.models import EjecucionAuditoria

# Importa servicios adaptadores de ejecución web.
from seo_auditor.web.apps.auditorias.services_web import construir_request_desde_formulario, ejecutar_auditoria_web


# Obtiene listado reciente de archivos generados en carpeta de salidas.
def _listar_archivos_recientes(limite: int = 10) -> list[dict[str, str]]:
    """Recorre la carpeta `salidas` para exponer artefactos recientes en dashboard."""

    # Define raíz de salidas usada por el núcleo actual.
    raiz_salidas = Path("./salidas")

    # Devuelve lista vacía cuando la carpeta no existe aún.
    if not raiz_salidas.exists():
        return []

    # Recolecta archivos candidatos de forma no recursiva costosa.
    archivos = [ruta for ruta in raiz_salidas.rglob("*") if ruta.is_file()]

    # Ordena por fecha de modificación descendente para mostrar recientes.
    archivos_ordenados = sorted(archivos, key=lambda ruta: ruta.stat().st_mtime, reverse=True)

    # Construye salida simplificada con metadatos legibles.
    return [
        {
            "nombre": archivo.name,
            "ruta": str(archivo),
            "fecha": datetime.utcfromtimestamp(archivo.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }
        for archivo in archivos_ordenados[:limite]
    ]


# Renderiza dashboard interno con accesos rápidos y estado general.
@require_GET
def dashboard(request: HttpRequest) -> HttpResponse:
    """Muestra inicio interno con accesos a auditorías y documentos recientes."""

    # Recupera últimas ejecuciones registradas para seguimiento rápido.
    ejecuciones = EjecucionAuditoria.objects.all()[:10]

    # Recupera últimos archivos detectados en carpeta de salidas.
    archivos_recientes = _listar_archivos_recientes()

    # Renderiza plantilla principal de dashboard interno.
    return render(
        request,
        "auditorias/dashboard.html",
        {
            "ejecuciones": ejecuciones,
            "archivos_recientes": archivos_recientes,
        },
    )


# Renderiza y procesa formulario para lanzar nueva auditoría.
@require_http_methods(["GET", "POST"])
def nueva_auditoria(request: HttpRequest) -> HttpResponse:
    """Gestiona la creación y ejecución de auditorías desde navegador."""

    # Instancia formulario vacío en método GET.
    if request.method == "GET":
        # Crea formulario sin datos para primera carga.
        form = NuevaAuditoriaForm()

        # Renderiza la vista de formulario inicial.
        return render(request, "auditorias/nueva_auditoria.html", {"form": form})

    # Instancia formulario con datos enviados por POST.
    form = NuevaAuditoriaForm(request.POST)

    # Verifica validez del formulario antes de ejecutar lógica.
    if not form.is_valid():
        # Re-renderiza formulario con errores de validación.
        return render(request, "auditorias/nueva_auditoria.html", {"form": form}, status=400)

    # Crea registro persistente en estado en proceso para trazabilidad.
    ejecucion = EjecucionAuditoria.objects.create(
        cliente=form.cleaned_data.get("cliente", ""),
        sitemap=form.cleaned_data["sitemap"],
        gestor=form.cleaned_data["gestor"],
        fecha_inicio=form.cleaned_data["fecha_inicio"],
        fecha_fin=form.cleaned_data["fecha_fin"],
        estado=EjecucionAuditoria.ESTADO_EN_PROCESO,
    )

    # Intenta construir request interno y ejecutar auditoría real.
    try:
        # Construye request de dominio reutilizando contratos existentes.
        request_auditoria = construir_request_desde_formulario(form.cleaned_data)

        # Ejecuta auditoría y obtiene resumen serializable para plantillas.
        resultado = ejecutar_auditoria_web(request_auditoria)

        # Obtiene lista de registros de entregables generados/omitidos.
        registros_entregables = resultado["entregables"].get("registros", [])

        # Busca primera ruta de salida disponible para mostrar acceso rápido.
        ruta_salida = ""

        # Recorre registros para encontrar una ruta física existente.
        for registro in registros_entregables:
            # Recupera ruta final reportada por el servicio.
            ruta_registro = str(registro.get("ruta_final") or "").strip()

            # Conserva la primera ruta no vacía como ruta base visible.
            if ruta_registro:
                # Guarda ruta candidata para ficha de ejecución.
                ruta_salida = ruta_registro

                # Finaliza recorrido al encontrar primer artefacto válido.
                break

        # Actualiza registro como finalizado con resultados serializados.
        ejecucion.estado = EjecucionAuditoria.ESTADO_FINALIZADA

        # Guarda ruta de salida para trazabilidad y descargas.
        ejecucion.ruta_salida = ruta_salida

        # Guarda fuentes activas para resumen operativo.
        ejecucion.fuentes_activas = resultado["resumen"].get("fuentes_activas", [])

        # Guarda fuentes fallidas para alertas no fatales.
        ejecucion.fuentes_fallidas = resultado["resumen"].get("fuentes_fallidas", [])

        # Guarda resumen detallado serializado para la vista de resultado.
        ejecucion.resumen_resultado = resultado

        # Guarda registros de entregables para sección de descargas.
        ejecucion.entregables = registros_entregables

        # Persiste cambios finales de ejecución satisfactoria.
        ejecucion.save(update_fields=["estado", "ruta_salida", "fuentes_activas", "fuentes_fallidas", "resumen_resultado", "entregables", "fecha_actualizacion"])
    except Exception as exc:
        # Marca ejecución como error controlado ante cualquier excepción.
        ejecucion.estado = EjecucionAuditoria.ESTADO_ERROR

        # Guarda detalle de error para diagnóstico en UI.
        ejecucion.mensaje_error = str(exc)

        # Persiste estado de error para trazabilidad.
        ejecucion.save(update_fields=["estado", "mensaje_error", "fecha_actualizacion"])

    # Redirige a vista de detalle para estado y resultados.
    return redirect(reverse("auditorias:detalle", kwargs={"ejecucion_id": ejecucion.pk}))


# Muestra estado y resumen de una ejecución específica.
@require_GET
def detalle_auditoria(request: HttpRequest, ejecucion_id: int) -> HttpResponse:
    """Renderiza estado, resumen y descargas de una ejecución web."""

    # Recupera ejecución por ID o devuelve 404 si no existe.
    ejecucion = get_object_or_404(EjecucionAuditoria, pk=ejecucion_id)

    # Renderiza plantilla de detalle con datos persistidos.
    return render(request, "auditorias/detalle_auditoria.html", {"ejecucion": ejecucion})


# Descarga un archivo generado en una ejecución concreta.
@require_GET
def descargar_entregable(request: HttpRequest, ejecucion_id: int, indice: int) -> FileResponse:
    """Sirve un entregable generado cuando existe en disco local."""

    # Recupera ejecución de referencia para validar entregable.
    ejecucion = get_object_or_404(EjecucionAuditoria, pk=ejecucion_id)

    # Recupera colección de entregables serializados desde persistencia.
    entregables = list(ejecucion.entregables or [])

    # Valida que el índice solicitado exista en la colección.
    if indice < 0 or indice >= len(entregables):
        # Lanza 404 cuando el índice no es válido.
        raise Http404("El entregable solicitado no existe.")

    # Recupera registro del entregable solicitado.
    registro = entregables[indice]

    # Extrae ruta física del artefacto generado.
    ruta = Path(str(registro.get("ruta_final") or "").strip())

    # Valida existencia del archivo antes de descargarlo.
    if not ruta.exists() or not ruta.is_file():
        # Lanza 404 cuando el archivo ya no está disponible en disco.
        raise Http404("El archivo solicitado no está disponible.")

    # Devuelve archivo en modo binario como descarga adjunta.
    return FileResponse(ruta.open("rb"), as_attachment=True, filename=ruta.name)
