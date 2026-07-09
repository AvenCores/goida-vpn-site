import concurrent.futures
import os
import requests
import json
from datetime import datetime
from app.config import (
    FALLBACK_LINKS, DOWNLOAD_CACHE_FILE, DOWNLOAD_CACHE_DURATION,
    STATS_REPO, STATS_CACHE_FILE, STATS_CACHE_DURATION, BADGES
)
import app.config as config_module

def select_v2rayng_apk(assets):
    """Выбирает APK (arm64-v8a) для обычного Android."""
    # 1. Try arm64-v8a.apk (excluding fdroid / sig) - most common standard architecture
    for asset in assets:
        name_lower = asset.get('name', '').lower()
        if name_lower.endswith('.apk') and 'arm64-v8a' in name_lower and 'f-droid' not in name_lower and 'fdroid' not in name_lower:
            return asset

    # 2. Try universal as fallback just in case
    for asset in assets:
        name_lower = asset.get('name', '').lower()
        if name_lower.endswith('.apk') and 'universal' in name_lower and 'f-droid' not in name_lower and 'fdroid' not in name_lower:
            return asset

    # 3. Try any apk (excluding fdroid / sig)
    for asset in assets:
        name_lower = asset.get('name', '').lower()
        if name_lower.endswith('.apk') and 'f-droid' not in name_lower and 'fdroid' not in name_lower:
            return asset

    return None

def select_v2rayng_tv_apk(assets):
    """Выбирает APK для Android TV (armv7)."""
    for asset in assets:
        name_lower = asset.get('name', '').lower()
        if name_lower.endswith('.apk') and 'armeabi-v7a' in name_lower and 'f-droid' not in name_lower and 'fdroid' not in name_lower:
            return asset
    for asset in assets:
        name_lower = asset.get('name', '').lower()
        if name_lower.endswith('.apk') and 'v7a' in name_lower and 'f-droid' not in name_lower and 'fdroid' not in name_lower:
            return asset
    return select_v2rayng_apk(assets)

def get_cached_links():
    """Получить кэшированные ссылки если они актуальны"""
    if os.path.exists(DOWNLOAD_CACHE_FILE):
        try:
            with open(DOWNLOAD_CACHE_FILE, 'r') as f:
                cache = json.load(f)
                cache_time = datetime.fromisoformat(cache.get('timestamp', ''))
                if datetime.now() - cache_time < DOWNLOAD_CACHE_DURATION:
                    return cache.get('links')
        except Exception as e:
            print(f"Ошибка при чтении кэша: {e}")
    return None

def save_links_cache(links):
    """Сохранить ссылки в кэш"""
    if config_module.DEBUG_MODE:
        return

    cache = {
        'timestamp': datetime.now().isoformat(),
        'links': links
    }
    try:
        with open(DOWNLOAD_CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Ошибка при сохранении кэша: {e}")

def _fetch_v2rayng_links() -> dict:
    """Получить ссылки на актуальные APK v2rayNG."""
    links = {}
    try:
        print("Получение v2rayNG...")
        response = requests.get('https://api.github.com/repos/2dust/v2rayNG/releases/latest', timeout=10)
        print(f"v2rayNG ответ: {response.status_code}")
        if response.status_code == 200:
            releases = response.json()
            apk = select_v2rayng_apk(releases.get('assets', []))
            if apk:
                links['v2rayng-apk'] = apk['browser_download_url']
                print(f"v2rayNG ссылка: {links['v2rayng-apk']}")

            tv_apk = select_v2rayng_tv_apk(releases.get('assets', []))
            if tv_apk:
                links['v2rayng-tv-apk'] = tv_apk['browser_download_url']
                print(f"v2rayNG TV ссылка: {links['v2rayng-tv-apk']}")
        else:
            print(f"Ошибка GitHub API для v2rayNG: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при получении v2rayNG: {e}")
    return links


def _fetch_throne_links() -> dict:
    """Получить ссылки на актуальные релизы Throne."""
    links = {}
    try:
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
    return links


def fetch_download_links():
    """Получить актуальные ссылки с GitHub API параллельно."""
    if config_module.DEBUG_MODE:
        print("[DEBUG] DEBUG MODE: Используем заглушки для ссылок на скачивание")
        return FALLBACK_LINKS.copy()

    links = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(_fetch_v2rayng_links), executor.submit(_fetch_throne_links)]
        for future in concurrent.futures.as_completed(futures):
            links.update(future.result())

    return links if links else None

def _download_badge(item: tuple[str, str]) -> None:
    """Скачивает один бэдж в указанную директорию."""
    filename, url = item
    badges_dir = os.path.join(config_module.BASE_DIR, 'app', 'static', 'images', 'badges')
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(os.path.join(badges_dir, filename), 'wb') as f:
                f.write(response.content)
            print(f"[OK] Бэдж {filename} обновлен")
        else:
            print(f"[WARN] Не удалось загрузить бэдж {filename}: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Ошибка при загрузке бэджа {filename}: {e}")


def download_badges():
    """Скачивает бэджи локально для кэширования в параллельном режиме."""
    if config_module.DEBUG_MODE:
        print("[DEBUG] DEBUG MODE: Пропуск загрузки бэджей")
        return

    badges_dir = os.path.join(config_module.BASE_DIR, 'app', 'static', 'images', 'badges')
    if not os.path.exists(badges_dir):
        os.makedirs(badges_dir, exist_ok=True)

    print("Загрузка бэджей...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(_download_badge, BADGES.items()))

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
    if config_module.DEBUG_MODE:
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

    def _fetch_traffic(endpoint_field: tuple[str, str]) -> None:
        endpoint, field = endpoint_field
        try:
            response = requests.get(f'{base_url}/traffic/{endpoint}', headers=auth_headers, timeout=10)
            if not response.ok:
                print(f"Warning: GitHub traffic API /{endpoint} returned {response.status_code}")
                return
            payload = response.json()
            if field in ('clones', 'views'):
                stats[field]['count'] = payload.get('count', 0)
                stats[field]['uniques'] = payload.get('uniques', 0)
            else:
                stats[field] = payload
        except requests.exceptions.RequestException as e:
            print(f"Warning: GitHub traffic API /{endpoint} failed: {e}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(_fetch_traffic, traffic_requests))

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
    if config_module.DEBUG_MODE:
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