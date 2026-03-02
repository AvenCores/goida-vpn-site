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

// Обновляем ссылки при загрузке страницы
document.addEventListener('DOMContentLoaded', updateDownloadLinks);

// Обновляем ссылки каждый час
setInterval(updateDownloadLinks, 60 * 60 * 1000);
