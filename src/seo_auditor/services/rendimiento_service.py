"""Servicios de rendimiento (PageSpeed y experiencia)."""

from seo_auditor.integrations.pagespeed.service import analizar_pagespeed_url


def ejecutar_pagespeed_batch(urls: list[str], **kwargs):
    return [analizar_pagespeed_url(url=url, **kwargs) for url in urls]
