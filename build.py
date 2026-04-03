import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

from flask import render_template

from main import (
    DEFAULT_META_DESCRIPTION,
    DEFAULT_META_TITLE,
    FALLBACK_LINKS,
    VC_RUNTIME_FALLBACK,
    app,
    download_badges,
    fetch_download_links,
    fetch_github_stats_data,
    fetch_vc_runtime_link,
    generate_robots_txt,
    generate_sitemap_xml,
    get_analytics_ids,
    get_vpn_configs,
    normalize_site_url,
)

# ANSI цвета
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    DIM = "\033[2m"


def log_info(message, emoji="ℹ️"):
    """Вывод информационного сообщения"""
    print(f"{Colors.CYAN}{emoji}  {Colors.BOLD}{message}{Colors.RESET}")


def log_success(message, emoji="✅"):
    """Вывод сообщения об успехе"""
    print(f"{Colors.GREEN}{emoji}  {message}{Colors.RESET}")


def log_warning(message, emoji="⚠️"):
    """Вывод предупреждения"""
    print(f"{Colors.YELLOW}{emoji}  {Colors.BOLD}{message}{Colors.RESET}")


def log_error(message, emoji="❌"):
    """Вывод ошибки"""
    print(f"{Colors.RED}{emoji}  {Colors.BOLD}{message}{Colors.RESET}")


def log_step(message, emoji="🔧"):
    """Вывод шага выполнения"""
    print(f"\n{Colors.MAGENTA}{emoji}  {Colors.BOLD}{message}{Colors.RESET}")


def log_detail(message, emoji="  ↳"):
    """Вывод детализации"""
    print(f"{Colors.DIM}{emoji}  {message}{Colors.RESET}")


def log_divider():
    """Вывод разделителя"""
    print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")

REPO_USER = "AvenCores"
REPO_NAME = "goida-vpn-site"
TARGET_REPO = f"https://github.com/{REPO_USER}/{REPO_NAME}.git"
DIST_DIR = "dist"
BRANCH = "gh-pages"


def build_site():
    log_divider()
    log_step("🚀 Сборка сайта", emoji="🚀")
    log_divider()
    log_info(f"Целевая директория: ./{DIST_DIR}")
    
    download_badges()
    log_success("Бейджи загружены")

    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
        log_detail("Старая папка dist удалена")
    
    os.makedirs(DIST_DIR)
    os.makedirs(os.path.join(DIST_DIR, "api"))
    log_success("Структура директорий создана")

    if os.path.exists("static"):
        shutil.copytree("static", os.path.join(DIST_DIR, "static"))
        log_success("📁 static скопирован")

    translations_src = "static/i18n/translations.json"
    if os.path.exists(translations_src):
        i18n_dir = os.path.join(DIST_DIR, "static", "i18n")
        os.makedirs(i18n_dir, exist_ok=True)
        shutil.copy2(translations_src, os.path.join(i18n_dir, "translations.json"))
        log_success("🌐 translations.json скопирован")

    site_url = normalize_site_url(
        os.getenv("SITE_URL") or f"https://{REPO_USER.lower()}.github.io/{REPO_NAME}/"
    )
    log_detail(f"URL сайта: {site_url}")

    with app.test_request_context():
        log_step("📄 Рендеринг index.html")
        configs = get_vpn_configs()
        analytics_ids = get_analytics_ids()
        if not analytics_ids.get("yandex_autoplacement_id"):
            log_warning("YANDEX_AUTOPLACEMENT_ID не установлен")

        rendered_html = render_template(
            "index.html",
            configs=configs,
            analytics_ids=analytics_ids,
            site_url=site_url,
            canonical_url=site_url,
            download_links=FALLBACK_LINKS,
            vc_runtime_link=VC_RUNTIME_FALLBACK,
            meta_title=os.environ.get("META_TITLE", DEFAULT_META_TITLE),
            meta_description=os.environ.get("META_DESCRIPTION", DEFAULT_META_DESCRIPTION),
            og_image=os.environ.get("OG_IMAGE_URL"),
        )

        with open(os.path.join(DIST_DIR, "index.html"), "w", encoding="utf-8") as f:
            f.write(rendered_html)
        log_success("📄 index.html создан")

    api_path = os.path.join(DIST_DIR, "api")

    log_step("🔗 Генерация API файлов")
    fetched_links = fetch_download_links()
    download_links = FALLBACK_LINKS.copy()
    if fetched_links:
        download_links.update(fetched_links)
        log_success("Ссылки на скачивание получены с GitHub")
    else:
        log_warning("Используются резервные ссылки на скачивание")

    with open(os.path.join(api_path, "download-links.json"), "w", encoding="utf-8") as f:
        json.dump(download_links, f)
    log_success("📦 download-links.json создан")

    log_detail("Получение ссылки на Visual C++ Runtimes...")
    vc_runtime_link = fetch_vc_runtime_link() or VC_RUNTIME_FALLBACK
    with open(os.path.join(api_path, "vc-runtime-link.json"), "w", encoding="utf-8") as f:
        json.dump({"link": vc_runtime_link}, f)
    log_success("⚙️ vc-runtime-link.json создан")

    log_detail("Получение статистики репозитория...")
    fetch_and_save_github_stats(api_path)

    open(os.path.join(DIST_DIR, ".nojekyll"), "w").close()
    log_success(".nojekyll создан")

    with open(os.path.join(DIST_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(generate_robots_txt(site_url))
    log_success("🤖 robots.txt создан")

    lastmod = datetime.utcnow().date().isoformat()
    with open(os.path.join(DIST_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(generate_sitemap_xml(site_url, lastmod=lastmod))
    log_success("🗺️ sitemap.xml создан")
    
    log_divider()
    log_success("✨ Сборка завершена успешно!", emoji="✨")
    log_divider()


def fetch_and_save_github_stats(api_path):
    stats = fetch_github_stats_data(os.getenv("MY_TOKEN"))
    with open(os.path.join(api_path, "github-stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f)
    log_success("📊 github-stats.json создан")


def deploy_to_github():
    token = os.getenv("MY_TOKEN")
    if not token:
        log_error("Отсутствует токен MY_TOKEN в переменных окружения")
        return

    log_divider()
    log_step(f"🚀 Публикация в ветку {BRANCH}", emoji="🚀")
    log_divider()
    
    auth_url = f"https://{token}@github.com/{REPO_USER}/{REPO_NAME}.git"
    commands = [
        ["git", "init"],
        ["git", "config", "user.name", "Auto Builder"],
        ["git", "config", "user.email", "actions@github.com"],
        ["git", "add", "."],
        ["git", "commit", "-m", "Deploy site update"],
        ["git", "branch", "-M", BRANCH],
        ["git", "remote", "add", "origin", auth_url],
        ["git", "push", "-f", "origin", BRANCH],
    ]

    cwd = os.path.abspath(DIST_DIR)
    try:
        for i, cmd in enumerate(commands, 1):
            log_detail(f"Выполнение шага {i}/{len(commands)}: {' '.join(cmd[:2])}...")
            subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)
        
        log_divider()
        log_success(f"🎉 Сайт успешно обновлен в ветке {BRANCH}!", emoji="🎉")
        log_divider()
    except subprocess.CalledProcessError as e:
        log_error(f"Ошибка при выполнении Git команд: {e}")
        if e.stderr:
            log_detail(f"Детали: {e.stderr.decode('utf-8')}")


if __name__ == "__main__":
    build_site()
    deploy_to_github()
