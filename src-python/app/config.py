import os
from datetime import timedelta

# Базовая директория проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Глобальная переменная для режима отладки
DEBUG_MODE = False

def set_debug_mode(enabled: bool):
    """Установить режим отладки глобально"""
    global DEBUG_MODE
    DEBUG_MODE = enabled

# SEO по умолчанию (может быть переопределено переменными окружения в продакшене)
DEFAULT_META_TITLE = "Goida VPN Configs"
DEFAULT_META_DESCRIPTION = (
    "Автоматические VPN-конфиги для V2Ray, VLESS, Hysteria, Trojan, VMess, Reality и Shadowsocks. "
    "Обновление каждые 9 минут, удобные ссылки и QR-коды."
)
DEFAULT_META_KEYWORDS = "vpn, vless, v2ray, shadowsocks, hysteria, trojan, vmess, reality, vpn configs, free vpn, goida vpn, обход блокировок, автоматичні vpn конфіги, обхід блокувань, бесплатные vpn, xray, proxy, прокси, whitelist bypass, obход снд, sni bypass, vpn subscription, vpn конфиги, vpn configs free, автоматические vpn, vpn для россии, vpn для украины, vpn настройка, v2rayng, throne vpn, proxy list, бесплатные прокси, конфигурации vpn, vpn android, vpn windows, vpn ios, vpn macos, vpn linux, безопасный интернет, анонимность в сети, приватность, шифрование трафика, xray core, v2fly, проект xray, mtp roto, reality tls, hysteria 2, juicity, tuic, wireguard, openvpn, softether, neutronvpn, npv, vpn 2024, vpn 2025, рабочий vpn, стабильный vpn, быстрый vpn"

# Fallback ссылки на случай, если GitHub API недоступен
FALLBACK_LINKS = {
    'v2rayng-apk': 'https://github.com/2dust/v2rayNG/releases/download/2.0.13/v2rayNG_2.0.13_universal.apk',
    'throne-win10': 'https://github.com/throneproj/Throne/releases/download/1.0.13/Throne-1.0.13-windows64.zip',
    'throne-win7': 'https://github.com/throneproj/Throne/releases/download/1.0.13/Throne-1.0.13-windowslegacy64.zip',
    'throne-linux': 'https://github.com/throneproj/Throne/releases/download/1.0.13/Throne-1.0.13-linux-amd64.zip',
}

# Кэш для ссылок на скачивание
DOWNLOAD_CACHE_FILE = os.path.join(BASE_DIR, 'download_links_cache.json')
DOWNLOAD_CACHE_DURATION = timedelta(hours=24)

# Ссылка на Visual C++ Runtimes
VC_RUNTIME_CACHE_FILE = os.path.join(BASE_DIR, 'vc_runtime_link_cache.json')
VC_RUNTIME_CACHE_DURATION = timedelta(hours=24)
VC_RUNTIME_FALLBACK = 'https://cf.comss.org/download/Visual-C-Runtimes-All-in-One-Dec-2025.zip'

# Бэджи для скачивания
BADGES = {
    'python.svg': 'https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54',
    'license.svg': 'https://img.shields.io/badge/License-GPL--3.0-blue?style=for-the-badge',
    'stars.svg': 'https://img.shields.io/github/stars/AvenCores/goida-vpn-configs?style=for-the-badge',
    'forks.svg': 'https://img.shields.io/github/forks/AvenCores/goida-vpn-configs?style=for-the-badge',
    'prs.svg': 'https://img.shields.io/github/issues-pr/AvenCores/goida-vpn-configs?style=for-the-badge',
    'issues.svg': 'https://img.shields.io/github/issues/AvenCores/goida-vpn-configs?style=for-the-badge'
}

# Кэш для статистики GitHub
STATS_REPO = 'AvenCores/goida-vpn-configs'
STATS_CACHE_FILE = os.path.join(BASE_DIR, 'github_stats_cache.json')
STATS_CACHE_DURATION = timedelta(hours=1)

# Кэш для обновлений VPN таблиц
VPN_CACHE_DURATION = timedelta(hours=1)

# Маппинг источников для каждого конфига
SOURCES_MAP = {
    1: "https://github.com/sakha1370/OpenRay",
    2: "https://github.com/sevcator/5ubscrpt10n",
    3: "https://github.com/yitong2333/proxy-minging",
    4: "https://github.com/acymz/AutoVPN",
    5: "https://github.com/miladtahanian/V2RayCFGDumper",
    6: "https://github.com/roosterkid/openproxylist",
    7: "https://github.com/Epodonios/v2ray-configs",
    8: "https://github.com/ShatakVPN/ConfigForge-V2Ray",
    9: "https://github.com/mohamadfg-dev/telegram-v2ray-configs-collector",
    10: "https://github.com/mheidari98/.proxy",
    11: "https://github.com/youfoundamin/V2rayCollector",
    12: "https://github.com/VOID-Anonymity/V.O.I.D-VPN_Bypass",
    13: "https://github.com/MahsaNetConfigTopic/config",
    14: "https://github.com/LalatinaHub/Mineral",
    15: "https://github.com/miladtahanian/Config-Collector",
    16: "https://github.com/Pawdroid/Free-servers",
    17: "https://github.com/MhdiTaheri/V2rayCollector_Py",
    18: "https://github.com/free18/v2ray/",
    19: "https://github.com/MhdiTaheri/V2rayCollector",
    20: "https://github.com/Argh94/Proxy-List",
    21: "https://github.com/shabane/kamaji",
    22: "https://github.com/wuqb2i4f/xray-config-toolkit",
    23: "https://github.com/igareck/vpn-configs-for-russia",
    24: "https://github.com/Mr-Meshky/vify",
    25: "https://github.com/V2RayRoot/V2RayConfig",
    26: [
        "https://github.com/EtoNeYaProject/etoneyaproject.github.io",
        "https://github.com/igareck/vpn-configs-for-russia",
        "https://github.com/ByeWhiteLists/ByeWhiteLists2",
        "https://gitverse.ru/cid-uskoritel/cid-white",
        "https://github.com/zieng2/wl",
        "https://etoneya.a9fm.site/"
    ]
}
