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


def minify_html(html: str) -> str:
    """Keep generated HTML readable enough while removing avoidable whitespace."""
    html = html.replace("\r\n", "\n").replace("\r", "\n")
    html = re.sub(r"[ \t]+$", "", html, flags=re.MULTILINE)
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()


def build_site() -> None:
    print(f"Building site into ./{DIST_DIR}...")
    download_badges()

    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)
    os.makedirs(os.path.join(DIST_DIR, "api"))

    if os.path.exists("static"):
        shutil.copytree("static", os.path.join(DIST_DIR, "static"))
        print("Copied static assets")

    translations_src = "static/i18n/translations.json"
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
