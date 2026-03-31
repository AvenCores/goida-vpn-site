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

Это веб-интерфейс для проекта [**goida-vpn-configs**](https://github.com/AvenCores/goida-vpn-configs/). 
Сайт автоматически парсит актуальные конфигурации (`V2Ray` / `VLESS` / `Hysteria` / `Trojan` / `VMess` / `Reality` / `Shadowsocks`), генерирует удобные ссылки для копирования, QR-коды и предоставляет инструкции по подключению.

<a href="https://avencores.github.io/goida-vpn-site/">
  <img width="1280" height="320" alt="1" src="https://github.com/user-attachments/assets/80f69696-5eb5-44fa-94bf-1fe50303f683" />
</a>

## ✨ Ключевые особенности

<img width="2560" height="1271" alt="chrome_KGIBWwqyCX" src="https://github.com/user-attachments/assets/03d7bfff-039b-4fce-9c8b-586994ebe3d1" />

- **Динамические конфигурации**: Данные подтягиваются напрямую из репозитория `goida-vpn-configs`, включая время последнего обновления.
- **Двойной режим работы**: 
  - **Динамический**: Flask-приложение с API-эндпоинтами и кэшированием.
  - **Статический**: Генерация готового сайта для хостинга на GitHub Pages.
- **Современный UI**: TailwindCSS для стилизации, Alpine.js для интерактивности, поддержка темной и светлой тем.
- **Интеграция с GitHub API**: Автоматическое получение последних версий VPN-клиентов и статистики репозитория.
- **Обход блокировок**: Специальный раздел с инструкциями и конфигом для обхода SNI/CIDR белых списков.
- **Видео-гайды**: Встроенные видео-инструкции для упрощения настройки.
- **Автоматизация**: GitHub Actions каждый час запускает пересборку сайта для актуализации данных.

## 🏗️ Структура проекта

- `main.py`: Основной файл Flask-приложения. Содержит логику API для получения ссылок на ПО и статистики GitHub.
- `services.py`: Логика парсинга конфигураций и данных об обновлениях из внешних источников.
- `build.py`: Скрипт-генератор. Рендерит шаблоны в статические HTML-файлы и подготавливает JSON-файлы для API при статическом деплое.
- `notes.md`: Подробные технические заметки по проекту, структуре и обслуживанию.
- `templates/`: Jinja2 шаблоны, разделенные на модульные компоненты (`hero`, `tabs`, `instructions` и др.).
- `static/`: Стили, клиентские скрипты (`statistics.js`, `update-download-links.js`) и медиа-ресурсы.

## 🛠️ Технологии

- **Backend:** Python 3.10+, Flask, Waitress, Requests.
- **Frontend:** HTML5, TailwindCSS (CDN), Alpine.js (CDN), FontAwesome.
- **CI/CD:** GitHub Actions + Custom Python Build Script.

## ⚙️ Установка и запуск

### Шаги установки:

1. **Клонируйте репозиторий**:
```bash
git clone https://github.com/AvenCores/goida-vpn-site.git
cd goida-vpn-site
```

2. **Создайте виртуальное окружение**:
```bash
python -m venv .env
# Windows:
.env\Scripts\activate
# Linux/macOS:
source .env/bin/activate
```

3. **Установите зависимости**:
```bash
pip install -r requirements.txt
```

### Использование:

- **Локальный сервер**: `python main.py` (доступно на `http://localhost:5000`).
- **Сборка сайта**: `python build.py` (результат в папке `dist/`).

---

## 🚀 Автоматизация (GitHub Actions)

Проект настроен на автоматическое обновление:
1. **По расписанию**: Каждый час выполняется запуск `build.py` для обновления данных о конфигах.
2. **При пуше**: Любое изменение в ветке `main` триггерит деплой новой версии сайта в ветку `gh-pages`.

Для работы деплоя требуется Secret `MY_TOKEN` с правами доступа к репозиторию.

## 📜 Лицензия
Данный проект распространяется под лицензией GPL-3.0 — подробности см. в файле [LICENSE](LICENSE).

---
# 💰 Поддержать автора
+ **SBER**: `2202 2050 1464 4675`
