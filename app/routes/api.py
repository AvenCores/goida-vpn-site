import os
from flask import Blueprint, jsonify
from app.services.github import (
    get_cached_links, fetch_download_links, save_links_cache,
    get_cached_stats, fetch_github_stats_data, save_stats_cache
)
from app.services.vc_runtime import (
    get_cached_vc_runtime_link, fetch_vc_runtime_link, save_vc_runtime_link_cache
)
from app.config import FALLBACK_LINKS, VC_RUNTIME_FALLBACK

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/download-links')
@api_bp.route('/download-links.json')
def get_download_links():
    """API endpoint для получения ссылок на скачивание"""
    cached = get_cached_links()
    if cached:
        print("Возвращаем кэшированные ссылки")
        return jsonify(cached)
    
    print("Получаем новые ссылки с GitHub")
    fetched_links = fetch_download_links()
    
    if fetched_links:
        links = FALLBACK_LINKS.copy()
        links.update(fetched_links)
        save_links_cache(links)
        print(f"Возвращаем новые ссылки: {links}")
        return jsonify(links)
    
    print("Возвращаем fallback ссылки")
    return jsonify(FALLBACK_LINKS)

@api_bp.route('/vc-runtime-link')
@api_bp.route('/vc-runtime-link.json')
def get_vc_runtime_link():
    """API endpoint для получения ссылки на Visual C++ Runtimes"""
    cached = get_cached_vc_runtime_link()
    if cached:
        print("Возвращаем кэшированную ссылку на VC Runtime")
        return jsonify({'link': cached})

    print("Получаем новую ссылку на VC Runtime")
    link = fetch_vc_runtime_link()

    if link:
        save_vc_runtime_link_cache(link)
        print(f"Возвращаем новую ссылку на VC Runtime: {link}")
        return jsonify({'link': link})

    print("Возвращаем fallback ссылку на VC Runtime")
    return jsonify({'link': VC_RUNTIME_FALLBACK})

@api_bp.route('/github-stats')
@api_bp.route('/github-stats.json')
def get_github_stats():
    """API endpoint для получения статистики репозитория с кэшированием"""
    cached_stats = get_cached_stats()
    if cached_stats:
        print("Возвращаем кэшированную статистику GitHub")
        return jsonify(cached_stats)

    stats = fetch_github_stats_data(os.getenv('MY_TOKEN'))
    if stats.get('error') in (None, 'Token not configured'):
        save_stats_cache(stats)
    return jsonify(stats)
