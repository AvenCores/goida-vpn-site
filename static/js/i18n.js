/**
 * I18n модуль для поддержки мультиязычности (RU/EN)
 * Загружает переводы из static/i18n/translations.json и применяет их к элементам с data-i18n
 */
(function() {
    'use strict';

    let translations = {};
    let currentLang = 'ru';

    // Загрузка переводов
    let _translationsReady = false;

    // Хранилище оригинальных значений (сохраняем ДО применения переводов)
    let _originalValues = new Map();

    async function loadTranslations() {
        try {
            const response = await fetch('static/i18n/translations.json');
            if (!response.ok) {
                console.error('✗ Ошибка загрузки файла переводов');
                return false;
            }
            translations = await response.json();
            _translationsReady = true;
            return true;
        } catch (error) {
            console.error('✗ Ошибка при загрузке переводов:', error);
            return false;
        }
    }

    // Сохранить оригинальные значения всех элементов с data-i18n
    function saveOriginals() {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (!_originalValues.has(key)) {
                _originalValues.set(key, el.innerHTML);
            }
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (!_originalValues.has(key)) {
                _originalValues.set('placeholder:' + key, el.placeholder);
            }
        });
        document.querySelectorAll('[data-i18n-title]').forEach(el => {
            const key = el.getAttribute('data-i18n-title');
            if (!_originalValues.has(key)) {
                _originalValues.set('title:' + key, el.title);
            }
        });
        document.querySelectorAll('[data-i18n-alt]').forEach(el => {
            const key = el.getAttribute('data-i18n-alt');
            if (!_originalValues.has(key)) {
                _originalValues.set('alt:' + key, el.alt);
            }
        });
    }

    // Получить оригинальное fallback значение
    function _getFallback(key, type) {
        const lookupKey = type ? type + ':' + key : key;
        return _originalValues.get(lookupKey);
    }

    // Получить строку перевода по ключу (поддержка вложенных ключей через точку)
    function t(key, fallback) {
        const keys = key.split('.');

        // Сначала пробуем перевод для текущего языка
        let value = translations[currentLang];
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                value = null;
                break;
            }
        }

        // Если перевод найден — возвращаем
        if (typeof value === 'string' || Array.isArray(value)) {
            return value;
        }

        // Если нет — пробуем русский
        let ru = translations['ru'];
        if (ru) {
            for (const fk of keys) {
                if (ru && typeof ru === 'object' && fk in ru) {
                    ru = ru[fk];
                } else {
                    ru = null;
                    break;
                }
            }
            if (typeof ru === 'string' || Array.isArray(ru)) {
                return ru;
            }
        }

        // Последний fallback — переданный или сохранённый оригинал
        if (fallback !== undefined) {
            return fallback;
        }
        const saved = _getFallback(key);
        if (saved !== undefined) {
            return saved;
        }

        // Для шагов возвращаем массив
        if (key.endsWith('_steps')) return [];

        return key;
    }

    // Дефолтное значение по типу ключа
    function _defaultForType(key) {
        if (key.endsWith('_steps')) return [];
        return key;
    }

    // Проверка: переводы загружены?
    function isLoaded() {
        return _translationsReady;
    }

    // Получить текущий язык
    function getLanguage() {
        return currentLang;
    }

    // Установить язык (из localStorage или браузера)
    function initLanguage() {
        const savedLang = localStorage.getItem('lang');
        if (savedLang && (savedLang === 'ru' || savedLang === 'en' || savedLang === 'de')) {
            currentLang = savedLang;
        } else {
            // Определяем язык браузера
            const browserLang = navigator.language || navigator.userLanguage;
            if (browserLang.startsWith('de')) {
                currentLang = 'de';
            } else if (browserLang.startsWith('en')) {
                currentLang = 'en';
            } else {
                currentLang = 'ru';
            }
        }
    }

    // Применить переводы ко всем элементам с data-i18n + обновить Alpine i18nReady
    function applyTranslations() {
        // Установить i18nReady = true в Alpine (реактивное переключение x-if)
        // Пробуем несколько раз на случай если Alpine ещё не инициализирован
        const enableI18nReady = () => {
            try {
                const comps = document.querySelectorAll('[x-data]');
                if (comps.length > 0) {
                    comps.forEach(comp => {
                        try {
                            const data = Alpine.$data(comp);
                            if (data && 'i18nReady' in data) {
                                data.i18nReady = true;
                            }
                        } catch(e) {}
                    });
                    return true;
                }
            } catch(e) {}
            return false;
        };

        if (!enableI18nReady()) {
            // Если Alpine ещё не готов — пробуем через тик
            if (window.Alpine) {
                Alpine.nextTick(() => enableI18nReady());
            } else {
                // Последний fallback — задержка
                setTimeout(() => enableI18nReady(), 100);
            }
        }

        // Элементы с data-i18n — fallback берётся из сохранённых оригиналов
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            const translated = t(key);
            if (translated) {
                el.innerHTML = translated;
            }
        });

        // Элементы с data-i18n-placeholder
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            const translated = t(key);
            if (translated) {
                el.placeholder = translated;
            }
        });

        // Элементы с data-i18n-title
        document.querySelectorAll('[data-i18n-title]').forEach(el => {
            const key = el.getAttribute('data-i18n-title');
            const translated = t(key);
            if (translated) {
                el.title = translated;
            }
        });

        // Элементы с data-i18n-alt
        document.querySelectorAll('[data-i18n-alt]').forEach(el => {
            const key = el.getAttribute('data-i18n-alt');
            const translated = t(key);
            if (translated) {
                el.alt = translated;
            }
        });
    }

    // Переключить язык (циклически)
    function toggleLanguage() {
        const languages = ['ru', 'en', 'de'];
        const currentIndex = languages.indexOf(currentLang);
        currentLang = languages[(currentIndex + 1) % languages.length];
        localStorage.setItem('lang', currentLang);
        applyTranslations();
        updateHtmlLang();
        // Обновить Alpine.js переменную если есть
        if (window.Alpine) {
            const components = document.querySelectorAll('[x-data]');
            components.forEach(comp => {
                const data = Alpine.$data(comp);
                if (data && 'currentLanguage' in data) {
                    data.currentLanguage = currentLang;
                }
            });
        }
        console.log(`✓ Язык переключён на: ${currentLang}`);
    }

    // Установить конкретный язык
    function setLanguage(lang) {
        if (lang !== 'ru' && lang !== 'en' && lang !== 'de') return;
        if (lang === currentLang) return;
        currentLang = lang;
        localStorage.setItem('lang', currentLang);
        applyTranslations();
        updateHtmlLang();
        // Обновить Alpine.js переменную если есть
        if (window.Alpine) {
            const components = document.querySelectorAll('[x-data]');
            components.forEach(comp => {
                const data = Alpine.$data(comp);
                if (data && 'currentLanguage' in data) {
                    data.currentLanguage = currentLang;
                }
            });
        }
        console.log(`✓ Язык установлен на: ${currentLang}`);
    }

    // Обновить атрибут lang у <html>
    function updateHtmlLang() {
        document.documentElement.lang = currentLang;
    }

    // Инициализация
    async function init() {
        // 1. Сначала сохраняем оригинальные значения (русский текст из HTML)
        saveOriginals();

        // 2. Определяем язык
        initLanguage();

        // 3. Загружаем переводы
        const loaded = await loadTranslations();

        // 4. Применяем переводы для выбранного языка
        if (loaded) {
            applyTranslations();
            updateHtmlLang();
        }
    }

    // Экспорт глобальных функций
    window.i18n = {
        t,
        getLanguage,
        isLoaded,
        toggleLanguage,
        setLanguage,
        applyTranslations,
        init
    };

    // Запуск при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
