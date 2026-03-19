# Define el punto de entrada del ejecutable en Python.
from seo_auditor.cli import main

# Ejecuta el programa solo cuando este archivo se invoca directamente.
if __name__ == "__main__":
    # Lanza la función principal del CLI.
    raise SystemExit(main())
