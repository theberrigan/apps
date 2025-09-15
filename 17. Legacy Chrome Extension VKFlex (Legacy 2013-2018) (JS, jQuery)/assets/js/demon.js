// VK Flex Chrome Extension: demon.js
// Dependencies: jQuery.js, common.js

var vkf_demon,               // Объект управления демоном
    isSettingsReady = false; // Флаг, обозначающий, что настройки готовы

(function ($) {


// Объект управления демоном
function VKFlexDemon () {

    var that = this,
        B = $('body'),
        C = vkf_common,
        D = $(document),
        W = $(window),
        update_timer;

    this.audios = null;

    // Инициализация
    var init = function () {
        C.log('[' + (new Date()).toLocaleString() + '] Init...');

        // [Async] Получить настройки и считать языковой файл
        that.get_settings(function () {
            User.init(function () {
                // События обращения к ядру
                chrome.runtime.onMessage.addListener(that.onCoreMsg);

                // При обращении из инъекции
                chrome.runtime.onMessageExternal.addListener(that.onExternalMessage);

                // Событие ввода в омнибокс "vkf ..."
                chrome.omnibox.onInputEntered.addListener(that.onOmniboxQuery);

                // Событие клика по кнопкам во всплывающем уведомлении
                chrome.notifications.onButtonClicked.addListener(that.onNotificationClick);

                // Событие клика по всплывающему уведомлению
                chrome.notifications.onClicked.addListener(that.onNotificationClick);

                // Событие закрытия всплывающего уведомления
                chrome.notifications.onClosed.addListener(that.onNotificationClose);

                // Установить цвет счётчика
                chrome.browserAction.setBadgeBackgroundColor({ color: '#ff5757' });

                // Внешние ссылки
                that.external_links = {
                    soc_vk: 'http://vk.com/vk.flex',
                    soc_tw: 'https://twitter.com/vkflex_chrome',
                    chromestore: 'http://vk-flex.ru/go/',
                    share_vk: 'http://vk.com/share.php?url=http%3A%2F%2Fvk-flex.ru%2Fgo%2F&title=' + encodeURIComponent(that.lang_data.demon['share_vk_title']) + '&description=' + encodeURIComponent(that.lang_data.demon['share_vk_description']) + '&image=http%3A%2F%2Fvk-flex.ru%2Fassets%2Fimages%2Fshare.png',
                    website: 'http://vk-flex.ru/'
                };

                // Группа в ВК
                chrome.contextMenus.create({
                    title: that.lang_data.demon['cm_in_vk'],
                    contexts: ['browser_action'],
                    onclick: function () {
                        window.open(that.external_links.soc_vk, '_blank');
                    }
                });

                // Страница в твиттере
                chrome.contextMenus.create({
                    title: that.lang_data.demon['cm_in_tw'],
                    contexts: ['browser_action'],
                    onclick: function () {
                        window.open(that.external_links.soc_tw, '_blank');
                    }
                });

                // Страница в Chrome store
                chrome.contextMenus.create({
                    title: that.lang_data.demon['cm_in_cs'],
                    contexts: ['browser_action'],
                    onclick: function () {
                        window.open(that.external_links.chromestore, '_blank');
                    }
                });

                // Сайт
                chrome.contextMenus.create({
                    title: that.lang_data.demon['cm_site'],
                    contexts: ['browser_action'],
                    onclick: function () {
                        window.open(that.external_links.website, '_blank');
                    }
                });

                // Рассказать друзьям в вк
                chrome.contextMenus.create({
                    title: that.lang_data.demon['cm_share_vk'],
                    contexts: ['browser_action'],
                    onclick: function () {
                        window.open(that.external_links.share_vk, 'share_popup', 'width=700,height=500,toolbar=0,menubar=0,location=1,status=1,scrollbars=1,resizable=1,left=0,top=0');
                    }
                });

                // Флаг, обозначающий, что демон успешно инициализирован и готов к работе
                isSettingsReady = true;

                // Применить настройки и запустить проверку
                that.apply_settings();
            });
        });
    };

    // Статичные данные
    this.statics = {
        // Количество вариантов звуковых уведомлений
        sounds: 9,

        // Частота запросов к ВК (мс)
        update_delays: [3000, 10000, 30000, 60000],

        // Языки (d - default, vk)
        langs: {
            vk: {
                code: null,
                label: 'По умолчанию'
            },
            0: {
                code: 'ru',
                label: 'Русский'
            }
        }
    };

    // Информация, полученная из ВК
    this.vk_data = {
        status: 'loading',
        counters: {}
    };

    // Ссылка "Поделиться в ВК"
    this.external_links = {};

    // Язык ВК
    this.vk_lang = null;

    // ID языка (>=0)
    this.lang_id = null;

    // JSON со всеми строками i18n
    this.lang_data = {};

    // Настройки
    this.settings = {};

    // Звук уведомления
    this.sound = null;

    // Таймер до скрытия текущего уведомления
    this.notify_timer = null;

    // id последнего уведомления
    this.last_notify_id = '';

    // Манифест
    this.manifest = chrome.runtime.getManifest();

    // Тексты локализации ВК
    this.vk_messages = {
        0: { // рус.
            friends_only: 'только для друзей'
        },
        1: { // укр.
            friends_only: 'лише для друзів'
        },
        3: { // англ.
            friends_only: 'Friends only'
        },
        97: { // каз.
            friends_only: 'тек достарым үшін'
        },
        100: { // доревоц.
            friends_only: 'только для знакомцевъ'
        },
        114: { // беларус.
            friends_only: 'толькі для сяброў'
        }
    };

    // Настройки расширения по умолчанию
    this.defaults = {
        common: {
            language: 'vk',                 // Язык расширения (int-код либо 'vk')
            update_delay: 0,                // Частота обращений к серверу
            show_welcome_msg: true          // Показывать ли сообщения после обновления или установки расширения
        },
        vk: {                               // Настройки интерфейса ВК
            audio_downlink: true,           // Ссылка на скачивание трека
            audio_info: 1,                  // Инфо о треке (0 - off, 1 - bitrate & size, 2 - bitrate, 3 - size)
            video_downlink: true,           // Ссылка на скачивание видео
            video_show_size: true,          // Показывать размер видео
            fix_menu: true,                 // Фиксировать левое меню
            change_videos_link: false,      // Заменить ссылку "Мои видеозаписи"
            hide_advert: true,              // Удалять рекламу
            hide_potential_friends: false,  // Скрывать список предлагаемых друзей
            hide_photo_like: true,          // Скрывать большой лайк в фотогалерее
            add_middlename: true,           // Добавлять отчество на сраницу редактирования профиля
            skip_redirect: true,            // Пропускать страницу редиректа
            show_user_age: true,            // Возраст пользователя
            show_user_zodiac: true,         // Знак зодиака
            add_calendar: false,            // Добавить календарь в левое меню
            url_shortener: true,            // Сокращение ссылок
            simplify_audio_ui: false        // Упростить интерфейс раздела аудиозаписей
            // fchat_size_control: 0,          // Запоминать размер мини-чата (0 - off, 1 - window y-fit, 2 - remember size)
        },
        notifications: {                    // Настройки уведомлений
            sound: 5,                       // id звукового уведомления или false
            popup: true,                    // Текстовое уведомление
            counter: true,                  // Отображать общий счётчик
            events: {                       // События, о которых уведомлять
                friends: true,              // Новые друзья
                messages: true,             // Новые сообщения
                mentions: true,             // Новые упоминания
                groups: true,               // Новые группы
                photos: true,               // Новые фотографии
                videos: true,               // Новые видео
                notes: false,               // Новые комментарии в заметках
                gifts: false                // Новые подарки        
            }
        },
        menu: {                                      // Меню расширения
            profile:   { order: 0,  show: true },    // Профиль
            friends:   { order: 1,  show: true },    // Друзья
            photos:    { order: 2,  show: true },    // Фотографии
            videos:    { order: 3,  show: true },    // Видео
            music:     { order: 4,  show: true },    // Музыка
            messages:  { order: 5,  show: true },    // Сообщения
            groups:    { order: 6,  show: true },    // Группы
            news:      { order: 7,  show: true },    // Новости
            feedback:  { order: 8,  show: true },    // Ответы
            bookmarks: { order: 9,  show: true },    // Закладки
            settings:  { order: 10, show: true },    // Настройки
            mentions:  { order: 11, show: false },   // Упоминания
            notes:     { order: 12, show: false },   // Заметки
            gifts:     { order: 13, show: false },   // Подарки
            apps:      { order: 14, show: true },    // Приложения
            documents: { order: 15, show: true },    // Документы
            search:    { order: 16, show: false }    // Поиск
        }
    };

    this.getInjectionData = function (callback) {
        let injectionData = {
            settings: that.settings.vk,
            langData: that.lang_data.vk,
            welcomeMessage: null
        };

        let lastSavedVersion = C.ls_get('last_message_version'),
            messageType = lastSavedVersion ? (that.manifest.version != lastSavedVersion ? 'update' : null) : 'install';

        if (messageType == 'update' && !that.settings.common.show_welcome_msg) {
            that.markWelcomeMessageAsShown();
            callback(injectionData);
            return;
        }

        if (messageType) {
            $.ajax({
                url: chrome.extension.getURL('assets/locales/' + that.statics.langs[that.lang_id].code + '/' + messageType + '.html'),
                type: 'POST',
                dataType: 'HTML'
            }).success(function (message) {
                message = message
                    .replace(/[\n\t\r]/g, '')
                    .replace(/__ext_id__/g, chrome.runtime.id)
                    .trim();

                message && (injectionData.welcomeMessage = message);

                callback(injectionData);
            });
        } else {
            callback(injectionData);
        }
    };

    this.markWelcomeMessageAsShown = function () {
        C.ls_set('last_message_version', that.manifest.version);
    };

    this.onExternalMessage = function (request, sender, callback) {
        var action = request._action;
        delete request._action;

        switch (action) {
            case 'getInjectionData':
                that.getInjectionData(callback);
                return true;
            case 'welcomeMessageIsShown':
                that.markWelcomeMessageAsShown();
            case 'get_file_size': // old
                that.get_file_size(request.link, callback);
                return true;
            case 'getFileSize':
                that.get_file_size(request.url, callback);
                return true;  
            case 'downloadFile':
                that.download(request);
            case 'getUserAge':
                that.getUserAge(request, callback);
                return true;  
            case 'getShortUrl':
                that.getShortUrl(request.url, callback);
                return true;  
            default:
                callback({ error: 'Unknown action' });
        }
    };

    this.getShortUrl = function (url, callback) {
        API.request(
            'utils.getShortLink',
            {
                url,
                private: 1
            },
            function (data) {
                if (data.errorCode === 'notAuthorized') {
                    callback({ error: 'Для использования этой функции необходимо авторизоваться, кликнув на соответствующий пункт в меню расширения VK Flex.' });
                } else if (data.error && data.error.error_msg) {
                    callback({ error: data.error.error_msg });
                } else if (data.error) {
                    callback({ error: 'Неизвестная ошибка' });
                } else {
                    callback({ url: data.response.short_url });                    
                }
            }
        );
    };

    // Событие срабатывает при получении сообщения от других компонентов расширения
    // Выполнение отправки такого сообщение асинхронно
    this.onCoreMsg = function (request, sender, callback) {
        var a = request.action;
        callback = callback || function () {};

        // Пришёл запрос со страницы настроек для получения всех необходимых данных
        if (a == 'get_settings_page_data') {
            callback({
                settings: that.settings,
                lang_data: that.lang_data.settings,
                statics: that.statics
            });

        // Пришёл запрос со страницы настроек для сохранения новых настроек
        } else if (a == 'set_settings') {
            if (C.isObject(request.data)) {
                that.save_settings(request.data, callback);
            }

        // Пришёл запрос со страницы меню для получения всех необходимых данных
        } else if (a == 'get_menu_data') {
            var response = {
                vk_data: that.vk_data
            };

            if (request.isInit) {
                response.settings = that.settings.menu;
                response.lang_data = that.lang_data.menu;
            }

            // C.log(response);

            callback(response);

        // Пришёл запрос со страницы меню для получения всех необходимых данных
        } else if (a == 'get_vk_data') {
            // var wm = that.welcome_message();
                        
            callback({
                settings: that.settings.vk,
                lang_data: that.lang_data.vk,
                // lang_code: that.statics.langs[that.lang_id].code,
                // message: wm && that.settings.common.show_welcome_msg ? wm : false,
                obt: !C.ls_get('omnibox_tip_is_shown')
            });

        // Приветсвенное сообщение показано
        } else if (a == 'welcome_message_is_shown') {
            that.welcome_message(true);

        // Приветсвенное сообщение показано
        } else if (a == 'omnibox_tip_is_shown') {
            C.ls_set('omnibox_tip_is_shown', 'true');

        // Получает размер файла на сервере
        } else if (a == 'get_file_size') {
            that.get_file_size(request.link, callback);
            return true;

        // Скачивание файла
        /*} else if (a == 'download_file') {
            that.download(request.link, request.title);*/

        // Вернуть язык 
        } else if (a == 'get_vk_msg') {
            that.get_vk_msg(request.msg_key, callback);

        // Получить конкретную внешнюю ссылку
        } else if (a == 'get_external_link') {
            callback(that.external_links[request.link]);

        // Тест
        } else if (a == 'test') {
            callback(true);

        // Начать процесс авторизации
        } else if (a == 'auth') {
            User.auth();

        // Разавторизоваться
        } else if (a == 'logout') {
            User.logout();

        // Проверяет, авторизован ли юзер
        } else if (a == 'check_user') {
            callback({
                isAuthed: User.isAuthed(), 
                isSynced: User.isSynced()
            });
        } else {
            console.log('Unknown event');
        }
    };

    // API Вконтакте
    var API = {
        _version: '5.131',
        get_version: function () {
            return API._version;
        },
        request: function (method, data, callback) {
            callback = callback || function () {};

            if (!data.access_token) {
                if (User.isAuthed()) {
                    data.access_token = User.get_token();  
                } else {
                    return callback({
                        errorCode: 'notAuthorized',
                        error: 'User is not authorized'
                    });
                }
            }  

            data.v = API._version;

            $.ajax({
                method: 'POST',
                url: 'https://api.vk.com/method/' + method,
                data: data
            }).success(function (data) {
                callback(data);

                if (data.error) {
                    C.log('VK API request failed', data);
                }
            }).error(function () {
                callback({
                    error: 'Request error'
                });
            });
        }
    };

    // объект авторизации
    var User = {
        _synced: false,
        data: {
            token: null,
            id: null
        },
        get_id: function () {
            return User.data.id;
        },
        get_token: function () {
            return User.data.token;
        },
        set_synced: function (user_id) {
            User._synced = User.data.id == user_id;
            return true;
        },
        isAuthed: function () {
            return !!(User.data.id && User.data.token);
        },
        isSynced: function () {
            return User._synced;
        },
        init: function (callback) {
            // TODO: Create new menu layout 'loading...'
            callback = callback || function () {};            
            var user_data = C.ls_get('user_data', 'json', User.data, true);

            if (!user_data.token) {
                return callback();
            }

            API.request(
                'account.getInfo',
                {
                    access_token: user_data.token
                },
                function (data) {
                    if (!data.error) {
                        User.data = user_data;
                    }

                    callback();
                }
            );
        },
        auth: function () {
            // TODO: Remove revoke param in url
            chrome.windows.create({
                url: 'https://oauth.vk.com/authorize?client_id=4819086&display=popup&redirect_uri=https://oauth.vk.com/blank.html&scope=offline&response_type=token&v=' + API.get_version() + '&state=vkflex&revoke=1',
                focused: true,
                type: 'popup'
            }, function (auth_window) {
                chrome.tabs.onUpdated.addListener(function (tab_id, change_info, tab) {
                    if (auth_window.tabs[0].id == tab_id && /^(http|https):\/\/oauth.vk.com\/blank\.html/.test(tab.url)) {
                        var url = tab.url.split('#');

                        if (url.length == 2) {
                            var params = {};

                            url[1].split('&').forEach(function (param) {
                                param = param.split('=');
                                params[param[0]] = param[1] ? decodeURIComponent(param[1]) : null;
                            });

                            if (params.state == 'vkflex' && !params.error && params.access_token) {
                                User.data.id = parseInt(params.user_id, 10);
                                User.data.token = params.access_token;
                                C.ls_set('user_data', User.data, 'json');
                            }
                        }

                        if (change_info.status == 'complete') {
                            chrome.windows.remove(auth_window.id, function () {});
                        }
                    }
                });
            });
        },
        logout: function () {
            User.data.token = null;
            User.data.id = null;
            User.set_synced(false);
            C.ls_set('user_data', {}, 'json');
        }
    };

    this.getUserAge = function (options, callback) {
        API.request(
            'execute.getUserBirthday',
            {
                screenName: options.screenName
            },
            function (data) {
                callback(data.response);
            }
        );
    };

    // Получить текст локализации интерфейса ВК по ключу
    this.get_vk_msg = function (msg_key, callback) {
        var lang_id = that.vk_lang in that.vk_messages ? that.vk_lang : 0,
            msg = msg_key in that.vk_messages[lang_id] ? that.vk_messages[lang_id][msg_key] : '';

        callback(msg);
    };

    // Узнать размер файла на сервере
    this.get_file_size = function (link, callback, timeout) {
        if (link) {
            $.ajax({
                url: link,
                type: 'HEAD',
                timeout: (timeout || 30) * 1000
            }).success(function (data, status, xhrObj) {
                var size = xhrObj.getResponseHeader('Content-Length');
                if (size !== null) {
                    size = parseInt(size, 10);
                    if (isNaN(size)) {
                        size = null;
                    }
                }
                callback(size);
            }).error(function (xhrObj) {
                // C.error('Get file size error:', link.split('/').pop(), xhrObj.status, xhrObj.statusText);
                callback(null);
            });
        } else {
            // C.error('[Size] Link is not defined.');
            callback(null);
        }
    };

    // Скачивает файл
    this.download = function (options) {
        let anchor = document.createElement('a');
        anchor.href = options.href;
        options.download && (anchor.download = options.download);
        anchor.click();

        /*let clickEvent = document.createEvent('MouseEvents');
        clickEvent.initMouseEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);

        anchor.dispatchEvent(clickEvent);*/
    };

    // Событие срабатывает, если в поисковой строке браузера пользователь ввёл "vkf ..."
    this.onOmniboxQuery = function (query, tab_name) {
        chrome.tabs.update({  
            url: 'http://vk.com/audio?q=' + encodeURIComponent(query)
        });
    };

    // Если сделан клик по всплывающему уведомлению или по кнопкам в нём
    this.onNotificationClick = function (nid, bid) {
        // Если id кнопки (bid) не передан или bid == 0 ("Перейти к ВК"), то перейти к ВК
        if (bid !== 1) {
            chrome.tabs.create({
                url: 'http://vk.com/id0',
                selected: true
            }, function () {
                chrome.windows.getCurrent(function (wnd) {
                    if ('id' in wnd) {
                        chrome.windows.update(wnd.id, {
                            focused: true
                        }, function () {});
                    }
                });
            });
        }

        clearTimeout(that.notify_timer);
        chrome.notifications.clear(that.last_notify_id, function () {});
        that.last_notify_id = '';
    };

    // Во время закрытия уведомления
    this.onNotificationClose = function (nid, by_user) {
        clearTimeout(that.notify_timer);
        that.last_notify_id = '';
    };

    // Возвращает тип сообщения для пользователя
    // 'install', 'update', false
    /*this.welcome_message = function (disable) {
        // Получить текущую версию из манифеста
        var cur_ver = that.manifest.version;

        // Если отключить сообщение
        if (disable) {
            // Сохранить текущую версию расширения
            C.ls_set('last_message_version', cur_ver);

        // Если нужно вернуть тип сообщения
        } else {
            // Получить предыдущую версию расширения
            var last_ver = C.ls_get('last_message_version');

            // Вернуть false (не пок. сообщ), 'update' (сообщ. после обнов.), 'install' (сообщ. после установ.)
            return last_ver ? (cur_ver == last_ver ? false : 'update') : 'install';
        }
    };*/

    // Устанавливает счётчик
    this.set_badge = function (cnt) {
        chrome.browserAction.setBadgeText({text: cnt.toString()});
    };

    // Убирает счётчик
    this.remove_badge = function () {
        chrome.browserAction.setBadgeText({text: ''});
    };

    // Выполняет обращение к ВК
    this.vk_check = function () {
        // Запрос к серверу ВК
        $.ajax({
            url: 'https://vk.com/feed2.php',
            type: 'POST',
            dataType: 'JSON'
        }).success(function (data) {
            // Если запрос делался для получения языка, установить язык
            if (data.lang && ('id' in data.lang)) {
                var new_vk_lang = parseInt(data.lang.id, 10);
                if (new_vk_lang != that.vk_lang) {
                    that.vk_lang = new_vk_lang;
                    C.ls_set('vk_lang', that.vk_lang);
                    that.get_language();
                }
            }

            // Если пользователь авторизован в расширении и в ВК, и id пользователя совпадают
            if (data.user && data.user.id && data.user.id !== -1 && User.set_synced(data.user.id) && User.isSynced()) {
                chrome.browserAction.setIcon({
                    path: {
                        "16":  "/assets/images/icons/icon16.png",
                        "32":  "/assets/images/icons/icon32.png",
                        "48":  "/assets/images/icons/icon48.png",
                        "128": "/assets/images/icons/icon128.png"
                    }
                });

                chrome.browserAction.setTitle({
                    title: 'VK Flex'
                });

                var events = that.settings.notifications.events, // Список событий из настроек
                    total = 0,                                   // Общий счётчик
                    new_counters = {},                           // Новый объект с данными ВК
                    count,                                       // Счётчик текущего события, пришедший из ВК
                    popup = [],                                  // Массив объектов для всплывающего уведомления
                    sound = false;                               // Нужно ли звуковое уведомление

                // Перебрать все события из настроек
                for (var e in events) {
                    // Если уведомление по текущему событию включено и счётчик по этому событию получен
                    if (events[e] && (e in data) && ('count' in data[e])) {
                        // Обработать присланный счётчик события
                        count = parseInt(data[e].count, 10);

                        // Если события есть
                        if (count) {
                            // Добавить счётчик этого события в объект событий
                            new_counters[e] = count;

                            // Прибавить к общему счётчику
                            total += count;

                            // Если пользователь уже был уведомлён об этих событиях, то обнулить счётчик
                            if (e in that.vk_data.counters) {
                                count = that.vk_data.counters[e] < count ? (count - that.vk_data.counters[e]) : 0;
                            }

                            // Если есть события, о которых пользователь не был уведомлён
                            if (count) {
                                // Необходимо звуковое уведомление
                                sound = true;

                                // Добавить событие в массив уведомлений
                                popup.push({
                                    title: that.lang_data.demon['en_e_' + e] + ': ',
                                    message: '+' + count
                                });                                    
                            }
                        }
                    }
                }

                // Если включено всплывающе уведомление и уведомления есть
                if (that.settings.notifications.popup && popup.length) {
                    // Убрать таймер скрытия уведомления
                    clearTimeout(that.notify_timer);

                    // Передать в замыкание данные об уведомлении
                    (function (popup) {
                        // Очистить последнее уведомление
                        chrome.notifications.clear(that.last_notify_id, function () {
                            //Создать случайный id для уведомления
                            that.last_notify_id = Math.random().toString();

                            // Показать уведомление 
                            chrome.notifications.create(
                                that.last_notify_id,
                                {  
                                    type: 'list', 
                                    items: popup,
                                    buttons: [
                                        {
                                            title: that.lang_data.demon['en_go_to_vk'],
                                            iconUrl: '/assets/images/demon/notification_icon_vk.png'
                                        },
                                        {
                                            title: that.lang_data.demon['en_close'],
                                            iconUrl: '/assets/images/demon/notification_icon_close.png'
                                        }
                                    ],
                                    message: '',
                                    iconUrl: '/assets/images/demon/notification_logo.png', 
                                    title: that.lang_data.demon['en_title']
                                },
                                function (nid) {
                                    // Поставить таймер скрытия уведомления
                                    that.notify_timer = setTimeout(function () {
                                        chrome.notifications.clear(that.last_notify_id, function () {});
                                        that.last_notify_id = '';
                                    }, 6000);
                                }
                            );
                        });
                    })(popup);
                }

                // Если включено всплывающе уведомление и если есть звук уведомления и если нужно звуковое уведомление
                if (that.settings.notifications.sound !== false && that.sound && sound) {
                    that.sound.play();
                }

                // Если включен общий счётчик и он больше нуля, то показать его, в противном случае скрыть
                if (that.settings.notifications.counter && total) {
                    that.set_badge(total > 999 ? '999+' : total);
                } else {
                    that.remove_badge();                       
                }

                //Установыть новый объект с данными событий
                that.vk_data = {
                    status: 'ready',
                    counters: new_counters
                };

            // Если уведомления по всем событиям отключены в настройках, сделать объект событий пустым
            } else {
                chrome.browserAction.setIcon({
                    path: {
                        "16":  "/assets/images/icons/icon16gs.png",
                        "32":  "/assets/images/icons/icon32gs.png",
                        "48":  "/assets/images/icons/icon48gs.png",
                        "128": "/assets/images/icons/icon128gs.png"
                    }
                });

                chrome.browserAction.setTitle({
                    title: that.lang_data.demon['need_auth']
                });

                that.remove_badge(); 

                that.vk_data = {
                    status: 'need_auth',
                    counters: {}
                };

            }

        // Если ошибка
        }).error(function () {
            that.vk_data.status = 'ready';
            // В случае ошибки сбрасывать that.vk_data.counter не нужно, считается, что счётчики не обновлялись 

        // Когда все предыдущие функции выполнены          
        }).complete(function () {
            update_timer = setTimeout(that.vk_check, that.statics.update_delays[that.settings.common.update_delay]);
        });
    };

    // [Async] Возвращает всю локализацию ввиде json
    this.get_language = function (callback) {
        var new_lang_id = that.settings.common.language === 'vk' ? (C.isInteger(that.vk_lang) && (that.vk_lang in that.statics.langs) ? that.vk_lang : 0) : that.settings.common.language;

        if (new_lang_id != that.lang_id) {
            that.lang_id = new_lang_id;

            C.log('Lang:', that.lang_id);

            $.ajax({
                url: '/assets/locales/' + that.statics.langs[that.lang_id].code + '/lang.json',
                type: 'POST',
                dataType: 'JSON'
            }).success(function (data) {
                that.lang_data = data;
                if (callback) {
                    callback();
                }
            });
        } else {
            if (callback) {
                callback();
            }
        }
    };

    // [Async] Получает настройки из localStorage
    this.get_settings = function (callback) {
        that.settings = C.ls_get('settings', 'json', that.defaults, true);
        that.vk_lang = C.ls_get('vk_lang', 'integer', null);
        that.get_language(callback);
    };

    // [Async] Обновляет объект с настройками в этом классе
    // Аругменты:
    // data (не обязательный) - объект с новыми настройками
    // callback (не обязательный) - функция, выполняема после сохранения и применения новых настроек
    this.save_settings = function (a0, a1) {

        // Если пришёл объект с новыми настройками, смержить их с дефолтными
        if (C.isObject(a0)) {
            that.settings = C.objects_merge([that.defaults, a0], true, 'left');
        }

        // Создать коллбек
        var callback = C.isFunction(a0) ? a0 : (C.isFunction(a1) ? a1 : function () {});

        // Сохранить полученные настройки в LS
        C.ls_set('settings', that.settings, 'json');
        
        // Считать языковой файл, применить новые настройки и язык к демону и выполнить коллбэк
        that.get_language(function () {
            that.apply_settings();
            callback();
        });
    };

    // Функция применяет новые настройки в демоне
    this.apply_settings = function () {
        // Очистить текущий таймер
        clearTimeout(update_timer);

        // Установить новый звук
        if (that.settings.notifications.sound === false) {
            that.sound = null;
        } else {
            that.sound = document.createElement('audio');
            that.sound.src = ('/assets/sounds/notify_sound_' + that.settings.notifications.sound + '.mp3');
        }

        // Запустить первый запрос к ВК
        that.vk_check(); 
    };

    // Начало инициализации
    init();
}

// Запуск демона
vkf_demon = new VKFlexDemon();

})(jQuery);


/*
const checkTab = (tab) => {
    const patterns = [
        /^https?:\/\/(([A-Z\d\-]+)\.)*vk\.com\/lentach1/i
    ];

    for (let pattern of patterns) {
        if (pattern.test(tab.url)) {
            const url = new URL(tab.url);

            chrome.tabs.update(tab.id, {
                url: url.origin + '/id0'
            });
        }
    }
};

chrome.tabs.query({}, (tabs) => {
    tabs.forEach((tab) => checkTab(tab));
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.url) {
        checkTab(tab);
    }
});
*/