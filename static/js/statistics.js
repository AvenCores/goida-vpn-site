async function loadGitHubStats() {
    const statsContent = document.getElementById('stats-content');
    
    // Показываем спиннер
    statsContent.innerHTML = `
        <div class="text-center py-6">
            <i class="fa-solid fa-spinner fa-spin text-3xl text-gray-400"></i>
            <p class="mt-2 text-sm text-gray-500">Загрузка данных...</p>
        </div>`;

    try {
        // Используем относительный путь, чтобы работало на GH Pages
        const response = await fetch(`api/github-stats.json?t=${new Date().getTime()}`);
        
        if (!response.ok) {
            throw new Error(`Ошибка HTTP: ${response.status}`);
        }
        
        const data = await response.json();

        if (data.error && data.error !== "Token not configured") {
            // Если токен не настроен, мы все равно можем показать хотя бы звезды, если они есть,
            // но если ошибка другая - выводим её.
            throw new Error(`API Error: ${data.error}`);
        }

        // Форматирование чисел
        const formatNumber = (num) => {
            if (!num && num !== 0) return '0';
            if (num >= 1000) {
                return (num / 1000).toFixed(1) + 'К';
            }
            return num;
        };

        // Форматирование даты
        let dateString = "Неизвестно";
        if (data.pushed_at) {
            dateString = new Date(data.pushed_at).toLocaleString('ru-RU', {
                day: 'numeric',
                month: 'long',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        statsContent.innerHTML = `
            <div class="space-y-4">
                <div class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-100 dark:border-blue-800">
                    <div class="text-sm text-gray-500 dark:text-gray-400 mb-1">Последнее обновление</div>
                    <div class="font-bold text-lg flex items-center gap-2">
                        <i class="fa-regular fa-clock text-blue-500"></i>
                        ${dateString}
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                     <div class="p-3 bg-gray-50 dark:bg-black/30 rounded-lg text-center">
                        <div class="text-xs text-gray-500 uppercase font-bold mb-1">Звёзды</div>
                        <div class="text-xl font-bold text-yellow-500">
                            <i class="fa-solid fa-star mr-1"></i> ${formatNumber(data.stargazers_count)}
                        </div>
                    </div>
                     <div class="p-3 bg-gray-50 dark:bg-black/30 rounded-lg text-center">
                        <div class="text-xs text-gray-500 uppercase font-bold mb-1">Просмотры (14Д)</div>
                        <div class="text-xl font-bold text-purple-400">
                            <i class="fa-solid fa-eye mr-1"></i> ${formatNumber(data.views.count)}
                        </div>
                    </div>
                </div>

                <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-black/30 rounded-lg">
                    <span class="font-semibold flex items-center gap-2 text-sm"><i class="fa-solid fa-download text-green-500"></i> Клоны (14Д)</span>
                    <span class="font-bold text-lg">${formatNumber(data.clones.count)}</span>
                </div>
                
                <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-black/30 rounded-lg">
                    <span class="font-semibold flex items-center gap-2 text-sm"><i class="fa-solid fa-user-check text-orange-400"></i> Уникальные клоны (14Д)</span>
                    <span class="font-bold text-lg">${formatNumber(data.clones.uniques)}</span>
                </div>
                 
                 <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-black/30 rounded-lg">
                    <span class="font-semibold flex items-center gap-2 text-sm"><i class="fa-solid fa-users text-indigo-400"></i> Уникальные посетители (14Д)</span>
                    <span class="font-bold text-lg">${formatNumber(data.views.uniques)}</span>
                </div>
            </div>
            <div class="mt-4 text-center text-xs text-gray-400">
                Статистика обновляется при каждой сборке сайта.
            </div>
        `;
    } catch (error) {
        console.error(error);
        statsContent.innerHTML = `
            <div class="text-center text-red-500 py-4">
                <i class="fa-solid fa-circle-exclamation text-3xl mb-2"></i>
                <p class="font-semibold">Не удалось загрузить статистику</p>
                <p class="text-xs mt-1 opacity-75">${error.message}</p>
            </div>
        `;
    }
}