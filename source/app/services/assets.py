"""Локальные фронтенд-ассеты для dev-сервера и сборки.

Все эти файлы лежат в .gitignore (скачиваются, а не коммитятся):
  - Alpine.js / Tailwind CDN-fallback / FontAwesome / флаги  -> download_external_assets()
  - shields.io бэджи                                        -> download_badges() (services.github)

В --debug режиме внешние запросы к API пропуcкаются (заглушки), но сами
статические файлы должны существовать локально, иначе браузер получает
десятки 404 (alpine, all.min.css, webfonts, flags, badges).
Поэтому dev-сервер вызывает ensure_local_assets(): недостающие файлы
докачиваются один раз (идемпотентно), а бэджи в debug заменяются
локальными SVG-плейсхолдерами без похода в сеть.
"""

import concurrent.futures
import logging
import os

import app.config as config_module
from app.config import BADGES

log = logging.getLogger(__name__)

EXTERNAL_ASSETS: tuple[tuple[str, str], ...] = (
    # Alpine JS
    ("https://cdn.jsdelivr.net/npm/@alpinejs/collapse@3.x.x/dist/cdn.min.js", "app/static/js/alpine-collapse.min.js"),
    ("https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js", "app/static/js/alpine.min.js"),
    # Tailwind Fallback
    ("https://cdn.tailwindcss.com", "app/static/js/tailwind.min.js"),
    # FontAwesome CSS
    ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css", "app/static/css/all.min.css"),
    # FontAwesome Fonts
    ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/webfonts/fa-solid-900.woff2", "app/static/webfonts/fa-solid-900.woff2"),
    ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/webfonts/fa-regular-400.woff2", "app/static/webfonts/fa-regular-400.woff2"),
    ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/webfonts/fa-brands-400.woff2", "app/static/webfonts/fa-brands-400.woff2"),
    # Flags
    ("https://flagcdn.com/w20/ru.png", "app/static/images/flags/ru.png"),
    ("https://flagcdn.com/w40/ru.png", "app/static/images/flags/ru@2x.png"),
    ("https://flagcdn.com/w20/gb.png", "app/static/images/flags/gb.png"),
    ("https://flagcdn.com/w40/gb.png", "app/static/images/flags/gb@2x.png"),
    ("https://flagcdn.com/w20/de.png", "app/static/images/flags/de.png"),
    ("https://flagcdn.com/w40/de.png", "app/static/images/flags/de@2x.png"),
    ("https://flagcdn.com/w20/ua.png", "app/static/images/flags/ua.png"),
    ("https://flagcdn.com/w40/ua.png", "app/static/images/flags/ua@2x.png"),
    ("https://flagcdn.com/w20/by.png", "app/static/images/flags/by.png"),
    ("https://flagcdn.com/w40/by.png", "app/static/images/flags/by@2x.png"),
    ("https://flagcdn.com/w20/kz.png", "app/static/images/flags/kz.png"),
    ("https://flagcdn.com/w40/kz.png", "app/static/images/flags/kz@2x.png"),
    ("https://flagcdn.com/w20/fr.png", "app/static/images/flags/fr.png"),
    ("https://flagcdn.com/w40/fr.png", "app/static/images/flags/fr@2x.png"),
    ("https://flagcdn.com/w20/pl.png", "app/static/images/flags/pl.png"),
    ("https://flagcdn.com/w40/pl.png", "app/static/images/flags/pl@2x.png"),
)


def _resolve(path: str) -> str:
    """Абсолютный путь от корня source/ независимо от cwd."""
    return os.path.join(config_module.BASE_DIR, path.replace("/", os.sep))


def _download_single_asset(args: tuple[str, str]) -> None:
    """Download a single external asset if it does not already exist locally."""
    url, rel_path = args
    path = _resolve(rel_path)
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    if os.path.exists(path):
        return

    import requests
    log.info("Downloading %s -> %s...", url, rel_path)
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            log.info("Successfully downloaded %s", rel_path)
        else:
            log.warning("Failed to download %s: HTTP %s", url, r.status_code)
    except Exception as e:
        log.warning("Failed to download %s: %s", url, e)


def download_external_assets() -> None:
    """Download all required external frontend assets in parallel (skip existing)."""
    log.info("Checking and downloading external assets...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(_download_single_asset, EXTERNAL_ASSETS))


def _badge_placeholder_svg(filename: str) -> str:
    label = filename.replace(".svg", "")
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="28" role="img">'
        '<rect width="120" height="28" rx="6" fill="#555"/>'
        f'<text x="60" y="18" font-family="Verdana,sans-serif" font-size="11" '
        f'fill="#fff" text-anchor="middle">{label}</text></svg>'
    )


def ensure_badge_placeholders() -> None:
    """Создать SVG-плейсхолдеры отсутствующих бэджей (без сети, для --debug)."""
    badges_dir = os.path.join(config_module.BASE_DIR, "app", "static", "images", "badges")
    os.makedirs(badges_dir, exist_ok=True)
    for filename in BADGES:
        path = os.path.join(badges_dir, filename)
        if os.path.exists(path):
            continue
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(_badge_placeholder_svg(filename))
            log.info("Created badge placeholder %s", filename)
        except OSError as e:
            log.warning("Failed to create badge placeholder %s: %s", filename, e)


def ensure_local_assets() -> None:
    """Гарантировать наличие локальных ассетов для dev-сервера.

    Внешние ассеты докачиваются (только отсутствующие), бэджи в debug
    заменяются плейсхолдерами, в prod — скачиваются как раньше.
    """
    download_external_assets()
    if config_module.DEBUG_MODE:
        ensure_badge_placeholders()
    else:
        from app.services.github import download_badges
        download_badges()
