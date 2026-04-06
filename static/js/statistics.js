async function loadGitHubStats() {
    const statsContent = document.getElementById('stats-content');
    const t = (key) => window.i18n ? window.i18n.t(key) : key;

    // Показываем спиннер только если нет загруженных данных
    if (!statsContent.querySelector('.stats-container')) {
        statsContent.innerHTML = `
            <div class="text-center py-6">
                <i class="fa-solid fa-spinner fa-spin text-3xl text-gray-400"></i>
                <p class="mt-2 text-sm text-gray-500">${t('stats.loading')}</p>
            </div>`;
    }

    try {
        const response = await fetch(`api/github-stats.json?t=${new Date().getTime()}`);
        
        if (!response.ok) {
            throw new Error(`Ошибка HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        const stats = {
            pushed_at: data.pushed_at || null,
            stargazers_count: Number(data.stargazers_count || 0),
            clones: {
                count: Number((data.clones && data.clones.count) || 0),
                uniques: Number((data.clones && data.clones.uniques) || 0)
            },
            views: {
                count: Number((data.views && data.views.count) || 0),
                uniques: Number((data.views && data.views.uniques) || 0)
            },
            referrers: Array.isArray(data.referrers) ? data.referrers : [],
            popular_content: Array.isArray(data.popular_content) ? data.popular_content : [],
            error: data.error || null
        };

        if (stats.error && stats.error !== "Token not configured") {
            console.warn(`GitHub stats API warning: ${stats.error}`);
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
        let dateString = t('stats.last_update');
        if (stats.pushed_at) {
            const dateObj = new Date(stats.pushed_at);
            const lang = window.i18n ? window.i18n.getLanguage() : 'ru';
            const localeMap = {
                ru: 'ru-RU',
                en: 'en-US',
                de: 'de-DE',
                uk: 'uk-UA',
                be: 'be-BY'
            };
            dateString = dateObj.toLocaleString(localeMap[lang] || 'ru-RU', {
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
            <div class="space-y-3 animate-fade-in">
                <!-- Последнее обновление -->
                <div class="p-3 sm:p-4 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-100 dark:border-blue-800/50 shadow-sm">
                    <div class="text-[10px] text-blue-600 dark:text-blue-400 uppercase font-bold mb-1 tracking-wider">${t('stats.last_update')}</div>
                    <div class="font-bold text-sm sm:text-base flex items-center gap-2 text-gray-800 dark:text-gray-100 flex-wrap">
                        <i class="fa-regular fa-clock text-blue-500 shrink-0"></i>
                        <span>${dateString}</span>
                    </div>
                </div>

                <!-- Звёзды и просмотры -->
                <div class="grid grid-cols-2 gap-2 sm:gap-4">
                    <div class="p-3 sm:p-4 bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-yellow-900/10 dark:to-amber-900/10 rounded-xl border border-yellow-100 dark:border-yellow-800/30 text-center shadow-sm">
                        <div class="text-[10px] text-amber-700 dark:text-amber-500 uppercase font-bold mb-1 tracking-wider">${t('stats.stars')}</div>
                        <div class="text-xl sm:text-2xl font-black text-amber-500">
                            <i class="fa-solid fa-star mr-1 drop-shadow-sm"></i>${formatNumber(stats.stargazers_count)}
                        </div>
                    </div>
                    <div class="p-3 sm:p-4 bg-gradient-to-br from-purple-50 to-fuchsia-50 dark:from-purple-900/10 dark:to-fuchsia-900/10 rounded-xl border border-purple-100 dark:border-purple-800/30 text-center shadow-sm">
                        <div class="text-[10px] text-purple-700 dark:text-purple-400 uppercase font-bold mb-1 tracking-wider leading-tight">${t('stats.views_14d')}</div>
                        <div class="text-xl sm:text-2xl font-black text-purple-500 dark:text-purple-400">
                            <i class="fa-solid fa-eye mr-1 drop-shadow-sm"></i>${formatNumber(stats.views.count)}
                        </div>
                    </div>
                </div>

                <!-- Строки со статистикой -->
                <div class="space-y-2 sm:space-y-3">
                    <div class="flex justify-between items-center p-3 sm:p-4 bg-gray-50 dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/10 shadow-sm hover:bg-white dark:hover:bg-white/10 transition-colors">
                        <span class="font-bold flex items-center gap-2 sm:gap-3 text-xs sm:text-sm text-gray-700 dark:text-gray-300 min-w-0">
                            <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600 dark:text-green-400 shrink-0">
                                <i class="fa-solid fa-download text-xs"></i>
                            </div>
                            <span class="truncate">${t('stats.clones_14d')}</span>
                        </span>
                        <span class="font-black text-lg sm:text-xl text-gray-800 dark:text-gray-100 shrink-0 ml-2">${formatNumber(stats.clones.count)}</span>
                    </div>

                    <div class="flex justify-between items-center p-3 sm:p-4 bg-gray-50 dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/10 shadow-sm hover:bg-white dark:hover:bg-white/10 transition-colors">
                        <span class="font-bold flex items-center gap-2 sm:gap-3 text-xs sm:text-sm text-gray-700 dark:text-gray-300 min-w-0">
                            <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center text-orange-600 dark:text-orange-400 shrink-0">
                                <i class="fa-solid fa-user-check text-xs"></i>
                            </div>
                            <span class="truncate">${t('stats.unique_clones_14d')}</span>
                        </span>
                        <span class="font-black text-lg sm:text-xl text-gray-800 dark:text-gray-100 shrink-0 ml-2">${formatNumber(stats.clones.uniques)}</span>
                    </div>

                    <div class="flex justify-between items-center p-3 sm:p-4 bg-gray-50 dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/10 shadow-sm hover:bg-white dark:hover:bg-white/10 transition-colors">
                        <span class="font-bold flex items-center gap-2 sm:gap-3 text-xs sm:text-sm text-gray-700 dark:text-gray-300 min-w-0">
                            <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center text-indigo-600 dark:text-indigo-400 shrink-0">
                                <i class="fa-solid fa-users text-xs"></i>
                            </div>
                            <span class="truncate">${t('stats.unique_visitors_14d')}</span>
                        </span>
                        <span class="font-black text-lg sm:text-xl text-gray-800 dark:text-gray-100 shrink-0 ml-2">${formatNumber(stats.views.uniques)}</span>
                    </div>
                </div>

                <div class="mt-4 text-center text-[10px] text-gray-400 uppercase tracking-widest font-bold opacity-60 px-2">
                    ${t('stats.stats_updated_on_build')}
                </div>
            </div>
        `;

        // 2. Referrers Tab HTML
        let referrersTabHtml = '<div class="space-y-2 sm:space-y-3 animate-fade-in">';
        if (stats.referrers.length > 0) {
            stats.referrers.forEach(ref => {
                referrersTabHtml += `
                    <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/10 hover:bg-white dark:hover:bg-white/10 transition-colors gap-2">
                        <div class="flex items-center gap-2 sm:gap-3 min-w-0">
                            <div class="w-7 h-7 sm:w-8 sm:h-8 shrink-0 rounded-lg bg-teal-100 dark:bg-teal-900/30 flex items-center justify-center text-teal-600 dark:text-teal-400">
                                <i class="fa-solid fa-link text-xs"></i>
                            </div>
                            <div class="flex flex-col min-w-0">
                                <span class="font-bold text-xs sm:text-sm text-gray-800 dark:text-gray-200 truncate" title="${ref.referrer}">${ref.referrer}</span>
                                <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wide">${t('stats.referrer_label')}</span>
                            </div>
                        </div>
                        <div class="text-right shrink-0">
                            <div class="font-black text-xs sm:text-sm text-gray-800 dark:text-gray-100 whitespace-nowrap">${formatNumber(ref.count)} <span class="text-[10px] font-normal text-gray-400">${t('stats.views_short')}</span></div>
                            <div class="text-[10px] text-gray-400">${formatNumber(ref.uniques)} ${t('stats.unique_short')}</div>
                        </div>
                    </div>
                `;
            });
        } else {
            referrersTabHtml += `
                <div class="text-center py-10 opacity-60">
                    <i class="fa-solid fa-link-slash text-4xl mb-3 text-gray-300 dark:text-gray-600"></i>
                    <p class="text-sm text-gray-500">${t('stats.no_referrers')}</p>
                </div>
            `;
        }
        referrersTabHtml += '</div>';

        // 3. Popular Content Tab HTML
        let contentTabHtml = '<div class="space-y-2 sm:space-y-3 animate-fade-in">';
        if (stats.popular_content.length > 0) {
            stats.popular_content.forEach(item => {
                contentTabHtml += `
                    <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/10 hover:bg-white dark:hover:bg-white/10 transition-colors gap-2">
                        <div class="flex items-center gap-2 sm:gap-3 min-w-0">
                            <div class="w-7 h-7 sm:w-8 sm:h-8 shrink-0 rounded-lg bg-pink-100 dark:bg-pink-900/30 flex items-center justify-center text-pink-600 dark:text-pink-400">
                                <i class="fa-solid fa-file-lines text-xs"></i>
                            </div>
                            <div class="flex flex-col min-w-0">
                                <span class="font-bold text-xs sm:text-sm text-gray-800 dark:text-gray-200 truncate" title="${item.path}">${item.title || item.path}</span>
                                <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wide truncate" title="${item.path}">${item.path}</span>
                            </div>
                        </div>
                        <div class="text-right shrink-0">
                            <div class="font-black text-xs sm:text-sm text-gray-800 dark:text-gray-100 whitespace-nowrap">${formatNumber(item.count)} <span class="text-[10px] font-normal text-gray-400">${t('stats.views_short')}</span></div>
                            <div class="text-[10px] text-gray-400">${formatNumber(item.uniques)} ${t('stats.unique_short')}</div>
                        </div>
                    </div>
                `;
            });
        } else {
            contentTabHtml += `
                <div class="text-center py-10 opacity-60">
                    <i class="fa-regular fa-folder-open text-4xl mb-3 text-gray-300 dark:text-gray-600"></i>
                    <p class="text-sm text-gray-500">${t('stats.no_content')}</p>
                </div>
            `;
        }
        contentTabHtml += '</div>';

        // Итоговая структура
        statsContent.innerHTML = `
            <div class="stats-container flex flex-col h-full">
                <!-- Вкладки (touch-friendly) -->
                <div class="flex-shrink-0 flex space-x-1 bg-gray-100 dark:bg-white/5 p-1 rounded-xl mb-3">
                    <button onclick="switchStatsTab('general', this)" class="stats-tab-btn active flex-1 py-2.5 text-xs font-bold rounded-lg transition-all bg-white dark:bg-gray-700 shadow-sm text-gray-900 dark:text-white touch-manipulation">${t('stats.general')}</button>
                    <button onclick="switchStatsTab('referrers', this)" class="stats-tab-btn flex-1 py-2.5 text-xs font-bold rounded-lg transition-all text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 touch-manipulation">${t('stats.referrers')}</button>
                    <button onclick="switchStatsTab('content', this)" class="stats-tab-btn flex-1 py-2.5 text-xs font-bold rounded-lg transition-all text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 touch-manipulation">${t('stats.popular_content')}</button>
                </div>

                <!-- Скроллируемый контент -->
                <div class="relative overflow-hidden rounded-xl border border-gray-100 dark:border-white/5 bg-gray-50/50 dark:bg-white/5">
                    <!-- 
                        Высота: на мобиле берём всю доступную высоту модального окна (calc),
                        на sm+ используем фиксированную высоту.
                    -->
                    <div class="stats-scroll-area overflow-y-auto p-3 sm:p-4 custom-scrollbar">
                        <div id="stats-tab-general" class="stats-tab-content block">
                            ${generalTabHtml}
                        </div>
                        <div id="stats-tab-referrers" class="stats-tab-content hidden">
                            ${referrersTabHtml}
                        </div>
                        <div id="stats-tab-content" class="stats-tab-content hidden">
                            ${contentTabHtml}
                        </div>
                    </div>
                </div>
            </div>
            
            <style>
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(5px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .animate-fade-in {
                    animation: fadeIn 0.3s ease-out forwards;
                }

                /* Высота скролл-области: адаптивная */
                .stats-scroll-area {
                    /* Мобиле: учитываем высоту шапки модалки + вкладок */
                    max-height: calc(100dvh - 160px);
                    /* Плавный инерционный скролл на iOS */
                    -webkit-overflow-scrolling: touch;
                    overscroll-behavior: contain;
                }
                @media (min-width: 640px) {
                    .stats-scroll-area {
                        max-height: 485px;
                    }
                }

                /* Тонкий скроллбар */
                .custom-scrollbar::-webkit-scrollbar { width: 4px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background-color: #cbd5e1;
                    border-radius: 20px;
                }
                .dark .custom-scrollbar::-webkit-scrollbar-thumb {
                    background-color: #475569;
                }
            </style>
        `;

        // Переключение вкладок
        window.switchStatsTab = (tabName, btnElement) => {
            document.querySelectorAll('.stats-tab-content').forEach(el => {
                el.classList.add('hidden');
                el.classList.remove('block');
            });
            const selectedTab = document.getElementById(`stats-tab-${tabName}`);
            if (selectedTab) {
                selectedTab.classList.remove('hidden');
                selectedTab.classList.add('block');
            }
            document.querySelectorAll('.stats-tab-btn').forEach(btn => {
                btn.className = 'stats-tab-btn flex-1 py-2.5 text-xs font-bold rounded-lg transition-all text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 touch-manipulation';
            });
            btnElement.className = 'stats-tab-btn active flex-1 py-2.5 text-xs font-bold rounded-lg transition-all bg-white dark:bg-gray-700 shadow-sm text-gray-900 dark:text-white touch-manipulation';
        };

    } catch (error) {
        console.error(error);
        statsContent.innerHTML = `
            <div class="text-center text-red-500 py-6">
                <i class="fa-solid fa-circle-exclamation text-3xl mb-2"></i>
                <p class="font-semibold text-sm">${t('stats.error_loading')}</p>
                <p class="text-xs mt-1 opacity-75">${error.message}</p>
            </div>
        `;
    }
}
