# Arquitectura del proyecto

## Resumen
El sistema sigue una arquitectura modular con separación por capas:

1. **Entrada y orquestación**: `cli.py`.
2. **Configuración**: `config.py`.
3. **Adquisición/análisis técnico**: `fetcher.py`, `analyzer.py`, `indexacion.py`.
4. **Fuentes externas opcionales**: `pagespeed.py`, `gsc.py`, `ga4.py`.
5. **Narrativa IA opcional**: `gemini_client.py`.
6. **Exportación de entregables**: `reporters/` (fachada puente) + `documentacion/` (responsabilidades internas).
7. **Soporte transversal**: `models.py`, `utils.py`, `cache.py`.

## Flujos operativos soportados

### 1) Auditoría SEO completa
- Entrada por `--sitemap`.
- Auditoría técnica por URL.
- Capa opcional de rendimiento (PageSpeed).
- Capa opcional de datos autenticados (GSC/GA4).
- Capa opcional narrativa IA.
- Exportación multi-formato.

### 2) Modo dedicado GA4 premium
- Activado con `--modo informe-ga4`.
- No requiere ejecutar auditoría SEO completa.
- Genera entregables específicos de GA4 en HTML, PDF y Excel.

## Principios de diseño
- **Degradación elegante**: fallo de una integración no bloquea el flujo global.
- **Separación técnico/ejecutivo**: el detalle técnico convive con narrativa accionable.
- **Evolución mantenible**: módulos externos desacoplados de la orquestación.
- **Trazabilidad**: mensajes de consola y estados de fuentes para diagnóstico.

## Extensibilidad
- Nuevas fuentes pueden añadirse como módulos desacoplados.
- La capa de reporting reutiliza modelos estructurados, reduciendo acoplamiento con el origen de datos.
- La capa de caché permite escalar a backends externos en futuras iteraciones.

## Contrato documental de layout
- El archivo `*_ia.md` se conserva únicamente como artefacto auxiliar de revisión interna.
- El layout final de cliente (DOCX/PDF/HTML) no lee markdown IA de forma directa.
- Los exportadores finales consumen exclusivamente la capa semántica intermedia (`construir_modelo_semantico_informe`) para mantener coherencia transversal.
