# Flujo de datos de reporting documental

## Resumen
1. `cli.py` consolida `ResultadoAuditoria`.
2. `documentacion/modelo/` expone el modelo semántico común (`construir_modelo_semantico_informe`).
3. `documentacion/builders/` compone jerarquías y secciones intermedias.
4. `documentacion/shared/` normaliza/sanitiza textos y estilos transversales.
5. `documentacion/exportadores/` materializa cada formato.
6. `reporters/` mantiene módulos puente para compatibilidad externa.

## Contrato clave
- DOCX/PDF/HTML deben renderizar desde la capa semántica común, no desde markdown directo.
- El markdown IA (`*_ia.md`) es artefacto auxiliar interno de revisión.
