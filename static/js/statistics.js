async function loadGitHubStats() {
    const statsContent = document.getElementById('stats-content');
    
    // Показываем спиннер только если нет загруженных данных (проверяем наличие основного контейнера)
    if (!statsContent.querySelector('.stats-container')) {
        statsContent.innerHTML = `
            <div class="text-center py-6">
                <i class="fa-solid fa-spinner fa-spin text-3xl text-gray-400"></i>
                <p class="mt-2 text-sm text-gray-500">Загрузка данных...</p>
            </div>`;
    }

    try {
        // Используем относительный путь, чтобы работало на GH Pages
        const response = await fetch(`api/github-stats.json?t=${new Date().getTime()}`);
        
        if (!response.ok) {
            throw new Error(`Ошибка HTTP: ${response.status}`);
        }
        
        const data = await response.json();

        if (data.error && data.error !== "Token not configured") {
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

        // --- ГЕНЕРАЦИЯ HTML ДЛЯ ВКЛАДОК ---

        // 1. General Tab HTML
        const generalTabHtml = `
            <div class="space-y-4">
                <div class="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-100 dark:border-blue-800/50 shadow-sm">
                    <div class="text-xs text-blue-600 dark:text-blue-400 uppercase font-bold mb-1 tracking-wider">Последнее обновление</div>
                    <div class="font-bold text-lg flex items-center gap-2 text-gray-800 dark:text-gray-100">
                        <i class="fa-regular fa-clock text-blue-500"></i>
                        ${dateString}
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                     <div class="p-4 bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-yellow-900/10 dark:to-amber-900/10 rounded-xl border border-yellow-100 dark:border-yellow-800/30 text-center shadow-sm">
                        <div class="text-[10px] text-amber-700 dark:text-amber-500 uppercase font-bold mb-1 tracking-wider">Звёзды</div>
                        <div class="text-2xl font-black text-amber-500">
                            <i class="fa-solid fa-star mr-1 drop-shadow-sm"></i> ${formatNumber(data.stargazers_count)}
                        </div>
                    </div>
                     <div class="p-4 bg-gradient-to-br from-purple-50 to-fuchsia-50 dark:from-purple-900/10 dark:to-fuchsia-900/10 rounded-xl border border-purple-100 dark:border-purple-800/30 text-center shadow-sm">
                        <div class="text-[10px] text-purple-700 dark:text-purple-400 uppercase font-bold mb-1 tracking-wider">Просмотры (14д)</div>
                        <div class="text-2xl font-black text-purple-500 dark:text-purple-400">
                            <i class="fa-solid fa-eye mr-1 drop-shadow-sm"></i> ${formatNumber(data.views.count)}
                        </div>
                    </div>
                </div>

                <div class="space-y-3">
                    <div class="flex justify-between items-center p-4 bg-gray-50 dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/10 shadow-sm hover:bg-white dark:hover:bg-white/10 transition-colors">
                        <span class="font-bold flex items-center gap-3 text-sm text-gray-700 dark:text-gray-300">
                            <div class="w-8 h-8 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600 dark:text-green-400">
                                <i class="fa-solid fa-download"></i>
                            </div>
                            Клоны (14д)
                        </span>
                        <span class="font-black text-xl text-gray-800 dark:text-gray-100">${formatNumber(data.clones.count)}</span>
                    </div>
                    
                    <div class="flex justify-between items-center p-4 bg-gray-50 dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/10 shadow-sm hover:bg-white dark:hover:bg-white/10 transition-colors">
                        <span class="font-bold flex items-center gap-3 text-sm text-gray-700 dark:text-gray-300">
                            <div class="w-8 h-8 rounded-lg bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center text-orange-600 dark:text-orange-400">
                                <i class="fa-solid fa-user-check"></i>
                            </div>
                            Уникальные клоны
                        </span>
                        <span class="font-black text-xl text-gray-800 dark:text-gray-100">${formatNumber(data.clones.uniques)}</span>
                    </div>
                     
                     <div class="flex justify-between items-center p-4 bg-gray-50 dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/10 shadow-sm hover:bg-white dark:hover:bg-white/10 transition-colors">
                        <span class="font-bold flex items-center gap-3 text-sm text-gray-700 dark:text-gray-300">
                            <div class="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                                <i class="fa-solid fa-users"></i>
                            </div>
                            Уникальные посетители
                        </span>
                        <span class="font-black text-xl text-gray-800 dark:text-gray-100">${formatNumber(data.views.uniques)}</span>
                    </div>
                </div>
                <div class="mt-6 text-center text-[10px] text-gray-400 uppercase tracking-widest font-bold opacity-60">
                    Статистика обновляется при каждой сборке сайта.
                </div>
            </div>
        `;

        // 2. Referrers Tab HTML
        let referrersTabHtml = '';
        if (data.referrers && data.referrers.length > 0) {
            referrersTabHtml = '<div class="space-y-3">';
            data.referrers.forEach(ref => {
                referrersTabHtml += `
                    <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/10 hover:bg-white dark:hover:bg-white/10 transition-colors">
                        <div class="flex items-center gap-3 overflow-hidden">
                             <div class="w-8 h-8 flex-shrink-0 rounded-lg bg-teal-100 dark:bg-teal-900/30 flex items-center justify-center text-teal-600 dark:text-teal-400">
                                <i class="fa-solid fa-link text-xs"></i>
                            </div>
                            <div class="flex flex-col min-w-0">
                                <span class="font-bold text-sm text-gray-800 dark:text-gray-200 truncate" title="${ref.referrer}">${ref.referrer}</span>
                                <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wide">Источник</span>
                            </div>
                        </div>
                        <div class="text-right flex-shrink-0">
                            <div class="font-black text-sm text-gray-800 dark:text-gray-100">${formatNumber(ref.count)} <span class="text-xs font-normal text-gray-400">просмотров</span></div>
                            <div class="text-[10px] text-gray-400">${formatNumber(ref.uniques)} уник.</div>
                        </div>
                    </div>
                `;
            });
            referrersTabHtml += '</div>';
        } else {
            referrersTabHtml = `
                <div class="flex flex-col items-center justify-center h-full opacity-60 pb-10">
                    <i class="fa-solid fa-link-slash text-4xl mb-3 text-gray-300 dark:text-gray-600"></i>
                    <p class="text-sm text-gray-500">Нет данных об источниках</p>
                </div>
            `;
        }

        // 3. Popular Content Tab HTML
        let contentTabHtml = '';
        if (data.popular_content && data.popular_content.length > 0) {
            contentTabHtml = '<div class="space-y-3">';
            data.popular_content.forEach(item => {
                contentTabHtml += `
                    <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/10 hover:bg-white dark:hover:bg-white/10 transition-colors">
                        <div class="flex items-center gap-3 overflow-hidden">
                             <div class="w-8 h-8 flex-shrink-0 rounded-lg bg-pink-100 dark:bg-pink-900/30 flex items-center justify-center text-pink-600 dark:text-pink-400">
                                <i class="fa-solid fa-file-lines text-xs"></i>
                            </div>
                            <div class="flex flex-col min-w-0">
                                <span class="font-bold text-sm text-gray-800 dark:text-gray-200 truncate" title="${item.path}">${item.title || item.path}</span>
                                <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wide truncate" title="${item.path}">${item.path}</span>
                            </div>
                        </div>
                        <div class="text-right flex-shrink-0">
                            <div class="font-black text-sm text-gray-800 dark:text-gray-100">${formatNumber(item.count)} <span class="text-xs font-normal text-gray-400">просмотров</span></div>
                            <div class="text-[10px] text-gray-400">${formatNumber(item.uniques)} уник.</div>
                        </div>
                    </div>
                `;
            });
            contentTabHtml += '</div>';
        } else {
            contentTabHtml = `
                 <div class="flex flex-col items-center justify-center h-full opacity-60 pb-10">
                    <i class="fa-regular fa-folder-open text-4xl mb-3 text-gray-300 dark:text-gray-600"></i>
                    <p class="text-sm text-gray-500">Нет данных о популярном контенте</p>
                </div>
            `;
        }

        // Итоговая структура
        statsContent.innerHTML = `
            <div class="stats-container flex flex-col h-[600px] p-6">
                <!-- Меню вкладок (фиксированное) -->
                <div class="flex-shrink-0 flex space-x-1 bg-gray-100 dark:bg-white/5 p-1 rounded-xl mb-4">
                    <button onclick="switchStatsTab('general', this)" class="stats-tab-btn active flex-1 py-2 text-xs font-bold rounded-lg transition-all bg-white dark:bg-gray-700 shadow-sm text-gray-900 dark:text-white">Общее</button>
                    <button onclick="switchStatsTab('referrers', this)" class="stats-tab-btn flex-1 py-2 text-xs font-bold rounded-lg transition-all text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200">Источники</button>
                    <button onclick="switchStatsTab('content', this)" class="stats-tab-btn flex-1 py-2 text-xs font-bold rounded-lg transition-all text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200">Контент</button>
                </div>

                <!-- Область контента (заполняет пространство, скроллится) -->
                <div class="flex-1 min-h-0 overflow-hidden relative rounded-xl border border-gray-100 dark:border-white/5 bg-gray-50/50 dark:bg-white/5">
                     <div class="h-full overflow-y-auto p-4 custom-scrollbar">
                        <div id="stats-tab-general" class="stats-tab-content block">
                            ${generalTabHtml}
                        </div>
                        <div id="stats-tab-referrers" class="stats-tab-content hidden h-full">
                            ${referrersTabHtml}
                        </div>
                        <div id="stats-tab-content" class="stats-tab-content hidden h-full">
                            ${contentTabHtml}
                        </div>
                    </div>
                </div>
            </div>
            
            <style>
                /* Тонкий скроллбар для области контента */
                .custom-scrollbar::-webkit-scrollbar {
                    width: 4px;
                }
                .custom-scrollbar::-webkit-scrollbar-track {
                    background: transparent;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background-color: #cbd5e1;
                    border-radius: 20px;
                }
                .dark .custom-scrollbar::-webkit-scrollbar-thumb {
                    background-color: #475569;
                }
            </style>
        `;

        // Функция переключения (глобальная область видимости, чтобы работал onclick)
        window.switchStatsTab = (tabName, btnElement) => {
            // Скрыть все вкладки
            document.querySelectorAll('.stats-tab-content').forEach(el => {
                el.classList.add('hidden');
                el.classList.remove('block');
            });
            // Показать выбранную
            const selectedTab = document.getElementById(`stats-tab-${tabName}`);
            if (selectedTab) {
                selectedTab.classList.remove('hidden');
                selectedTab.classList.add('block');
            }

            // Обновить стили кнопок
            document.querySelectorAll('.stats-tab-btn').forEach(btn => {
                // Сброс активного состояния
                btn.className = 'stats-tab-btn flex-1 py-2 text-xs font-bold rounded-lg transition-all text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200';
            });
            
            // Установка активного состояния
            btnElement.className = 'stats-tab-btn active flex-1 py-2 text-xs font-bold rounded-lg transition-all bg-white dark:bg-gray-700 shadow-sm text-gray-900 dark:text-white';
        };

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