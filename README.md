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

- **🌍 Мультиязычность (i18n)**: Полная поддержка 8 языков (Русский, English, Français, Polski, Українська, Беларуская, Deutsch, Казахский) с сохранением выбора пользователя.
- **📱 PWA Ready**: Сайт является прогрессивным веб-приложением. Его можно установить на смартфон или ПК, он поддерживает кэширование и работает в офлайн-режиме быстрее.
- **🔄 Динамические конфигурации**: Данные о конфигах и времени их обновления подтягиваются в реальном времени из внешнего репозитория.
- **⚡ Автоматизация ссылок**: Автоматический поиск и обновление прямых ссылок на VPN-клиенты (v2rayNG, Throne) и системные компоненты (VC Runtimes) на базе GitHub API и comss.ru.
- **🌗 Поддержка тем**: Полноценная темная и светлая темы с автоматическим определением предпочтений системы.
- **🔍 SEO Оптимизация**: Автоматическая генерация `sitemap.xml` и `robots.txt`, правильные мета-теги и канонические ссылки.
- **🛡️ Безопасность**: Модальные окна подтверждения для внешних ссылок и загрузок файлов.

---

## 🏗️ Структура проекта

Кодовая база спроектирована по канонам разработки на Flask с использованием фабрики приложений (`Application Factory`), разделением роутинга на синие страницы (`Blueprints`) и инкапсуляцией логики в слой сервисов (`Services`).

```text
goida-vpn-site/
├── app/                              # Основной пакет веб-приложения
│   ├── __init__.py                  # Фабрика приложений (create_app), регистрация Blueprints
│   ├── config.py                    # Глобальные настройки, SEO-дефолты, fallback-ссылки и источники
│   ├── utils.py                     # Утилиты генерации robots.txt, sitemap.xml и нормализации URL
│   ├── routes/                      # Контроллеры и маршрутизация (Blueprints)
│   │   ├── views.py                 # Рендеринг основного UI (главная страница `/`)
│   │   ├── api.py                   # API эндпоинты с кэшированием (скачивания, статистика, VC++)
│   │   └── seo.py                   # SEO и PWA-файлы (sitemap, robots, sw.js, manifest)
│   ├── services/                    # Бизнес-логика и сбор данных из внешних источников
│   │   ├── vpn.py                   # Скрапинг VPN-конфигураций и времени их обновлений
│   │   ├── github.py                # Работа с GitHub API (загрузка бейджей, ссылки, статистика)
│   │   └── vc_runtime.py            # Парсинг VC++ Redistributable с comss.ru
│   ├── templates/                   # HTML-шаблоны (Jinja2)
│   │   ├── base.html                # Основной лэйаут с Alpine.js (модалки, темы, меню)
│   │   ├── index.html               # Точка сборки главной страницы
│   │   └── components/              # Модульные компоненты UI (header, footer, hero, tabs, bypass, video, instructions)
│   └── static/                      # Статические ресурсы фронтенда
│       ├── css/                     # Tailwind CSS стили (tailwind.css, tailwind.input.css)
│       ├── js/                      # Скрипты (i18n.js, statistics.js, update-download-links.js, link-confirmation.js)
│       ├── i18n/                    # Переводы (translations.json на 5 языках)
│       ├── images/                  # Картинки, фавиконы, QR-коды и папка badges/
│       ├── manifest.webmanifest     # Манифест PWA-приложения
│       └── sw.js                    # Сервис-воркер PWA-кэширования
├── dist/                             # Папка компиляции статического сайта (генерируется сборщиком)
├── build.py                          # Скрипт сборки статического HTML/JSON сайта и деплоя в Pages
├── main.py                           # Точка входа для локального запуска сервера (Flask / Waitress)
├── tailwind.config.js                # Конфигурация сканирования контента Tailwind CSS
└── package.json                      # Зависимости Tailwind (JIT/CLI компилятор)
```

---

## 🛠️ Технологии

- **Backend:** Python 3.10+, Flask, Waitress, Requests, BeautifulSoup4.
- **Frontend:** TailwindCSS (CLI), Alpine.js, FontAwesome, Vanilla JS.
- **Интернационализация:** Собственная JS-реализация на базе JSON-файла переводов.
- **PWA:** Service Workers, Web App Manifest.
- **CI/CD:** GitHub Actions + `build.py` для автоматического деплоя в ветку `gh-pages`.

---

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

2. **Настройте виртуальное окружение**:
```bash
python -m venv .env
# Windows:
.env\Scripts\activate
# Linux/macOS:
source .env/bin/activate
# Установите зависимости:
pip install -r requirements.txt
```

3. **Сборка стилей (опционально)**:
```bash
npm install
npm run build:css
```

---

## 📝 Разработка и обслуживание

### Локальный запуск
* **Режим отладки (со всеми заглушками API)**:
  ```bash
  python main.py --debug
  ```
  *Сайт будет доступен на `http://localhost:5000` с включенным автоперезагрузчиком при изменении кода.*
* **Режим продакшена (через Waitress)**:
  ```bash
  python main.py
  ```

### Сборка статической версии
* **Простая локальная компиляция** (по умолчанию):
  ```bash
  python build.py
  ```
  или с явным указанием флага:
  ```bash
  python build.py --build-only
  ```
  *Результат компилируется в папку `dist/`.*
* **Компиляция и деплой на GitHub Pages**:
  ```bash
  python build.py --deploy
  ```
  *(Требуется наличие `MY_TOKEN` или `GITHUB_TOKEN` в переменных окружения).*

### Обслуживание контента
* **Обновление конфигураций VPN**: Все конфигурации подтягиваются динамически. Любые изменения вносите напрямую в исходный репозиторий `AvenCores/goida-vpn-configs`.
* **Редактирование локализации**: Для изменения текстов, добавления новых строк или исправления перевода редактируйте файл перевода: `app/static/i18n/translations.json`.
* **Изменение дизайна и стилей**: После изменения шаблонов или файла `app/static/css/tailwind.input.css` запустите сборку стилей через `npm run build:css`.

---

## 🚀 Автоматизация (GitHub Actions)

Сайт полностью автономен и обновляется через CI/CD:
1. **По расписанию (каждый час)**: Запускается GitHub Action, который через `build.py` стягивает свежие ссылки, собирает актуальную статистику репозитория конфигураций и компилирует свежую статическую версию.
2. **При пуше изменений**: Автоматически запускается процесс деплоя сгенерированного билда в ветку `gh-pages`.

## 📜 Лицензия
Лицензия GPL-3.0 — подробности в файле [LICENSE](LICENSE).

---

# 💰 Поддержать автора
+ **SBER**: `2202 2050 1464 4675`
