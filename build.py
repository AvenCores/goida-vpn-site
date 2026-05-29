import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime

from flask import render_template

# Импорты из нового модульного пакета app
from app import create_app
from app.config import (
    DEFAULT_META_DESCRIPTION,
    DEFAULT_META_KEYWORDS,
    DEFAULT_META_TITLE,
    FALLBACK_LINKS,
    VC_RUNTIME_FALLBACK,
)
from app.services.github import (
    download_badges,
    fetch_download_links,
    fetch_github_stats_data,
)
from app.services.vc_runtime import fetch_vc_runtime_link
from app.services.vpn import get_vpn_configs
from app.utils import (
    generate_robots_txt,
    generate_sitemap_xml,
    get_analytics_ids,
    normalize_site_url,
)

app = create_app()

REPO_USER = "AvenCores"
REPO_NAME = "goida-vpn-site"
TARGET_REPO = f"https://github.com/{REPO_USER}/{REPO_NAME}.git"
DIST_DIR = "dist"
BRANCH = "gh-pages"
PWA_ROOT_FILES = ("manifest.webmanifest", "sw.js")


def minify_html(html: str) -> str:
    """Perform a clean, robust minification of the HTML content by stripping comments and unnecessary indentations."""
    # 1. Remove HTML comments
    html = re.sub(r"<!--[\s\S]*?-->", "", html)
    # 2. Normalize line endings
    html = html.replace("\r\n", "\n").replace("\r", "\n")
    # 3. Collapse multiple spaces and tabs inside lines
    html = re.sub(r"[ \t]+", " ", html)
    # 4. Remove trailing whitespace on each line
    html = re.sub(r"[ \t]+$", "", html, flags=re.MULTILINE)
    # 5. Strip all indentation for lines starting with HTML tags (saves massive bytes safely)
    html = re.sub(r"^[ \t]+<", "<", html, flags=re.MULTILINE)
    # 6. Collapse multiple blank lines
    html = re.sub(r"\n{2,}", "\n", html)
    return html.strip()


def download_external_assets() -> None:
    """Download all required external frontend assets to make the website completely self-hosted."""
    assets = [
        # Alpine JS
        ("https://cdn.jsdelivr.net/npm/@alpinejs/collapse@3.x.x/dist/cdn.min.js", "app/static/js/alpine-collapse.min.js"),
        ("https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js", "app/static/js/alpine.min.js"),
        # Tailwind Fallback
        ("https://cdn.tailwindcss.com", "app/static/js/tailwind.min.js"),
        # FontAwesome CSS
        ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css", "app/static/css/all.min.css"),
        # FontAwesome Fonts
        ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/webfonts/fa-solid-900.woff2", "app/static/webfonts/fa-solid-900.woff2"),
        ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/webfonts/fa-regular-400.woff2", "app/static/webfonts/fa-regular-400.woff2"),
        ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/webfonts/fa-brands-400.woff2", "app/static/webfonts/fa-brands-400.woff2"),
        # Flags
        ("https://flagcdn.com/w20/ru.png", "app/static/images/flags/ru.png"),
        ("https://flagcdn.com/w40/ru.png", "app/static/images/flags/ru@2x.png"),
        ("https://flagcdn.com/w20/gb.png", "app/static/images/flags/gb.png"),
        ("https://flagcdn.com/w40/gb.png", "app/static/images/flags/gb@2x.png"),
        ("https://flagcdn.com/w20/de.png", "app/static/images/flags/de.png"),
        ("https://flagcdn.com/w40/de.png", "app/static/images/flags/de@2x.png"),
        ("https://flagcdn.com/w20/ua.png", "app/static/images/flags/ua.png"),
        ("https://flagcdn.com/w40/ua.png", "app/static/images/flags/ua@2x.png"),
        ("https://flagcdn.com/w20/by.png", "app/static/images/flags/by.png"),
        ("https://flagcdn.com/w40/by.png", "app/static/images/flags/by@2x.png"),
    ]

    import requests
    print("Checking and downloading external assets...")
    for url, path in assets:
        dir_name = os.path.dirname(path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        if not os.path.exists(path):
            print(f"Downloading {url} -> {path}...")
            try:
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    with open(path, "wb") as f:
                        f.write(r.content)
                    print(f"Successfully downloaded {path}")
                else:
                    print(f"ERROR: Failed to download {url}: HTTP {r.status_code}")
            except Exception as e:
                print(f"ERROR: Failed to download {url}: {e}")


def build_site() -> None:
    print(f"Building site into ./{DIST_DIR}...")
    download_external_assets()
    download_badges()

    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)
    os.makedirs(os.path.join(DIST_DIR, "api"))

    if os.path.exists("app/static"):
        shutil.copytree("app/static", os.path.join(DIST_DIR, "static"))
        print("Copied static assets")

    for filename in PWA_ROOT_FILES:
        src_path = os.path.join("app", "static", filename)
        if os.path.exists(src_path):
            shutil.copy2(src_path, os.path.join(DIST_DIR, filename))
            print(f"Copied {filename}")

    translations_src = "app/static/i18n/translations.json"
    if os.path.exists(translations_src):
        i18n_dir = os.path.join(DIST_DIR, "static", "i18n")
        os.makedirs(i18n_dir, exist_ok=True)
        shutil.copy2(translations_src, os.path.join(i18n_dir, "translations.json"))
        print("Copied translations.json")

    site_url = normalize_site_url(
        os.getenv("SITE_URL") or f"https://{REPO_USER.lower()}.github.io/{REPO_NAME}/"
    )

    with app.test_request_context():
        print("Rendering index.html...")
        analytics_ids = get_analytics_ids()
        if not analytics_ids.get("yandex_autoplacement_id"):
            print("WARNING: YANDEX_AUTOPLACEMENT_ID is not set, skipping Yandex Autoplacement")

        rendered_html = render_template(
            "index.html",
            configs=get_vpn_configs(),
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
            f.write(minify_html(rendered_html))
        print("Created index.html")

    api_path = os.path.join(DIST_DIR, "api")

    print("Fetching download links...")
    fetched_links = fetch_download_links()
    download_links = FALLBACK_LINKS.copy()
    if fetched_links:
        download_links.update(fetched_links)
    else:
        print("WARNING: using fallback download links")

    with open(os.path.join(api_path, "download-links.json"), "w", encoding="utf-8") as f:
        json.dump(download_links, f, ensure_ascii=False)
    print("Created download-links.json")

    print("Fetching Visual C++ Runtime link...")
    vc_runtime_link = fetch_vc_runtime_link() or VC_RUNTIME_FALLBACK
    with open(os.path.join(api_path, "vc-runtime-link.json"), "w", encoding="utf-8") as f:
        json.dump({"link": vc_runtime_link}, f, ensure_ascii=False)
    print("Created vc-runtime-link.json")

    print("Fetching GitHub stats...")
    fetch_and_save_github_stats(api_path)

    with open(os.path.join(DIST_DIR, ".nojekyll"), "w", encoding="utf-8"):
        pass

    with open(os.path.join(DIST_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(generate_robots_txt(site_url))

    lastmod = datetime.utcnow().date().isoformat()
    with open(os.path.join(DIST_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(generate_sitemap_xml(site_url, lastmod=lastmod))


def fetch_and_save_github_stats(api_path: str) -> None:
    stats = fetch_github_stats_data(os.getenv("MY_TOKEN") or os.getenv("GITHUB_TOKEN"))
    with open(os.path.join(api_path, "github-stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False)
    print("Saved github-stats.json")


def run_git_command(
    label: str,
    command: list[str],
    cwd: str,
    redactions: list[str] | None = None,
) -> bool:
    redactions = [value for value in (redactions or []) if value]
    try:
        subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {label}")
        stderr = e.stderr or ""
        for secret in redactions:
            stderr = stderr.replace(secret, "[redacted]")
        if stderr.strip():
            print(f"Details: {stderr.strip()}")
        return False


def deploy_to_github() -> bool:
    token = os.getenv("MY_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token:
        print("ERROR: deployment token is not configured. Set MY_TOKEN or GITHUB_TOKEN.")
        return False

    if not os.path.isdir(DIST_DIR):
        print(f"ERROR: {DIST_DIR}/ does not exist. Build the site before deploying.")
        return False

    print(f"Deploying to {BRANCH}...")
    cwd = os.path.abspath(DIST_DIR)
    commands = [
        ("init", ["git", "init"]),
        ("config user.name", ["git", "config", "user.name", "Auto Builder"]),
        ("config user.email", ["git", "config", "user.email", "actions@github.com"]),
        ("add files", ["git", "add", "."]),
        ("commit", ["git", "commit", "-m", "Deploy site update"]),
        ("set branch", ["git", "branch", "-M", BRANCH]),
        ("add remote", ["git", "remote", "add", "origin", TARGET_REPO]),
    ]

    for label, command in commands:
        if not run_git_command(label, command, cwd):
            return False

    credentials = base64.b64encode(f"x-access-token:{token}".encode("utf-8")).decode("ascii")
    auth_header = f"AUTHORIZATION: basic {credentials}"
    push_command = [
        "git",
        "-c",
        f"http.https://github.com/.extraheader={auth_header}",
        "push",
        "-f",
        "origin",
        BRANCH,
    ]
    if not run_git_command("push", push_command, cwd, redactions=[token, credentials, auth_header]):
        return False

    print(f"Site deployed to {BRANCH}")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Goida VPN static site.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--deploy", action="store_true", help="Build and deploy to GitHub Pages.")
    mode.add_argument("--build-only", action="store_true", help="Build without deploying. This is the default.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build_site()
    if args.deploy:
        return 0 if deploy_to_github() else 1

    print(f"Build complete: ./{DIST_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
