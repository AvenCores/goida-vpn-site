// Функция для получения ссылок на скачивание с нашего API
async function updateDownloadLinks() {
    try {
        const response = await fetch('api/download-links.json');

        if (!response.ok) {
            console.warn('✗ API сервер недоступен, используются локальные ссылки');
            return;
        }

        const links = await response.json();

        // Обновляем ссылки на странице
        Object.entries(links).forEach(([linkType, url]) => {
            document.querySelectorAll(`[data-link-type="${linkType}"]`).forEach(el => {
                el.href = url;
            });
        });

        console.log('✓ Ссылки на скачивание обновлены');
    } catch (error) {
        console.error('✗ Ошибка при обновлении ссылок:', error);
    }
}

// Функция для обновления ссылки на Visual C++ Runtimes
async function updateVcRuntimeLink() {
    try {
        const response = await fetch('api/vc-runtime-link.json');

        if (!response.ok) {
            console.warn('✗ API VC Runtime ссылка недоступна, используется локальная ссылка');
            return;
        }

        const data = await response.json();
        const url = data.link;

        if (url) {
            document.querySelectorAll('[data-vc-runtime-link="true"]').forEach(el => {
                el.href = url;
            });
            console.log('✓ Ссылка на Visual C++ Runtimes обновлена:', url);
        }
    } catch (error) {
        console.error('✗ Ошибка при обновлении ссылки на VC Runtime:', error);
    }
}

// Обновляем ссылки при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    updateDownloadLinks();
    updateVcRuntimeLink();
});

// Обновляем ссылки каждый час
setInterval(updateDownloadLinks, 60 * 60 * 1000);
setInterval(updateVcRuntimeLink, 60 * 60 * 1000);
