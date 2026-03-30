# Ejemplos de comandos CLI

## Modo completo (prompt principal)

```bash
python -m src.main --sitemap https://ejemplo.com/sitemap.xml --modo completo
```

## Modos con prompts específicos

```bash
python -m src.main --sitemap https://ejemplo.com/sitemap.xml --modo resumen
python -m src.main --sitemap https://ejemplo.com/sitemap.xml --modo quickwins
python -m src.main --sitemap https://ejemplo.com/sitemap.xml --modo gsc
python -m src.main --sitemap https://ejemplo.com/sitemap.xml --modo roadmap
```

## Nota de compatibilidad

- La convención canónica de plantillas es `prompts/`.
- Se mantiene fallback temporal de lectura desde `Prompt/consulta_ia_prompt.txt` para ejecuciones legacy.
