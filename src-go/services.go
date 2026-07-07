package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"
)

func downloadBadges() {
	badges := map[string]string{
		"python.svg":  "https://img.shields.io/badge/go-%2300ADD8.svg?style=for-the-badge&logo=go&logoColor=white",
		"license.svg": "https://img.shields.io/badge/License-GPL--3.0-blue?style=for-the-badge",
		"stars.svg":   "https://img.shields.io/github/stars/AvenCores/goida-vpn-configs?style=for-the-badge",
		"forks.svg":   "https://img.shields.io/github/forks/AvenCores/goida-vpn-configs?style=for-the-badge",
		"prs.svg":     "https://img.shields.io/github/issues-pr/AvenCores/goida-vpn-configs?style=for-the-badge",
		"issues.svg":  "https://img.shields.io/github/issues/AvenCores/goida-vpn-configs?style=for-the-badge",
	}

	badgesDir := filepath.Join("app", "static", "images", "badges")
	os.MkdirAll(badgesDir, 0755)

	for filename, url := range badges {
		path := filepath.Join(badgesDir, filename)
		fmt.Println("Downloading badge", filename)
		resp, err := http.Get(url)
		if err == nil {
			defer resp.Body.Close()
			f, _ := os.Create(path)
			io.Copy(f, resp.Body)
			f.Close()
		}
	}
}

type GHAsset struct {
	Name               string `json:"name"`
	BrowserDownloadUrl string `json:"browser_download_url"`
}

func selectV2rayngApk(assets []GHAsset) *GHAsset {
	// 1. Try universal.apk (excluding fdroid / sig)
	for i := range assets {
		nameLower := strings.ToLower(assets[i].Name)
		if strings.HasSuffix(nameLower, ".apk") &&
			strings.Contains(nameLower, "universal") &&
			!strings.Contains(nameLower, "f-droid") &&
			!strings.Contains(nameLower, "fdroid") {
			return &assets[i]
		}
	}
	// 2. Try universal (any format except .sig)
	for i := range assets {
		nameLower := strings.ToLower(assets[i].Name)
		if strings.Contains(nameLower, "universal") &&
			!strings.HasSuffix(nameLower, ".sig") {
			return &assets[i]
		}
	}
	// 3. Try arm64-v8a.apk (excluding fdroid / sig) - most common standard architecture
	for i := range assets {
		nameLower := strings.ToLower(assets[i].Name)
		if strings.HasSuffix(nameLower, ".apk") &&
			strings.Contains(nameLower, "arm64-v8a") &&
			!strings.Contains(nameLower, "f-droid") &&
			!strings.Contains(nameLower, "fdroid") {
			return &assets[i]
		}
	}
	// 4. Try any apk (excluding fdroid / sig)
	for i := range assets {
		nameLower := strings.ToLower(assets[i].Name)
		if strings.HasSuffix(nameLower, ".apk") &&
			!strings.Contains(nameLower, "f-droid") &&
			!strings.Contains(nameLower, "fdroid") {
			return &assets[i]
		}
	}
	return nil
}

func fetchDownloadLinks() map[string]string {
	links := make(map[string]string)
	for k, v := range fallbackLinks {
		links[k] = v
	}

	// v2rayNG
	resp, err := http.Get("https://api.github.com/repos/2dust/v2rayNG/releases/latest")
	if err == nil {
		defer resp.Body.Close()
		var data struct {
			Assets []GHAsset `json:"assets"`
		}
		if json.NewDecoder(resp.Body).Decode(&data) == nil {
			if apk := selectV2rayngApk(data.Assets); apk != nil {
				links["v2rayng-apk"] = apk.BrowserDownloadUrl
			}
		}
	}

	// Throne
	resp2, err := http.Get("https://api.github.com/repos/throneproj/Throne/releases/latest")
	if err == nil {
		defer resp2.Body.Close()
		var data struct {
			Assets []struct {
				Name               string `json:"name"`
				BrowserDownloadUrl string `json:"browser_download_url"`
			} `json:"assets"`
		}
		if json.NewDecoder(resp2.Body).Decode(&data) == nil {
			for _, a := range data.Assets {
				if strings.Contains(a.Name, "windows64") && !strings.Contains(a.Name, "legacy") {
					links["throne-win10"] = a.BrowserDownloadUrl
				}
				if strings.Contains(a.Name, "windowslegacy64") {
					links["throne-win7"] = a.BrowserDownloadUrl
				}
				if strings.Contains(a.Name, "linux-amd64") {
					links["throne-linux"] = a.BrowserDownloadUrl
				}
			}
		}
	}

	return links
}

func fetchGithubStats(apiPath string) {
	token := os.Getenv("MY_TOKEN")
	if token == "" {
		token = os.Getenv("GITHUB_TOKEN")
	}

	stats := map[string]interface{}{
		"pushed_at":        nil,
		"stargazers_count": 0,
		"clones":           map[string]int{"count": 0, "uniques": 0},
		"views":            map[string]int{"count": 0, "uniques": 0},
		"referrers":        []interface{}{},
		"popular_content":  []interface{}{},
		"error":            nil,
	}

	if token == "" {
		stats["error"] = "Token not configured"
		saveJson(filepath.Join(apiPath, "github-stats.json"), stats)
		return
	}

	req, _ := http.NewRequest("GET", "https://api.github.com/repos/AvenCores/goida-vpn-configs", nil)
	req.Header.Set("Authorization", "token "+token)
	req.Header.Set("Accept", "application/vnd.github.v3+json")

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err == nil {
		defer resp.Body.Close()
		var repoData map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&repoData)
		stats["pushed_at"] = repoData["pushed_at"]
		stats["stargazers_count"] = repoData["stargazers_count"]
	} else {
		stats["error"] = err.Error()
		saveJson(filepath.Join(apiPath, "github-stats.json"), stats)
		return
	}

	endpoints := map[string]string{
		"clones":            "clones",
		"views":             "views",
		"popular/referrers": "referrers",
		"popular/paths":     "popular_content",
	}

	for endpoint, field := range endpoints {
		req, _ := http.NewRequest("GET", "https://api.github.com/repos/AvenCores/goida-vpn-configs/traffic/"+endpoint, nil)
		req.Header.Set("Authorization", "token "+token)
		req.Header.Set("Accept", "application/vnd.github.v3+json")
		resp, err := client.Do(req)
		if err == nil && resp.StatusCode == 200 {
			defer resp.Body.Close()
			var data interface{}
			err = json.NewDecoder(resp.Body).Decode(&data)
			if err != nil {
				continue
			}
			if field == "clones" || field == "views" {
				if m, ok := data.(map[string]interface{}); ok {
					stats[field] = map[string]interface{}{
						"count":   m["count"],
						"uniques": m["uniques"],
					}
				}
			} else {
				stats[field] = data
			}
		}
	}

	saveJson(filepath.Join(apiPath, "github-stats.json"), stats)
}

func saveJson(path string, data interface{}) {
	b, _ := json.Marshal(data)
	os.WriteFile(path, b, 0644)
}

var sourcesMap = map[int]interface{}{
	1:  "https://github.com/sakha1370/OpenRay",
	2:  "https://github.com/sevcator/5ubscrpt10n",
	3:  "https://github.com/yitong2333/proxy-minging",
	4:  "https://github.com/acymz/AutoVPN",
	5:  "https://github.com/miladtahanian/V2RayCFGDumper",
	6:  "https://github.com/roosterkid/openproxylist",
	7:  "https://github.com/Epodonios/v2ray-configs",
	8:  "https://github.com/ShatakVPN/ConfigForge-V2Ray",
	9:  "https://github.com/mohamadfg-dev/telegram-v2ray-configs-collector",
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
	26: []string{
		"https://github.com/igareck/vpn-configs-for-russia",
		"https://github.com/ByeWhiteLists/ByeWhiteLists2",
		"https://gitverse.ru/cid-uskoritel/cid-white",
		"https://github.com/zieng2/wl",
	},
}

func fetchVcRuntimeLink() string {
	resp, err := http.Get("https://www.comss.ru/download/page.php?id=6271")
	if err != nil {
		return ""
	}
	defer resp.Body.Close()
	b, _ := io.ReadAll(resp.Body)
	html := string(b)

	re := regexp.MustCompile(`https://dl\.comss\.org/download/Visual-C-Runtimes[^"'\s>]+`)
	match := re.FindString(html)
	if match != "" {
		return match
	}
	return ""
}
