import json
import os
import shutil
import subprocess
from datetime import datetime

from flask import render_template

from main import (
    DEFAULT_META_DESCRIPTION,
    DEFAULT_META_KEYWORDS,
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

REPO_USER = "AvenCores"
REPO_NAME = "goida-vpn-site"
TARGET_REPO = f"https://github.com/{REPO_USER}/{REPO_NAME}.git"
DIST_DIR = "dist"
BRANCH = "gh-pages"


def build_site():
    print(f"Начинаем сборку сайта в ./{DIST_DIR}...")
    download_badges()

    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)
    os.makedirs(os.path.join(DIST_DIR, "api"))

    if os.path.exists("static"):
        shutil.copytree("static", os.path.join(DIST_DIR, "static"))
        print("Папка static скопирована")

    translations_src = "static/i18n/translations.json"
    if os.path.exists(translations_src):
        i18n_dir = os.path.join(DIST_DIR, "static", "i18n")
        os.makedirs(i18n_dir, exist_ok=True)
        shutil.copy2(translations_src, os.path.join(i18n_dir, "translations.json"))
        print("Файл переводов translations.json скопирован")

    site_url = normalize_site_url(
        os.getenv("SITE_URL") or f"https://{REPO_USER.lower()}.github.io/{REPO_NAME}/"
    )

    with app.test_request_context():
        print("Рендеринг index.html...")
        configs = get_vpn_configs()
        analytics_ids = get_analytics_ids()
        if not analytics_ids.get("yandex_autoplacement_id"):
            print("WARNING: YANDEX_AUTOPLACEMENT_ID is not set, skipping Yandex Autoplacement in dist/index.html")

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
            meta_keywords=os.environ.get("META_KEYWORDS", DEFAULT_META_KEYWORDS),
            og_image=os.environ.get("OG_IMAGE_URL"),
        )

        with open(os.path.join(DIST_DIR, "index.html"), "w", encoding="utf-8") as f:
            f.write(rendered_html)
        print("Файл index.html создан")

    api_path = os.path.join(DIST_DIR, "api")

    print("Получение ссылок на скачивание...")
    fetched_links = fetch_download_links()
    download_links = FALLBACK_LINKS.copy()
    if fetched_links:
        download_links.update(fetched_links)
    else:
        print("Не удалось получить ссылки с GitHub, используются резервные")

    with open(os.path.join(api_path, "download-links.json"), "w", encoding="utf-8") as f:
        json.dump(download_links, f)
    print("API файл ссылок создан")

    print("Получение ссылки на Visual C++ Runtimes...")
    vc_runtime_link = fetch_vc_runtime_link() or VC_RUNTIME_FALLBACK
    with open(os.path.join(api_path, "vc-runtime-link.json"), "w", encoding="utf-8") as f:
        json.dump({"link": vc_runtime_link}, f)
    print("API файл ссылки на VC Runtime создан")

    print("Получение статистики репозитория...")
    fetch_and_save_github_stats(api_path)

    open(os.path.join(DIST_DIR, ".nojekyll"), "w").close()

    with open(os.path.join(DIST_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(generate_robots_txt(site_url))

    lastmod = datetime.utcnow().date().isoformat()
    with open(os.path.join(DIST_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(generate_sitemap_xml(site_url, lastmod=lastmod))


def fetch_and_save_github_stats(api_path):
    stats = fetch_github_stats_data(os.getenv("MY_TOKEN"))
    with open(os.path.join(api_path, "github-stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f)
    print("Статистика GitHub сохранена")


def deploy_to_github():
    token = os.getenv("MY_TOKEN")
    if not token:
        print("ОШИБКА: Нет токена MY_TOKEN")
        return

    print(f"Публикация в ветку {BRANCH}...")
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
        for cmd in commands:
            subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)
        print(f"Сайт обновлен в ветке {BRANCH}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка Git: {e}")
        if e.stderr:
            print(f"Детали: {e.stderr.decode('utf-8')}")


if __name__ == "__main__":
    build_site()
    deploy_to_github()