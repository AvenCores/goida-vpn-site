from flask import Flask, render_template, send_from_directory, jsonify, request, Response
from services import get_vpn_configs, set_debug_mode as set_services_debug_mode
import requests
import json
from datetime import datetime, timedelta
from urllib.parse import urljoin
import os
import re
from bs4 import BeautifulSoup
import argparse
import logging
from waitress import serve

app = Flask(__name__)

# Глобальная переменная для режима отладки
DEBUG_MODE = False

def select_v2rayng_apk(assets):
    """Choose the standard universal APK for v2rayNG, not the F-Droid build."""
    standard_apk = next(
        (
            asset
            for asset in assets
            if 'universal.apk' in asset.get('name', '').lower()
            and 'f-droid' not in asset.get('name', '').lower()
            and 'fdroid' not in asset.get('name', '').lower()
        ),
        None,
    )
    if standard_apk:
        return standard_apk

    return next(
        (asset for asset in assets if 'universal.apk' in asset.get('name', '').lower()),
        None,
    )

def set_debug_mode(enabled: bool):
    """Установить режим отладки"""
    global DEBUG_MODE
    DEBUG_MODE = enabled
    # Передать режим в services модуль
    set_services_debug_mode(enabled)

# SEO defaults (can be overridden via env in production)
DEFAULT_META_TITLE = "Goida VPN Configs"
DEFAULT_META_DESCRIPTION = (
    "Автоматические VPN-конфиги для V2Ray, VLESS, Hysteria, Trojan, VMess, Reality и Shadowsocks. "
    "Обновление каждые 9 минут, удобные ссылки и QR-коды."
)
DEFAULT_META_KEYWORDS = "vpn, vless, v2ray, shadowsocks, hysteria, trojan, vmess, reality, vpn configs, free vpn, goida vpn, обход блокировок, автоматичні vpn конфіги, обхід блокувань, бесплатные vpn, xray, proxy, прокси, whitelist bypass, obход снд, sni bypass, vpn subscription, vpn конфиги, vpn configs free, автоматические vpn, vpn для россии, vpn для украины, vpn настройка, v2rayng, throne vpn, proxy list, бесплатные прокси, конфигурации vpn, vpn android, vpn windows, vpn ios, vpn macos, vpn linux, безопасный интернет, анонимность в сети, приватность, шифрование трафика, xray core, v2fly, проект xray, mtp roto, reality tls, hysteria 2, juicity, tuic, wireguard, openvpn, softether, neutronvpn, npv, vpn 2024, vpn 2025, рабочий vpn, стабильный vpn, быстрый vpn"

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

# Кэш для ссылок на скачивание
CACHE_FILE = 'download_links_cache.json'
CACHE_DURATION = timedelta(hours=24)

# Fallback ссылки на случай, если GitHub API недоступен
FALLBACK_LINKS = {
    'v2rayng-apk': 'https://github.com/2dust/v2rayNG/releases/download/2.0.13/v2rayNG_2.0.13_universal.apk',
    'throne-win10': 'https://github.com/throneproj/Throne/releases/download/1.0.13/Throne-1.0.13-windows64.zip',
    'throne-win7': 'https://github.com/throneproj/Throne/releases/download/1.0.13/Throne-1.0.13-windowslegacy64.zip',
    'throne-linux': 'https://github.com/throneproj/Throne/releases/download/1.0.13/Throne-1.0.13-linux-amd64.zip',
}

def get_cached_links():
    """Получить кэшированные ссылки если они актуальны"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
                cache_time = datetime.fromisoformat(cache.get('timestamp', ''))
                if datetime.now() - cache_time < CACHE_DURATION:
                    return cache.get('links')
        except Exception as e:
            print(f"Ошибка при чтении кэша: {e}")
    return None

def save_links_cache(links):
    """Сохранить ссылки в кэш"""
    # В режиме отладки не сохраняем кэш
    if DEBUG_MODE:
        return

    cache = {
        'timestamp': datetime.now().isoformat(),
        'links': links
    }
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Ошибка при сохранении кэша: {e}")

def fetch_download_links():
    """Получить актуальные ссылки с GitHub API"""
    # В режиме отладки используем заглушки
    if DEBUG_MODE:
        print("⚙️ DEBUG MODE: Используем заглушки для ссылок на скачивание")
        return FALLBACK_LINKS.copy()
    
    links = {}

    try:
        # v2rayNG
        print("Получение v2rayNG...")
        response = requests.get('https://api.github.com/repos/2dust/v2rayNG/releases/latest', timeout=10)
        print(f"v2rayNG ответ: {response.status_code}")
        if response.status_code == 200:
            releases = response.json()
            apk = select_v2rayng_apk(releases.get('assets', []))
            if apk:
                links['v2rayng-apk'] = apk['browser_download_url']
                print(f"v2rayNG ссылка: {links['v2rayng-apk']}")
        else:
            print(f"Ошибка GitHub API для v2rayNG: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при получении v2rayNG: {e}")

    try:
        # Throne
        print("Получение Throne...")
        response = requests.get('https://api.github.com/repos/throneproj/Throne/releases/latest', timeout=10)
        print(f"Throne ответ: {response.status_code}")
        if response.status_code == 200:
            releases = response.json()
            throne_win10 = next((a for a in releases.get('assets', []) if 'windows64' in a['name'] and 'legacy' not in a['name']), None)
            throne_win7 = next((a for a in releases.get('assets', []) if 'windowslegacy64' in a['name']), None)
            throne_linux = next((a for a in releases.get('assets', []) if 'linux-amd64' in a['name']), None)

            if throne_win10:
                links['throne-win10'] = throne_win10['browser_download_url']
                print(f"Throne Win10 ссылка: {links['throne-win10']}")
            if throne_win7:
                links['throne-win7'] = throne_win7['browser_download_url']
                print(f"Throne Win7 ссылка: {links['throne-win7']}")
            if throne_linux:
                links['throne-linux'] = throne_linux['browser_download_url']
                print(f"Throne Linux ссылка: {links['throne-linux']}")
        else:
            print(f"Ошибка GitHub API для Throne: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при получении Throne: {e}")

    return links if links else None

# Кэш для ссылки на Visual C++ Runtimes
VC_RUNTIME_CACHE_FILE = 'vc_runtime_link_cache.json'
VC_RUNTIME_CACHE_DURATION = timedelta(hours=24)
VC_RUNTIME_FALLBACK = 'https://cf.comss.org/download/Visual-C-Runtimes-All-in-One-Dec-2025.zip'

def get_cached_vc_runtime_link():
    """Получить кэшированную ссылку на Visual C++ Runtimes если она актуальна"""
    # В режиме отладки не используем кэш
    if DEBUG_MODE:
        return None
    
    if os.path.exists(VC_RUNTIME_CACHE_FILE):
        try:
            with open(VC_RUNTIME_CACHE_FILE, 'r') as f:
                cache = json.load(f)
                cache_time = datetime.fromisoformat(cache.get('timestamp', ''))
                if datetime.now() - cache_time < VC_RUNTIME_CACHE_DURATION:
                    return cache.get('link')
        except Exception as e:
            print(f"Ошибка при чтении кэша VC Runtime: {e}")
    return None

def save_vc_runtime_link_cache(link):
    """Сохранить ссылку на Visual C++ Runtimes в кэш"""
    # В режиме отладки не сохраняем кэш
    if DEBUG_MODE:
        return
    
    cache = {
        'timestamp': datetime.now().isoformat(),
        'link': link
    }
    try:
        with open(VC_RUNTIME_CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Ошибка при сохранении кэша VC Runtime: {e}")

def fetch_vc_runtime_link():
    """Получить актуальную ссылку на Visual C++ Runtimes с comss.ru"""
    # В режиме отладки используем заглушку
    if DEBUG_MODE:
        print("⚙️ DEBUG MODE: Используем заглушку для VC Runtime ссылки")
        return VC_RUNTIME_FALLBACK
    
    url = 'https://www.comss.ru/download/page.php?id=6271'
    
    try:
        print(f"Получение ссылки на Visual C++ Runtimes с {url}...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем кнопку "скачать как" и связанные элементы
        # Ссылка обычно находится в data-атрибутах или в onclick обработчиках
        download_link = None
        
        # Ищем все ссылки, содержащие dl.comss.org
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'dl.comss.org' in href and 'Visual-C-Runtimes' in href:
                download_link = href
                break
        
        # Если не нашли, ищем в data-атрибутах кнопок
        if not download_link:
            for btn in soup.find_all('button', {'data-toggle': 'dropdown'}):
                if 'скачать как' in btn.get_text().lower():
                    # Ищем родительский элемент с данными
                    parent = btn.find_parent()
                    if parent:
                        # Ищем ссылки в выпадающем меню
                        dropdown_menu = parent.find('div', class_='dropdown-menu') or parent.find('ul', class_='dropdown-menu')
                        if dropdown_menu:
                            for link in dropdown_menu.find_all('a', href=True):
                                href = link.get('href', '')
                                if 'dl.comss.org' in href and 'Visual-C-Runtimes' in href:
                                    download_link = href
                                    break
                                # Также проверяем data-атрибуты
                                data_url = link.get('data-url') or link.get('data-href')
                                if data_url and 'dl.comss.org' in data_url and 'Visual-C-Runtimes' in data_url:
                                    download_link = data_url
                                    break
                        if download_link:
                            break
        
        # Если всё ещё не нашли, пробуем найти в JavaScript коде страницы
        if not download_link:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # Ищем URL в формате https://dl.comss.org/download/...
                    matches = re.findall(r'https://dl\.comss\.org/download/Visual-C-Runtimes[^\s\'"]+', script.string)
                    if matches:
                        download_link = matches[0]
                        break
        
        if download_link:
            print(f"Найдена ссылка на Visual C++ Runtimes: {download_link}")
            return download_link
        else:
            print("Не удалось найти ссылку на Visual C++ Runtimes, используем fallback")
            return VC_RUNTIME_FALLBACK
            
    except Exception as e:
        print(f"Ошибка при получении Visual C++ Runtimes: {e}")
        return VC_RUNTIME_FALLBACK

@app.route('/')
def home():
    configs = get_vpn_configs()
    analytics_ids = get_analytics_ids()
    site_url = get_site_url()
    # Гарантируем абсолютный URL для canonical
    canonical_url = site_url if site_url else request.url_root.rstrip('/') + '/'
    meta_title = os.environ.get('META_TITLE', DEFAULT_META_TITLE)
    meta_description = os.environ.get('META_DESCRIPTION', DEFAULT_META_DESCRIPTION)
    meta_keywords = os.environ.get('META_KEYWORDS', DEFAULT_META_KEYWORDS)
    og_image = os.environ.get('OG_IMAGE_URL')
    return render_template(
        'index.html',
        configs=configs,
        analytics_ids=analytics_ids,
        site_url=site_url,
        canonical_url=canonical_url,
        download_links=FALLBACK_LINKS,
        vc_runtime_link=VC_RUNTIME_FALLBACK,
        meta_title=meta_title,
        meta_description=meta_description,
        meta_keywords=meta_keywords,
        og_image=og_image
    )

@app.route('/robots.txt')
def robots_txt():
    site_url = get_site_url()
    content = generate_robots_txt(site_url)
    return Response(content, mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap_xml():
    site_url = get_site_url()
    content = generate_sitemap_xml(site_url)
    return Response(content, mimetype='application/xml')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'favicon.png', mimetype='image/png')

@app.route('/api/download-links')
def get_download_links():
    """API endpoint для получения ссылок на скачивание"""
    # Сначала проверяем кэш
    cached = get_cached_links()
    if cached:
        print("Возвращаем кэшированные ссылки")
        return jsonify(cached)
    
    # Если кэша нет или он устарел, получаем новые ссылки
    print("Получаем новые ссылки с GitHub")
    fetched_links = fetch_download_links()
    
    if fetched_links:
        links = FALLBACK_LINKS.copy()
        links.update(fetched_links)
        save_links_cache(links)
        print(f"Возвращаем новые ссылки: {links}")
        return jsonify(links)
    
    # Fallback - возвращаем ссылки по умолчанию
    print("Возвращаем fallback ссылки")
    return jsonify(FALLBACK_LINKS)

@app.route('/api/vc-runtime-link')
def get_vc_runtime_link():
    """API endpoint для получения ссылки на Visual C++ Runtimes"""
    # Сначала проверяем кэш
    cached = get_cached_vc_runtime_link()
    if cached:
        print("Возвращаем кэшированную ссылку на VC Runtime")
        return jsonify({'link': cached})

    # Если кэша нет или он устарел, получаем новую ссылку
    print("Получаем новую ссылку на VC Runtime")
    link = fetch_vc_runtime_link()

    if link:
        save_vc_runtime_link_cache(link)
        print(f"Возвращаем новую ссылку на VC Runtime: {link}")
        return jsonify({'link': link})

    # Fallback - возвращаем резервную ссылку
    print("Возвращаем fallback ссылку на VC Runtime")
    return jsonify({'link': VC_RUNTIME_FALLBACK})

# Маршруты для статических JSON файлов (для совместимости с фронтендом)
@app.route('/api/download-links.json')
def get_download_links_json():
    """Отдает JSON файл ссылок на скачивание (для фронтенда)"""
    return get_download_links()

@app.route('/api/vc-runtime-link.json')
def get_vc_runtime_link_json():
    """Отдает JSON файл ссылки на VC Runtime (для фронтенда)"""
    return get_vc_runtime_link()

@app.route('/api/github-stats.json')
def get_github_stats_json():
    """Отдает JSON файл статистики GitHub (для фронтенда)"""
    return get_github_stats()

# Кэш для статистики GitHub
STATS_CACHE_FILE = 'github_stats_cache.json'
STATS_CACHE_DURATION = timedelta(hours=1)

BADGES = {
    'python.svg': 'https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54',
    'license.svg': 'https://img.shields.io/badge/License-GPL--3.0-blue?style=for-the-badge',
    'stars.svg': 'https://img.shields.io/github/stars/AvenCores/goida-vpn-configs?style=for-the-badge',
    'forks.svg': 'https://img.shields.io/github/forks/AvenCores/goida-vpn-configs?style=for-the-badge',
    'prs.svg': 'https://img.shields.io/github/issues-pr/AvenCores/goida-vpn-configs?style=for-the-badge',
    'issues.svg': 'https://img.shields.io/github/issues/AvenCores/goida-vpn-configs?style=for-the-badge'
}
STATS_REPO = 'AvenCores/goida-vpn-configs'

def download_badges():
    """Скачивает бэджи локально для кэширования"""
    # В режиме отладки не скачиваем бэджи
    if DEBUG_MODE:
        print("⚙️ DEBUG MODE: Пропуск загрузки бэджей")
        return

    badges_dir = os.path.join('static', 'images', 'badges')
    if not os.path.exists(badges_dir):
        os.makedirs(badges_dir)
    
    print("Загрузка бэджей...")
    for filename, url in BADGES.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(os.path.join(badges_dir, filename), 'wb') as f:
                    f.write(response.content)
                print(f"✅ Бэдж {filename} обновлен")
            else:
                print(f"⚠️ Не удалось загрузить бэдж {filename}: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка при загрузке бэджа {filename}: {e}")

def create_github_stats_payload(error: str | None = None) -> dict:
    return {
        'pushed_at': None,
        'stargazers_count': 0,
        'clones': {'count': 0, 'uniques': 0},
        'views': {'count': 0, 'uniques': 0},
        'referrers': [],
        'popular_content': [],
        'error': error
    }

def fetch_github_stats_data(token: str | None = None) -> dict:
    """Получить статистику репозитория в едином формате для API и static build."""
    if DEBUG_MODE:
        stats = create_github_stats_payload()
        stats['pushed_at'] = datetime.utcnow().isoformat() + 'Z'
        return stats

    stats = create_github_stats_payload()
    base_url = f'https://api.github.com/repos/{STATS_REPO}'
    public_headers = {'Accept': 'application/vnd.github.v3+json'}

    try:
        repo_response = requests.get(base_url, headers=public_headers, timeout=10)
        repo_response.raise_for_status()
        repo_data = repo_response.json()
        stats['pushed_at'] = repo_data.get('pushed_at')
        stats['stargazers_count'] = repo_data.get('stargazers_count', 0)
    except requests.exceptions.RequestException as e:
        stats['error'] = str(e)
        return stats

    if not token:
        stats['error'] = 'Token not configured'
        return stats

    auth_headers = {
        **public_headers,
        'Authorization': f'token {token}'
    }
    traffic_requests = (
        ('clones', 'clones'),
        ('views', 'views'),
        ('popular/referrers', 'referrers'),
        ('popular/paths', 'popular_content'),
    )

    for endpoint, field in traffic_requests:
        try:
            response = requests.get(f'{base_url}/traffic/{endpoint}', headers=auth_headers, timeout=10)
            if not response.ok:
                print(f"Warning: GitHub traffic API /{endpoint} returned {response.status_code}")
                continue
            payload = response.json()
            if field in ('clones', 'views'):
                stats[field]['count'] = payload.get('count', 0)
                stats[field]['uniques'] = payload.get('uniques', 0)
            else:
                stats[field] = payload
        except requests.exceptions.RequestException as e:
            print(f"Warning: GitHub traffic API /{endpoint} failed: {e}")

    return stats

def get_cached_stats():
    """Получить кэшированную статистику, если она актуальна"""
    if os.path.exists(STATS_CACHE_FILE):
        try:
            with open(STATS_CACHE_FILE, 'r') as f:
                cache = json.load(f)
                cache_time = datetime.fromisoformat(cache.get('timestamp', ''))
                if datetime.now() - cache_time < STATS_CACHE_DURATION:
                    return cache.get('data')
        except Exception as e:
            print(f"Ошибка при чтении кэша статистики: {e}")
    return None

def save_stats_cache(data):
    """Сохранить статистику в кэш"""
    # В режиме отладки не сохраняем кэш
    if DEBUG_MODE:
        return

    cache = {
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    try:
        with open(STATS_CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Ошибка при сохранении кэша статистики: {e}")

@app.route('/api/github-stats')
def get_github_stats():
    """API endpoint для получения статистики репозитория с кэшированием"""
    # Сначала проверяем кэш
    cached_stats = get_cached_stats()
    if cached_stats:
        print("Возвращаем кэшированную статистику GitHub")
        return jsonify(cached_stats)

    stats = fetch_github_stats_data(os.getenv('MY_TOKEN'))
    if stats.get('error') in (None, 'Token not configured'):
        save_stats_cache(stats)
    return jsonify(stats)

@app.route('/LICENSE')
def serve_license():
    return send_from_directory('static', 'LICENSE')

if __name__ == '__main__':

    # Настройка логгера
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='Goida VPN Site')
    parser.add_argument('--debug', action='store_true', help='Режим отладки с автоперезагрузкой')
    parser.add_argument('--host', default='127.0.0.1', help='Хост для прослушивания')
    parser.add_argument('--port', type=int, default=5000, help='Порт для прослушивания')
    args = parser.parse_args()

    # Синхронизируем режим отладки
    set_debug_mode(args.debug)
    app.config['DEBUG'] = args.debug

    # ✅ Надёжная проверка: выполняется ли код в дочернем процессе релоадера
    # Werkzeug может устанавливать 'true' или '1' в зависимости от версии
    is_reloader_child = os.environ.get('WERKZEUG_RUN_MAIN') in ('true', '1')

    # Инициализация только в родительском процессе (чтобы не было дублей)
    if not is_reloader_child:
        download_badges()
        log.info("🔧 Запуск в режиме ОТЛАДКИ (auto-reload & debugger включены)")
        log.info(f"📍 Сайт доступен на http://{args.host}:{args.port}")

    host = args.host
    port = args.port

    if args.debug:
        # use_reloader=True по умолчанию при debug=True, но указываем явно для наглядности
        app.run(host=host, port=port, debug=True, use_reloader=True)
    else:
        # В продакшене логи выводятся один раз, так как релоадер не используется
        if not is_reloader_child:
            log.info(f"🚀 Запуск в ПРОДАКШЕН режиме (Waitress)")
            log.info(f"📍 Сайт доступен на http://{host}:{port}")
        serve(app, host=host, port=port)
