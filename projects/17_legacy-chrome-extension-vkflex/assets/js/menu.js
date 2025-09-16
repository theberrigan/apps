// VK Flex Chrome Extension: menu.js
// Dependencies: jQuery.js, common.js

// Объект управления страницей настроек
var vkf_menu;

// Нэймспейс, где $ == jQuery
(function ($) {

// Объект управления страницей настроек
function VKFlexMenu () {

    // Private свойства
    var that = this,
        B = $('body'),
        C = vkf_common,
        D = $(document),
        W = $(window),
        menu_items = $('.menu-items');

    // Текущие настройки
    this.settings = {};

    // Информация о счётчиках
    this.vk_data = {};

    // JSON со всеми i18n-строками секции "settings"
    this.lang_data = {};

    // Слои
    this.layouts = {};

    // Текущий слой
    this.current_layout = null;

    // Счётчики
    this.badges = {};

    // Данные о пунктах меню
    this.menu_data = {
        profile:   { link: '/id0', counter: false },
        friends:   { link: '/friends', counter: 'friends' },
        photos:    { link: '/albums', counter: 'photos' },
        videos:    { link: '/video', counter: 'videos' },
        music:     { link: '/audio', counter: false },
        messages:  { link: '/im', counter: 'messages' },
        groups:    { link: '/groups', counter: 'groups' },
        news:      { link: '/feed', counter: false },
        feedback:  { link: '/feed?section=notifications', counter: 'mentions' },
        bookmarks: { link: '/fave', counter: false },
        settings:  { link: '/settings', counter: false },
        mentions:  { link: '/feed?section=mentions', counter: false },
        notes:     { link: '/notes', counter: 'notes' },
        gifts:     { link: '/gifts', counter: 'gifts' },
        apps:      { link: '/apps', counter: false },
        documents: { link: '/docs', counter: false },
        search:    { link: '/search', counter: false }
    };

    // Циклично получает данные из ядра
    this.update = function (isInit) {
        // Асинхронное получение настроек из ядра 
        that.get_core_data(function () {  
            // Если инииализация
            if (isInit) {
                // Локализация интерфейса
                that.i18n();

                // Инициализация слоёв
                that.init_layouts();

                // Инициализация меню
                that.init_menu();

                // Клик по кнопке авторизации
                $('#auth').on('click', that.auth);
            } else {
                // Если текущий слой - меню, то нужно обновить данные. Остальные слои статичные, их обновлять не нужно
                if (that.vk_data.status == 'ready') {
                    that.update_menu();
                }
            }

            // Включить нужный слой
            that.switch_layout();

            // Снова запускает обновление данных через 500 мс
            setTimeout(that.update, 100);
        }, isInit);
    };

    // инициировать авторизацию
    this.auth = function (e) {
        that.coreMsg({
            action: 'auth'
        });
        return false;
    };

    // инициировать авторизацию
    this.logout = function (e) {
        that.coreMsg({
            action: 'logout'
        });
        return false;
    };

    // Отправляет сообщение в ядро расширения
    this.coreMsg = function (data, callback) {
        chrome.runtime.sendMessage(data, callback);
    };

    // Получает настройки и после этого выполняет переданную функцию
    this.get_core_data = function (callback, isInit) {
        that.coreMsg({
            action: 'get_menu_data',
            isInit: isInit ? true : false
        }, function (data) {
            if (data) {
                that.vk_data = data.vk_data;
                if (isInit) {
                    that.settings = data.settings;
                    that.lang_data = data.lang_data;
                } 
                callback();
            } else {
                alert('Runtime error #1.');
                window.close();
            }
        });
    };

    // Инициализация слоёв
    this.init_layouts = function () {
        $('.layout').each(function () {
            var layout = $(this),
                status = layout.attr('data-status');

            that.layouts[status] = layout;
        });
    };

    // Переключить слой на нужный
    this.switch_layout = function () {
        if (that.current_layout != that.vk_data.status) {
            if (that.current_layout) {
                that.layouts[that.current_layout].removeClass('shown');
            }
            that.layouts[that.vk_data.status].addClass('shown');
            that.current_layout = that.vk_data.status;
        }
        // that.layouts['loading'].addClass('shown');
    };

    // Инициализация меню
    this.init_menu = function () {
        var items = [],
            badge,
            counter_name;

        for (var menu_item in that.settings) {
            if (menu_item in that.menu_data) {
                counter_name = that.menu_data[menu_item].counter;
                if (counter_name === false) {
                    badge = '';
                } else {
                    if (counter_name in that.vk_data.counters) {
                        badge = ('<span class="badge shown" id="badge_' + menu_item + '">' + that.vk_data.counters[counter_name] + '</span>');
                    } else {
                        badge = ('<span class="badge" id="badge_' + menu_item + '">0</span>');
                    }
                }
                items[that.settings[menu_item].order] = ('<li' + (that.settings[menu_item].show ? ' class="shown"' : '') + '> \
                                                            <a target="_blank" href="http://vk.ru' + that.menu_data[menu_item].link + '">'
                                                                 + badge + 
                                                                '<span class="label">' + that.lang_data['mi_' + menu_item] + '</span> \
                                                            </a> \
                                                        </li>');
            }
        }

        items.push('<li class="shown"> \
                        <a target="_blank" href="#" id="logout"> \
                            <span class="label">' + that.lang_data['mi_logout'] + '</span> \
                        </a> \
                    </li>');

        menu_items.html(items.join('')); 

        $('#logout').on('click', that.logout);
    };

    // Обновить меню
    this.update_menu = function () {
        var badge,
            badge_obj,
            counter_name;

        for (var menu_item in that.settings) {
            counter_name = that.menu_data[menu_item].counter;
            if (menu_item in that.menu_data && counter_name !== false) {
                if (menu_item in that.badges) {
                    badge_obj = that.badges[menu_item];
                } else {
                    badge_obj = $('#badge_' + menu_item);
                    that.badges[menu_item] = badge_obj;
                }

                if (counter_name in that.vk_data.counters) {
                    badge_obj.text(that.vk_data.counters[counter_name].toString()).addClass('shown');
                } else {
                    // C.log('Hide', badge_obj);
                    badge_obj.text('0').removeClass('shown');
                }
            }
        }
    };

    // Функция локализации интерфейса
    this.i18n = function () {
        var items = $('[data-i18n]');
        items.each(function () {
            var item = $(this),
                key = item.attr('data-i18n');

            if (key in that.lang_data) {
                item.html(that.lang_data[key]);
            }
        });
    };

    // Запускает обновление данных с инициализацией
    that.update(true);
}

// Когда DOM и демон готовы, запуск скрипта
$(document).ready(function () {
    var demon = chrome.extension.getBackgroundPage();

    (function check_demon_ready () {
        if (demon.isSettingsReady) {
            vkf_menu = new VKFlexMenu();
        } else {
            setTimeout(check_demon_ready, 20);
        }
    })();
});


})(jQuery);