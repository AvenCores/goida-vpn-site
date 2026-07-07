import os
from flask import request
from urllib.parse import urljoin
from datetime import datetime

def normalize_site_url(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    if not value.endswith('/'):
        value += '/'
    return value

def get_site_url() -> str | None:
    site_url = normalize_site_url(os.environ.get('SITE_URL'))
    if site_url:
        return site_url
    try:
        return normalize_site_url(request.url_root)
    except RuntimeError:
        return None

def get_analytics_ids() -> dict[str, str | None]:
    return {
        'ga_id': os.environ.get('GA_ID'),
        'ym_id': os.environ.get('YM_ID'),
        'yandex_autoplacement_id': os.environ.get('YANDEX_AUTOPLACEMENT_ID')
    }

def generate_robots_txt(site_url: str | None) -> str:
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /api/",
        "Disallow: /download_links_cache.json",
        "Disallow: /github_stats_cache.json",
        "",
        "# Yandex-specific optimization",
        "User-agent: Yandex",
        "Allow: /",
        "Disallow: /api/",
        "Clean-param: utm_source&utm_medium&utm_campaign",
    ]
    if site_url:
        lines.append("")
        lines.append(f"Sitemap: {urljoin(site_url, 'sitemap.xml')}")
        lines.append(f"Host: {site_url.split('://')[-1].rstrip('/')}")
    return "\n".join(lines) + "\n"

def generate_sitemap_xml(site_url: str | None, lastmod: str | None = None) -> str:
    if not lastmod:
        lastmod = datetime.utcnow().date().isoformat()
    
    # Ensure site_url is absolute
    base = site_url or "/"
    loc = urljoin(base, "")
    if not loc.endswith('/'):
        loc += '/'
        
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
        '        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9\n'
        '        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n'
        "  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        "    <changefreq>hourly</changefreq>\n"
        "    <priority>1.0</priority>\n"
        "  </url>\n"
        "</urlset>\n"
    )
