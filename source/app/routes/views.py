import os
from flask import Blueprint, render_template, request
from app.services.vpn import get_vpn_configs
from app.utils import get_analytics_ids, get_site_url
from app.config import (
    DEFAULT_META_TITLE, DEFAULT_META_DESCRIPTION, DEFAULT_META_KEYWORDS,
    FALLBACK_LINKS, VC_RUNTIME_FALLBACK
)

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
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
