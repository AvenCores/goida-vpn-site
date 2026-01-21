<div align="center">
    <a href="https://www.youtube.com/@avencores/" target="_blank">
      <img src="https://github.com/user-attachments/assets/338bcd74-e3c3-4700-87ab-7985058bd17e" alt="YouTube" height="40">
    </a>
    <a href="https://t.me/avencoresyt" target="_blank">
      <img src="https://github.com/user-attachments/assets/939f8beb-a49a-48cf-89b9-d610ee5c4b26" alt="Telegram" height="40">
    </a>
    <a href="https://vk.com/avencoresvk" target="_blank">
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
Сайт автоматически парсит актуальные конфигурации, генерирует удобные ссылки для копирования, QR-коды и предоставляет инструкции по подключению.

Проект поддерживает работу в двух режимах:
1. **Локальный сервер** (Flask + Waitress)
2. **Генератор статического сайта** (для GitHub Pages)

<img width="2560" height="1271" alt="Screenshot" src="https://github.com/user-attachments/assets/4999543b-55c0-45d1-a4ee-32b38fdfca6c" />

## 🛠️ Технологии

- **Backend:** Python, Flask
- **Frontend:** HTML5, TailwindCSS (CDN), Alpine.js (CDN)
- **Server:** Waitress (WSGI)
- **Deployment:** Custom Python script (`build.py`)

## ⚙️ Установка

### Требования:
- Python 3.10+
- pip (менеджер пакетов Python)
- Git

### Шаги установки:

1. **Клонируйте репозиторий**:
```bash
git clone https://github.com/AvenCores/goida-vpn-site.git
cd goida-vpn-site
```

2. **Создайте виртуальное окружение** (рекомендуется):
```bash
python -m venv .env

# Для Windows:
.env\Scripts\activate

# Для macOS/Linux:
source .env/bin/activate
```

3. **Установите зависимости**:
```bash
pip install -r requirements.txt
```

---

## 🚀 Использование

### 1. Локальный запуск (Development)
Запускает веб-сервер на локальной машине. Идеально для разработки и проверки изменений.

```bash
python main.py
```
Приложение будет доступно по адресу: `http://localhost:5000`

### 2. Сборка статического сайта (Build)
Генерирует статические HTML файлы в папку `dist/`. Используется для хостинга без поддержки Python (например, GitHub Pages).

```bash
python build.py
```

### 3. Автоматический деплой (GitHub Actions)
Скрипт `build.py` поддерживает автоматическую отправку собранного сайта в ветку `gh-pages`.
Для этого необходима переменная окружения `MY_TOKEN` с правами на запись в репозиторий.

---
## 💰 Поддержать автора
+ **SBER**: `2202 2050 1464 4675`
