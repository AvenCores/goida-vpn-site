document.addEventListener('DOMContentLoaded', () => {
    document.body.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;

        // Если ссылка имеет атрибут data-no-confirm, игнорируем
        if (link.hasAttribute('data-no-confirm')) return;

        const href = link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('javascript:')) return;

        // Если ссылка помечена как загрузочная, открываем модалку скачивания ПЕРЕД проверкой на внешнюю ссылку
        if (link.hasAttribute('data-is-download')) {
            e.preventDefault();
            window.dispatchEvent(new CustomEvent('open-download-modal', { detail: { url: href } }));
            return;
        }

        // Проверяем, является ли ссылка внешней
        let isExternal = false;
        try {
            const url = new URL(href, window.location.href);
            if (url.hostname !== window.location.hostname) {
                isExternal = true;
            }
        } catch (err) {
            // Некорректный URL или относительный путь -> внутренний
            isExternal = false;
        }

        if (isExternal) {
            e.preventDefault();
            window.dispatchEvent(new CustomEvent('open-exit-modal', { detail: { url: href } }));
        }
    });
});