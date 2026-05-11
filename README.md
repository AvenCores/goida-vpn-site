<div align="center">
    <a href="https://www.youtube.com/@avencores/" target="_blank">
      <img src="https://github.com/user-attachments/assets/338bcd74-e3c3-4700-87ab-7985058bd17e" alt="YouTube" height="40">
    </a>
    <a href="https://t.me/avencoresyt" target="_blank">
      <img src="https://github.com/user-attachments/assets/939f8beb-a49a-48cf-89b9-d610ee5c4b26" alt="Telegram" height="40">
    </a>
    <a href="https://vk.ru/avencoresreuploads" target="_blank">
      <img src="https://github.com/user-attachments/assets/dc109dda-9045-4a06-95a5-3399f0e21dc4" alt="VK" height="40">
    </a>
    <a href="https://dzen.ru/avencores" target="_blank">
      <img src="https://github.com/user-attachments/assets/bd55f5cf-963c-4eb8-9029-7b80c8c11411" alt="Dzen" height="40">
    </a>
</div>

## 📝 Описание проекта

[![GPL-3.0 License](https://img.shields.io/badge/License-GPL--3.0-blue?style=for-the-badge)](./LICENSE)
[![Website](https://img.shields.io/badge/Website-Goida%20VPN-207e5c?style=for-the-badge&logo=firefox)](https://avencores.github.io/goida-vpn-site/)
[![GitHub stars](https://img.shields.io/github/stars/AvenCores/goida-vpn-site?style=for-the-badge)](https://github.com/AvenCores/goida-vpn-site/stargazers)
![GitHub forks](https://img.shields.io/github/forks/AvenCores/goida-vpn-site?style=for-the-badge)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/AvenCores/goida-vpn-site?style=for-the-badge)](https://github.com/AvenCores/goida-vpn-site/pulls)
[![GitHub issues](https://img.shields.io/github/issues/AvenCores/goida-vpn-site?style=for-the-badge)](https://github.com/AvenCores/goida-vpn-site/issues)

Это современный веб-интерфейс для проекта [**goida-vpn-configs**](https://github.com/AvenCores/goida-vpn-configs/). 
Сайт автоматически парсит актуальные конфигурации (`V2Ray` / `VLESS` / `Hysteria` / `Trojan` / `VMess` / `Reality` / `Shadowsocks`), генерирует удобные ссылки для копирования, QR-коды и предоставляет исчерпывающие инструкции по настройке.

<a href="https://avencores.github.io/goida-vpn-site/">
  <img alt="Preview" src="https://github.com/user-attachments/assets/80f69696-5eb5-44fa-94bf-1fe50303f683" />
</a>

## ✨ Ключевые особенности
![maxresdefault](https://i.ibb.co/xKkZ7gyv/chrome-mi9o-Yu-I3-Cd.png)

- **🌍 Мультиязычность (i18n)**: Полная поддержка 5 языков (Русский, English, Українська, Беларуская, Deutsch) с сохранением выбора пользователя.
- **📱 PWA Ready**: Сайт является прогрессивным веб-приложением. Его можно установить на смартфон или ПК, он поддерживает кэширование и работает быстрее.
- **🔄 Динамические конфигурации**: Данные о конфигах и времени их обновления подтягиваются в реальном времени из внешнего репозитория.
- **⚡ Автоматизация ссылок**: Автоматический поиск и обновление прямых ссылок на VPN-клиенты (v2rayNG, Throne) и системные компоненты (VC Runtimes).
- **🌗 Поддержка тем**: Полноценная темная и светлая темы с автоматическим определением предпочтений системы.
- **🔍 SEO Оптимизация**: Автоматическая генерация `sitemap.xml` и `robots.txt`, правильные мета-теги и канонические ссылки.
- **🛡️ Безопасность**: Модальные окна подтверждения для внешних ссылок и загрузок файлов.

## 🏗️ Структура проекта

- `main.py`: Flask-сервер с логикой кэширования, API-эндпоинтами и парсингом внешних ресурсов (GitHub API, comss.ru).
- `services.py`: Ядро логики по обработке VPN-конфигураций и метаданных.
- `build.py`: Скрипт сборки статической версии сайта для GitHub Pages.
- `static/js/i18n.js`: Клиентская система переводов на базе JSON.
- `sw.js` & `manifest.webmanifest`: Файлы конфигурации PWA.
- `templates/components/`: Модульные UI-блоки (шапка, подвал, табы, инструкции и т.д.).
- `notes.md`: Техническая документация для разработчиков.

## 🛠️ Технологии

- **Backend:** Python 3.10+, Flask, Waitress, Requests, BeautifulSoup4.
- **Frontend:** TailwindCSS (CLI), Alpine.js, FontAwesome, Vanilla JS.
- **Интернационализация:** Custom i18n logic (JSON-based).
- **PWA:** Service Workers, Web App Manifest.
- **CI/CD:** GitHub Actions + Python Build Script.

## ⚙️ Установка и запуск

### Предварительные требования:
- Python 3.10+
- Node.js (только если планируете изменять CSS)

### Шаги установки:

1. **Клонируйте репозиторий**:
```bash
git clone https://github.com/AvenCores/goida-vpn-site.git
cd goida-vpn-site
```

2. **Настройте окружение**:
```bash
python -m venv .env
# Windows:
.env\Scripts\activate
# Linux/macOS:
source .env/bin/activate
pip install -r requirements.txt
```

3. **Сборка стилей (опционально)**:
```bash
npm install
npm run build:css
```

### Использование:

- **Локальный сервер**: `python main.py` (доступно на `http://localhost:5000`).
- **Режим отладки**: `python main.py --debug` (автоперезагрузка, API-заглушки).
- **Сборка статики**: `python build.py` (результат в папке `dist/`).

---

## 🚀 Автоматизация (GitHub Actions)

Сайт обновляется автоматически:
1. **По расписанию**: Каждый час `build.py` обновляет данные о конфигах и статистику.
2. **При пуше**: Деплой новой версии в ветку `gh-pages`.

## 📜 Лицензия
Лицензия GPL-3.0 — подробности в файле [LICENSE](LICENSE).

---
# 💰 Поддержать автора
+ **SBER**: `2202 2050 1464 4675`
