async function loadGitHubStats() {
    const statsContent = document.getElementById('stats-content');
    
    // Показываем спиннер при каждом открытии
    statsContent.innerHTML = `
        <div class="text-center">
            <i class="fa-solid fa-spinner fa-spin text-3xl text-gray-400"></i>
            <p class="mt-2 text-sm text-gray-500">Загрузка данных...</p>
        </div>`;

    try {
        const repo = 'AvenCores/goida-vpn-configs';
        const response = await fetch(`https://api.github.com/repos/${repo}`);
        
        if (!response.ok) {
            throw new Error(`Ошибка GitHub API: ${response.status}`);
        }
        
        const data = await response.json();

        // Форматируем числа (например, 1000 -> 1k)
        const formatNumber = (num) => {
            if (num >= 1000) {
                return (num / 1000).toFixed(1) + 'k';
            }
            return num;
        };

        const lastUpdate = new Date(data.pushed_at).toLocaleString('ru-RU', {
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        statsContent.innerHTML = `
            <div class="space-y-4">
                <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-black/30 rounded-lg">
                    <span class="font-semibold flex items-center gap-2"><i class="fa-solid fa-star text-yellow-400"></i> Звёзды</span>
                    <span class="font-bold text-lg">${formatNumber(data.stargazers_count)}</span>
                </div>
                <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-black/30 rounded-lg">
                    <span class="font-semibold flex items-center gap-2"><i class="fa-solid fa-code-fork text-blue-400"></i> Форки</span>
                    <span class="font-bold text-lg">${formatNumber(data.forks_count)}</span>
                </div>
                <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-black/30 rounded-lg">
                    <span class="font-semibold flex items-center gap-2"><i class="fa-solid fa-eye text-green-400"></i> Наблюдатели</span>
                    <span class="font-bold text-lg">${formatNumber(data.watchers_count)}</span>
                </div>
                <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-black/30 rounded-lg">
                    <span class="font-semibold flex items-center gap-2"><i class="fa-solid fa-bug text-red-400"></i> Открытые проблемы</span>
                    <span class="font-bold text-lg">${data.open_issues_count}</span>
                </div>
                 <div class="pt-2 text-center">
                    <p class="text-xs text-gray-500 dark:text-gray-400">
                        Последнее обновление: ${lastUpdate}
                    </p>
                </div>
            </div>
        `;

    } catch (error) {
        statsContent.innerHTML = `
            <div class="text-center text-red-500">
                <i class="fa-solid fa-circle-exclamation text-3xl"></i>
                <p class="mt-2 font-semibold">Не удалось загрузить статистику.</p>
                <p class="text-sm">${error.message}</p>
            </div>
        `;
    }
}