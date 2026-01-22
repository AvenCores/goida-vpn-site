async function loadGitHubStats() {
    const statsContent = document.getElementById('stats-content');
    
    // Показываем спиннер при каждом открытии
    statsContent.innerHTML = `
        <div class="text-center">
            <i class="fa-solid fa-spinner fa-spin text-3xl text-gray-400"></i>
            <p class="mt-2 text-sm text-gray-500">Загрузка данных...</p>
        </div>`;

    try {
        const response = await fetch(`/api/github-stats.json`);
        
        if (!response.ok) {
            throw new Error(`Ошибка загрузки файла: ${response.status}`);
        }
        
        const data = await response.json();

        if (data.error) {
            throw new Error(`Ошибка API: ${data.error}`);
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
                            <span class="font-semibold flex items-center gap-2"><i class="fa-solid fa-download text-blue-400"></i> Clones in last 14 days</span>
                            <span class="font-bold text-lg">${data.clones.count}</span>
                        </div>
                        <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-black/30 rounded-lg">
                            <span class="font-semibold flex items-center gap-2"><i class="fa-solid fa-user-check text-green-400"></i> Unique cloners in last 14 days</span>
                            <span class="font-bold text-lg">${data.clones.uniques}</span>
                        </div>
                        <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-black/30 rounded-lg">
                            <span class="font-semibold flex items-center gap-2"><i class="fa-solid fa-eye text-yellow-400"></i> Total views in last 14 days</span>
                            <span class="font-bold text-lg">${data.views.count}</span>
                        </div>
                        <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-black/30 rounded-lg">
                            <span class="font-semibold flex items-center gap-2"><i class="fa-solid fa-users text-purple-400"></i> Unique visitors in last 14 days</span>
                            <span class="font-bold text-lg">${data.views.uniques}</span>
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