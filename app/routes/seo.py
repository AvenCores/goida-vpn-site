import os
from flask import Blueprint, Response, send_from_directory, current_app
from app.utils import get_site_url, generate_robots_txt, generate_sitemap_xml

seo_bp = Blueprint('seo', __name__)

@seo_bp.route('/robots.txt')
def robots_txt():
    site_url = get_site_url()
    content = generate_robots_txt(site_url)
    return Response(content, mimetype='text/plain')

@seo_bp.route('/sitemap.xml')
def sitemap_xml():
    site_url = get_site_url()
    content = generate_sitemap_xml(site_url)
    return Response(content, mimetype='application/xml')

@seo_bp.route('/manifest.webmanifest')
def webmanifest():
    response = send_from_directory(current_app.static_folder, 'manifest.webmanifest', mimetype='application/manifest+json')
    response.headers['Cache-Control'] = 'no-cache'
    return response

@seo_bp.route('/sw.js')
def service_worker():
    response = send_from_directory(current_app.static_folder, 'sw.js', mimetype='application/javascript')
    response.headers['Cache-Control'] = 'no-cache'
    return response

@seo_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.static_folder, 'images'),
                               'favicon.png', mimetype='image/png')

@seo_bp.route('/LICENSE')
def serve_license():
    # Ищет файл в папке static
    return send_from_directory(current_app.static_folder, 'LICENSE')
