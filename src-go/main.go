package main

import (
	"encoding/base64"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/flosch/pongo2/v6"
)

func init() {
	pongo2.RegisterFilter("tojson", func(in *pongo2.Value, param *pongo2.Value) (*pongo2.Value, *pongo2.Error) {
		b, err := json.Marshal(in.Interface())
		if err != nil {
			return pongo2.AsSafeValue(""), nil
		}
		// Return as safe HTML to prevent escaping quotes
		return pongo2.AsSafeValue(string(b)), nil
	})
	pongo2.RegisterFilter("default", func(in *pongo2.Value, param *pongo2.Value) (*pongo2.Value, *pongo2.Error) {
		if !in.IsTrue() {
			return param, nil
		}
		return in, nil
	})
}

const (
	distDir = "dist"
	branch  = "gh-pages"
)

var (
	targetRepo        = "https://github.com/AvenCores/goida-vpn-site.git"
	vcRuntimeFallback = "https://cf.comss.org/download/Visual-C-Runtimes-All-in-One-Dec-2025.zip"
	fallbackLinks    = map[string]string{
		"v2rayng-apk":  "https://github.com/2dust/v2rayNG/releases/download/2.0.13/v2rayNG_2.0.13_universal.apk",
		"throne-win10": "https://github.com/throneproj/Throne/releases/download/1.0.13/Throne-1.0.13-windows64.zip",
		"throne-win7":  "https://github.com/throneproj/Throne/releases/download/1.0.13/Throne-1.0.13-windowslegacy64.zip",
		"throne-linux": "https://github.com/throneproj/Throne/releases/download/1.0.13/Throne-1.0.13-linux-amd64.zip",
	}
)

func main() {
	deploy := flag.Bool("deploy", false, "Build and deploy to GitHub Pages")
	buildOnly := flag.Bool("build-only", false, "Build without deploying")
	debug := flag.Bool("debug", false, "Debug mode")
	port := flag.String("port", "5000", "Port to listen on")
	host := flag.String("host", "127.0.0.1", "Host to listen on")
	flag.Parse()

	if *deploy || *buildOnly {
		buildSite()
		if *deploy {
			if !deployToGithub() {
				os.Exit(1)
			}
		}
		fmt.Println("Build complete: ./" + distDir)
		return
	}

	fmt.Printf("[START] Web server on http://%s:%s (Debug: %v)\n", *host, *port, *debug)
	// Initialize assets
	fmt.Println("Downloading external assets if needed...")
	downloadExternalAssets()

	// HTTP Server mode
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			// Handle SEO files at root
			switch r.URL.Path {
			case "/robots.txt":
				w.Header().Set("Content-Type", "text/plain")
				w.Write([]byte("User-agent: *\nAllow: /\nSitemap: " + getSiteUrl() + "sitemap.xml"))
				return
			case "/sitemap.xml":
				w.Header().Set("Content-Type", "application/xml")
				lastmod := time.Now().UTC().Format("2006-01-02")
				w.Write([]byte(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>` + getSiteUrl() + `</loc><lastmod>` + lastmod + `</lastmod></url></urlset>`))
				return
			case "/manifest.webmanifest":
				http.ServeFile(w, r, "app/static/manifest.webmanifest")
				return
			case "/sw.js":
				http.ServeFile(w, r, "app/static/sw.js")
				return
			case "/favicon.ico":
				http.ServeFile(w, r, "app/static/images/favicon.png")
				return
			case "/LICENSE":
				http.ServeFile(w, r, "app/static/LICENSE")
				return
			}
			
			// Handle API routes
			if strings.HasPrefix(r.URL.Path, "/api/download-links") {
				w.Header().Set("Content-Type", "application/json")
				b, _ := json.Marshal(fetchDownloadLinks())
				w.Write(b)
				return
			}
			if strings.HasPrefix(r.URL.Path, "/api/vc-runtime-link") {
				w.Header().Set("Content-Type", "application/json")
				vcLink := fetchVcRuntimeLink()
				if vcLink == "" {
					vcLink = vcRuntimeFallback
				}
				b, _ := json.Marshal(map[string]string{"link": vcLink})
				w.Write(b)
				return
			}
			if strings.HasPrefix(r.URL.Path, "/api/github-stats") {
				os.MkdirAll(filepath.Join("dist", "api"), 0755)
				fetchGithubStats(filepath.Join("dist", "api"))
				w.Header().Set("Content-Type", "application/json")
				http.ServeFile(w, r, filepath.Join("dist", "api", "github-stats.json"))
				return
			}

			// serve static
			http.FileServer(http.Dir("app")).ServeHTTP(w, r)
			return
		}
		
		tpl, err := pongo2.FromFile("app/templates/index.html")
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		
	metaTitle := os.Getenv("META_TITLE")
	if metaTitle == "" {
		metaTitle = "Goida VPN Configs - Автоматические VPN-конфиги"
	}
	metaDesc := os.Getenv("META_DESCRIPTION")
	if metaDesc == "" {
		metaDesc = "Автоматические VPN-конфиги для V2Ray, VLESS, Hysteria, Trojan, VMess, Reality и Shadowsocks. Обновление каждые 9 минут, удобные ссылки и QR-коды."
	}
	metaKeywords := os.Getenv("META_KEYWORDS")
	if metaKeywords == "" {
		metaKeywords = "vpn, vless, v2ray, shadowsocks, hysteria, trojan, vmess, reality, vpn configs, free vpn, goida vpn, обход блокировок, автоматичні vpn конфіги, обхід блокувань"
	}
	
	downloadLinks := fetchDownloadLinks()
	vcLink := fetchVcRuntimeLink()
	if vcLink == "" {
		vcLink = vcRuntimeFallback
	}
	ctx := pongo2.Context{
		"configs":          getVpnConfigs(),
		"analytics_ids":    getAnalyticsIds(),
		"site_url":         getSiteUrl(),
		"canonical_url":    getSiteUrl(),
		"download_links":   downloadLinks,
		"vc_runtime_link":  vcLink,
		"meta_title":       metaTitle,
		"meta_description": metaDesc,
		"meta_keywords":    metaKeywords,
		"site_name":        "Goida VPN Configs",
		"og_image":         os.Getenv("OG_IMAGE_URL"),
	}
		out, err := tpl.Execute(ctx)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Write([]byte(out))
	})

	log.Fatal(http.ListenAndServe(*host+":"+*port, nil))
}

func getSiteUrl() string {
	url := os.Getenv("SITE_URL")
	if url == "" {
		return "https://avencores.github.io/goida-vpn-site/"
	}
	if !strings.HasSuffix(url, "/") {
		url += "/"
	}
	return url
}

func getAnalyticsIds() map[string]string {
	return map[string]string{
		"ga_id":                   os.Getenv("GA_ID"),
		"ym_id":                   os.Getenv("YM_ID"),
		"yandex_autoplacement_id": os.Getenv("YANDEX_AUTOPLACEMENT_ID"),
	}
}

func getVpnConfigs() []map[string]interface{} {
	baseUrl := "https://github.com/AvenCores/goida-vpn-configs/raw/refs/heads/main/githubmirror/"
	
	configs := []map[string]interface{}{}
	recIds := map[int]bool{1:true, 6:true, 22:true, 23:true, 24:true, 25:true}
	
	// Basic parsing
	updateInfo := parseUpdateTable()
	
	for i := 1; i <= 26; i++ {
		cfg := map[string]interface{}{
			"id":             i,
			"name":           fmt.Sprintf("Config %d.txt", i),
			"url":            fmt.Sprintf("%s%d.txt", baseUrl, i),
			"is_recommended": recIds[i],
			"is_sni":         i == 26,
			"qr_link":        fmt.Sprintf("https://github.com/AvenCores/goida-vpn-configs/blob/main/qr-codes/%d.png", i),
			"sources":        sourcesMap[i],
		}
		if info, ok := updateInfo[i]; ok {
			cfg["last_update"] = info
		}
		configs = append(configs, cfg)
	}
	return configs
}

func parseUpdateTable() map[int]map[string]string {
	res, err := http.Get("https://raw.githubusercontent.com/AvenCores/goida-vpn-configs/refs/heads/main/README.md")
	if err != nil {
		return nil
	}
	defer res.Body.Close()
	b, _ := io.ReadAll(res.Body)
	
	re := regexp.MustCompile(`\|\s*(\d+)\s*\|[^|]*\|[^|]*\|\s*(\d{2}:\d{2})\s*\|\s*(\d{2}\.\d{2}\.\d{4})\s*\|`)
	matches := re.FindAllStringSubmatch(string(b), -1)
	
	info := make(map[int]map[string]string)
	for _, m := range matches {
		id, _ := strconv.Atoi(m[1])
		info[id] = map[string]string{
			"time":         m[2],
			"date":         m[3],
			"datetime_str": m[3] + " " + m[2],
		}
	}
	return info
}

func buildSite() {
	fmt.Println("Building site...")
	downloadExternalAssets()
	
	os.RemoveAll(distDir)
	os.MkdirAll(filepath.Join(distDir, "api"), 0755)
	
	// copy static
	cmd := exec.Command("cp", "-r", "app/static", filepath.Join(distDir, "static"))
	if os.PathSeparator == '\\' {
		cmd = exec.Command("powershell", "-c", "Copy-Item -Recurse app/static "+distDir+"/static")
	}
	cmd.Run()
	
	pwaFiles := []string{"manifest.webmanifest", "sw.js"}
	for _, f := range pwaFiles {
		src := filepath.Join("app", "static", f)
		dst := filepath.Join(distDir, f)
		b, err := os.ReadFile(src)
		if err == nil {
			os.WriteFile(dst, b, 0644)
		}
	}
	
	metaTitle := os.Getenv("META_TITLE")
	if metaTitle == "" {
		metaTitle = "Goida VPN Configs - Автоматические VPN-конфиги"
	}
	metaDesc := os.Getenv("META_DESCRIPTION")
	if metaDesc == "" {
		metaDesc = "Автоматические VPN-конфиги для V2Ray, VLESS, Hysteria, Trojan, VMess, Reality и Shadowsocks. Обновление каждые 9 минут, удобные ссылки и QR-коды."
	}
	metaKeywords := os.Getenv("META_KEYWORDS")
	if metaKeywords == "" {
		metaKeywords = "vpn, vless, v2ray, shadowsocks, hysteria, trojan, vmess, reality, vpn configs, free vpn, goida vpn, обход блокировок, автоматичні vpn конфіги, обхід блокувань"
	}
	
	downloadLinks := fetchDownloadLinks()
	vcLink := fetchVcRuntimeLink()
	if vcLink == "" {
		vcLink = vcRuntimeFallback
	}
	ctx := pongo2.Context{
		"configs":          getVpnConfigs(),
		"analytics_ids":    getAnalyticsIds(),
		"site_url":         getSiteUrl(),
		"canonical_url":    getSiteUrl(),
		"download_links":   downloadLinks,
		"vc_runtime_link":  vcLink,
		"meta_title":       metaTitle,
		"meta_description": metaDesc,
		"meta_keywords":    metaKeywords,
		"site_name":        "Goida VPN Configs",
		"og_image":         os.Getenv("OG_IMAGE_URL"),
	}
	
	tpl, err := pongo2.FromFile("app/templates/index.html")
	if err == nil {
		out, execErr := tpl.Execute(ctx)
		if execErr != nil {
			fmt.Println("Error executing template:", execErr)
		}
		os.WriteFile(filepath.Join(distDir, "index.html"), []byte(out), 0644)
	} else {
		fmt.Println("Error templating:", err)
	}
	
	// JSON APIs
	dlBytes, _ := json.Marshal(downloadLinks)
	os.WriteFile(filepath.Join(distDir, "api", "download-links.json"), dlBytes, 0644)
	
	vcBytes, _ := json.Marshal(map[string]string{"link": vcLink})
	os.WriteFile(filepath.Join(distDir, "api", "vc-runtime-link.json"), vcBytes, 0644)
	
	fetchGithubStats(filepath.Join(distDir, "api"))
	
	os.WriteFile(filepath.Join(distDir, ".nojekyll"), []byte(""), 0644)
	os.WriteFile(filepath.Join(distDir, "robots.txt"), []byte("User-agent: *\nAllow: /\nSitemap: "+getSiteUrl()+"sitemap.xml"), 0644)
	lastmod := time.Now().UTC().Format("2006-01-02")
	os.WriteFile(filepath.Join(distDir, "sitemap.xml"), []byte(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>`+getSiteUrl()+`</loc><lastmod>`+lastmod+`</lastmod></url></urlset>`), 0644)
}

func deployToGithub() bool {
	token := os.Getenv("MY_TOKEN")
	if token == "" {
		token = os.Getenv("GITHUB_TOKEN")
	}
	if token == "" {
		fmt.Println("ERROR: no deployment token")
		return false
	}
	
	fmt.Println("Deploying to", branch)
	
	// Prepare basic auth header
	authStr := "x-access-token:" + token
	authEncoded := base64.StdEncoding.EncodeToString([]byte(authStr))
	authHeader := "AUTHORIZATION: basic " + authEncoded
	
	cmds := [][]string{
		{"git", "init"},
		{"git", "config", "user.name", "Auto Builder"},
		{"git", "config", "user.email", "actions@github.com"},
		{"git", "add", "."},
		{"git", "commit", "-m", "Deploy site update"},
		{"git", "branch", "-M", branch},
		{"git", "remote", "add", "origin", targetRepo},
		{"git", "-c", "http.https://github.com/.extraheader=" + authHeader, "push", "-f", "origin", branch},
	}
	
	for _, c := range cmds {
		cmd := exec.Command(c[0], c[1:]...)
		cmd.Dir = distDir
		if err := cmd.Run(); err != nil {
			fmt.Println("Git command failed:", c)
			return false
		}
	}
	return true
}

func downloadExternalAssets() {
	downloadBadges()
	assets := map[string]string{
		"https://cdn.jsdelivr.net/npm/@alpinejs/collapse@3.x.x/dist/cdn.min.js":        "app/static/js/alpine-collapse.min.js",
		"https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js":                  "app/static/js/alpine.min.js",
		"https://cdn.tailwindcss.com":                                                  "app/static/js/tailwind.min.js",
		"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css":      "app/static/css/all.min.css",
		"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/webfonts/fa-solid-900.woff2": "app/static/webfonts/fa-solid-900.woff2",
		"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/webfonts/fa-regular-400.woff2": "app/static/webfonts/fa-regular-400.woff2",
		"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/webfonts/fa-brands-400.woff2": "app/static/webfonts/fa-brands-400.woff2",
		"https://flagcdn.com/w20/ru.png": "app/static/images/flags/ru.png",
		"https://flagcdn.com/w40/ru.png": "app/static/images/flags/ru@2x.png",
		"https://flagcdn.com/w20/gb.png": "app/static/images/flags/gb.png",
		"https://flagcdn.com/w40/gb.png": "app/static/images/flags/gb@2x.png",
		"https://flagcdn.com/w20/de.png": "app/static/images/flags/de.png",
		"https://flagcdn.com/w40/de.png": "app/static/images/flags/de@2x.png",
		"https://flagcdn.com/w20/ua.png": "app/static/images/flags/ua.png",
		"https://flagcdn.com/w40/ua.png": "app/static/images/flags/ua@2x.png",
		"https://flagcdn.com/w20/by.png": "app/static/images/flags/by.png",
		"https://flagcdn.com/w40/by.png": "app/static/images/flags/by@2x.png",
		"https://flagcdn.com/w20/kz.png": "app/static/images/flags/kz.png",
		"https://flagcdn.com/w40/kz.png": "app/static/images/flags/kz@2x.png",
		"https://flagcdn.com/w20/fr.png": "app/static/images/flags/fr.png",
		"https://flagcdn.com/w40/fr.png": "app/static/images/flags/fr@2x.png",
		"https://flagcdn.com/w20/pl.png": "app/static/images/flags/pl.png",
		"https://flagcdn.com/w40/pl.png": "app/static/images/flags/pl@2x.png",
	}

	for url, path := range assets {
		if _, err := os.Stat(path); os.IsNotExist(err) {
			os.MkdirAll(filepath.Dir(path), 0755)
			fmt.Println("Downloading", url, "to", path)
			resp, err := http.Get(url)
			if err == nil {
				defer resp.Body.Close()
				f, _ := os.Create(path)
				io.Copy(f, resp.Body)
				f.Close()
			} else {
				fmt.Println("Failed to download", url, err)
			}
		}
	}
}

