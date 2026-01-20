import os
import shutil
import subprocess
import json
from flask import render_template
from main import app, get_vpn_configs, fetch_download_links, FALLBACK_LINKS

# НАСТРОЙКИ
REPO_USER = "AvenCores"
REPO_NAME = "goida-vpn-site"
TARGET_REPO = f"https://github.com/{REPO_USER}/{REPO_NAME}.git"
DIST_DIR = "dist"

# ВАЖНО: Пушим в отдельную ветку, чтобы не стереть исходный код в main
BRANCH = "gh-pages" 

def build_site():
    print(f"🚀 Начинаем сборку сайта в папку ./{DIST_DIR}...")

    # 1. Очистка и создание папки dist
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)
    os.makedirs(os.path.join(DIST_DIR, 'api'))

    # 2. Копирование статики
    if os.path.exists('static'):
        shutil.copytree('static', os.path.join(DIST_DIR, 'static'))
        print("✅ Папка static скопирована")

    # 3. Генерация HTML через Flask
    # ИСПОЛЬЗУЕМ test_request_context (Фикс ошибки URL)
    with app.test_request_context():
        print("⏳ Получение конфигов и рендеринг шаблона...")
        configs = get_vpn_configs()
        rendered_html = render_template('index.html', configs=configs)
        
        with open(os.path.join(DIST_DIR, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        print("✅ Файл index.html создан")

    # 4. Генерация API
    print("⏳ Получение ссылок на скачивание...")
    links = fetch_download_links()
    if not links:
        links = FALLBACK_LINKS
    
    api_path = os.path.join(DIST_DIR, 'api')
    with open(os.path.join(api_path, 'download-links'), 'w', encoding='utf-8') as f:
        json.dump(links, f)
    with open(os.path.join(api_path, 'download-links.json'), 'w', encoding='utf-8') as f:
        json.dump(links, f)
    print("✅ API файлы созданы")

    # 5. Создаем .nojekyll
    with open(os.path.join(DIST_DIR, '.nojekyll'), 'w') as f:
        pass

def deploy_to_github():
    token = os.getenv('MY_TOKEN')
    if not token:
        print("❌ ОШИБКА: Нет токена MY_TOKEN")
        return

    print(f"\n🚀 Публикация в ветку {BRANCH}...")
    
    auth_url = f"https://{token}@github.com/{REPO_USER}/{REPO_NAME}.git"

    # Создаем новый репозиторий внутри папки dist
    # Это безопасно, так как мы пушим ТОЛЬКО в ветку gh-pages
    commands = [
        ['git', 'init'],
        ['git', 'config', 'user.name', 'Auto Builder'],
        ['git', 'config', 'user.email', 'actions@github.com'],
        ['git', 'add', '.'],
        ['git', 'commit', '-m', 'Deploy site update'],
        ['git', 'branch', '-M', BRANCH], # Переименовываем локальную ветку в gh-pages
        ['git', 'remote', 'add', 'origin', auth_url],
        ['git', 'push', '-f', 'origin', BRANCH] # Перезаписываем только ветку gh-pages
    ]

    cwd = os.path.abspath(DIST_DIR)

    try:
        for cmd in commands:
            subprocess.run(cmd, cwd=cwd, check=True, capture_output=True) 
        print(f"\n🎉 УСПЕШНО! Сайт обновлен в ветке {BRANCH}")
        print(f"Ветка main осталась нетронутой.")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка Git: {e}")

if __name__ == '__main__':
    build_site()
    deploy_to_github()