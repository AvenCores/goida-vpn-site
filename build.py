import os
import shutil
import subprocess
import json
import requests
from datetime import datetime
from flask import render_template
from main import (
    app,
    get_vpn_configs,
    fetch_download_links,
    FALLBACK_LINKS,
    download_badges,
    normalize_site_url,
    generate_robots_txt,
    generate_sitemap_xml,
    DEFAULT_META_TITLE,
    DEFAULT_META_DESCRIPTION
)

# НАСТРОЙКИ
REPO_USER = "AvenCores"
REPO_NAME = "goida-vpn-site"
STATS_REPO_NAME = "goida-vpn-configs" # Репозиторий, чью статистику мы хотим видеть
TARGET_REPO = f"https://github.com/{REPO_USER}/{REPO_NAME}.git"
DIST_DIR = "dist"
BRANCH = "gh-pages" 

def build_site():
    print(f"🚀 Начинаем сборку сайта в папку ./{DIST_DIR}...")

    # Скачиваем актуальные бэджи
    download_badges()

    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)
    os.makedirs(os.path.join(DIST_DIR, 'api'))

    if os.path.exists('static'):
        shutil.copytree('static', os.path.join(DIST_DIR, 'static'))
        print("✅ Папка static скопирована")

    site_url = normalize_site_url(
        os.getenv('SITE_URL') or f"https://{REPO_USER.lower()}.github.io/{REPO_NAME}/"
    )

    with app.test_request_context():
        print("⏳ Получение конфигов и рендеринг шаблона...")
        configs = get_vpn_configs()
        analytics_ids = {
            'ga_id': os.environ.get('GA_ID'),
            'ym_id': os.environ.get('YM_ID')
        }
        meta_title = os.environ.get('META_TITLE', DEFAULT_META_TITLE)
        meta_description = os.environ.get('META_DESCRIPTION', DEFAULT_META_DESCRIPTION)
        og_image = os.environ.get('OG_IMAGE_URL')
        rendered_html = render_template(
            'index.html',
            configs=configs,
            analytics_ids=analytics_ids,
            site_url=site_url,
            canonical_url=site_url,
            meta_title=meta_title,
            meta_description=meta_description,
            og_image=og_image
        )
        
        with open(os.path.join(DIST_DIR, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        print("✅ Файл index.html создан")

    print("⏳ Получение ссылок на скачивание...")
    links = fetch_download_links()
    if not links:
        print("⚠️ Не удалось получить ссылки с GitHub, используются резервные")
        links = FALLBACK_LINKS
    
    api_path = os.path.join(DIST_DIR, 'api')
    
    with open(os.path.join(api_path, 'download-links.json'), 'w', encoding='utf-8') as f:
        json.dump(links, f)
    print("✅ API файл ссылок создан")

    print("⏳ Получение статистики репозитория...")
    fetch_and_save_github_stats(api_path)

    with open(os.path.join(DIST_DIR, '.nojekyll'), 'w') as f:
        pass

    with open(os.path.join(DIST_DIR, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write(generate_robots_txt(site_url))

    lastmod = datetime.utcnow().date().isoformat()
    with open(os.path.join(DIST_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(generate_sitemap_xml(site_url, lastmod=lastmod))

def fetch_and_save_github_stats(api_path):
    """Получает статистику трафика и общую инфо с GitHub"""
    base_url = f'https://api.github.com/repos/{REPO_USER}/{STATS_REPO_NAME}'
    token = os.getenv('MY_TOKEN')
    
    stats = {
        "pushed_at": None,
        "stargazers_count": 0,
        "clones": {"count": 0, "uniques": 0},
        "views": {"count": 0, "uniques": 0},
        "referrers": [],
        "popular_content": [],
        "error": None
    }

    if not token:
        print("❌ ОШИБКА: Для доступа к статистике трафика необходим MY_TOKEN.")
        stats["error"] = "Token not configured"
        with open(os.path.join(api_path, 'github-stats.json'), 'w', encoding='utf-8') as f:
            json.dump(stats, f)
        return

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    try:
        # 1. Получаем общую информацию (Дату пуша, Звезды)
        print(f"ℹ️ Запрос общей информации о {STATS_REPO_NAME}...")
        repo_response = requests.get(base_url, headers=headers, timeout=10)
        repo_response.raise_for_status()
        repo_data = repo_response.json()
        
        stats["pushed_at"] = repo_data.get("pushed_at")
        stats["stargazers_count"] = repo_data.get("stargazers_count", 0)

        # 2. Получаем данные о клонах (Нужны права push/admin)
        print("ℹ️ Запрос статистики клонирования...")
        clones_response = requests.get(f'{base_url}/traffic/clones', headers=headers, timeout=10)
        if clones_response.ok:
            clones_data = clones_response.json()
            stats["clones"]["count"] = clones_data.get('count', 0)
            stats["clones"]["uniques"] = clones_data.get('uniques', 0)
        else:
            print(f"⚠️ Warning: Clones API returned {clones_response.status_code}")

        # 3. Получаем данные о просмотрах
        print("ℹ️ Запрос статистики просмотров...")
        views_response = requests.get(f'{base_url}/traffic/views', headers=headers, timeout=10)
        if views_response.ok:
            views_data = views_response.json()
            stats["views"]["count"] = views_data.get('count', 0)
            stats["views"]["uniques"] = views_data.get('uniques', 0)
        else:
            print(f"⚠️ Warning: Views API returned {views_response.status_code}")

        # 4. Получаем cайтов-источников переходов
        print("ℹ️ Запрос cайтов-источников переходов...")
        referrers_response = requests.get(f'{base_url}/traffic/popular/referrers', headers=headers, timeout=10)
        if referrers_response.ok:
            stats["referrers"] = referrers_response.json()
        else:
            print(f"⚠️ Warning: Referrers API returned {referrers_response.status_code}")
            stats["referrers"] = []

        # 5. Получаем популярный контент
        print("ℹ️ Запрос популярного контента...")
        paths_response = requests.get(f'{base_url}/traffic/popular/paths', headers=headers, timeout=10)
        if paths_response.ok:
            stats["popular_content"] = paths_response.json()
        else:
            print(f"⚠️ Warning: Paths API returned {paths_response.status_code}")
            stats["popular_content"] = []

    except requests.exceptions.RequestException as e:
        error_message = str(e)
        print(f"❌ ОШИБКА при запросе к GitHub: {error_message}")
        stats["error"] = error_message

    # Сохраняем результат
    with open(os.path.join(api_path, 'github-stats.json'), 'w', encoding='utf-8') as f:
        json.dump(stats, f)
    print("✅ Файл статистики github-stats.json создан")

def deploy_to_github():
    token = os.getenv('MY_TOKEN')
    if not token:
        print("❌ ОШИБКА: Нет токена MY_TOKEN")
        return

    print(f"🚀 Публикация в ветку {BRANCH}...")
    auth_url = f"https://{token}@github.com/{REPO_USER}/{REPO_NAME}.git"

    commands = [
        ['git', 'init'],
        ['git', 'config', 'user.name', 'Auto Builder'],
        ['git', 'config', 'user.email', 'actions@github.com'],
        ['git', 'add', '.'],
        ['git', 'commit', '-m', 'Deploy site update'],
        ['git', 'branch', '-M', BRANCH],
        ['git', 'remote', 'add', 'origin', auth_url],
        ['git', 'push', '-f', 'origin', BRANCH]
    ]

    cwd = os.path.abspath(DIST_DIR)
    try:
        for cmd in commands:
            subprocess.run(cmd, cwd=cwd, check=True, capture_output=True) 
        print(f"🎉 Успешно! Сайт обновлен в ветке {BRANCH}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка Git: {e}")
        if e.stderr:
            print(f"Детали: {e.stderr.decode('utf-8')}")

if __name__ == '__main__':
    build_site()
    deploy_to_github()
