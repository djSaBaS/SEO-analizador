"""Servicios de auditoría principal."""

from seo_auditor.core.assembler import auditar_urls


def ejecutar_auditoria(urls: list[str], timeout: int, max_workers: int):
    return auditar_urls(urls=urls, timeout=timeout, max_workers=max_workers)
