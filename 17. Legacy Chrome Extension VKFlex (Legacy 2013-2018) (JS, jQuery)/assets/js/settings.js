// VK Flex Chrome Extension: settings.js
// Dependencies: jQuery.js, common.js

// Объект управления страницей настроек
var vkf_settings;

// Нэймспейс, где $ == jQuery
(function ($) {

// Объект управления страницей настроек
function VKFlexSettings () {

    // Private свойства
    var that = this,
        B = $('body'),
        C = vkf_common,
        D = $(document),
        W = $(window),
        isNeedRefreshTabs = false,
        content = $('.content'),
        settings_saved = $('.settings-saved'),
        sound_play_button = $('.sound-play'),
        notification_sound = $('#notifications--sound');

    // Инициализация объекта
    var init = function () {
        // Асинхронное получение настроек из ядра 
        that.init_settings(function () {  
            // Инициализация звуков 
            that.init_sounds();

            // Инициализация интерфейса
            that.UI();

            // Локализация интерфейса
            that.i18n();

            // Установить внешние ссылки
            that.init_links();

            // Донат
            $('#icon-dt').on('click', that.donate);

            // Бинд "поделиться в ВК"
            $('#icon-sh a').on('click', function (e) {
                e.preventDefault();
                e.stopPropagation();

                window.open(this.href, 'share_popup', 'width=700,height=500,toolbar=0,menubar=0,location=1,status=1,scrollbars=1,resizable=1,left=0,top=0');
            });

            // Если в LS есть флаг, что необходимо обновить все вкладки ВК,
            // то этот флаг необходимо убрать и показать сообщение об этой необходимости
            if (C.ls_get('settings_need_refresh_tabs')) {
                isNeedRefreshTabs = true;
                C.ls_remove('settings_need_refresh_tabs');
                that.check_vk_tabs();
            }
        });
    };

    // Статичные данные
    this.statics = {};

    // Текущие настройки
    this.settings = {};

    // JSON со всеми i18n-строками секции "settings"
    this.lang_data = {};

    // Массив со звуками
    this.sounds = [];

    // Управление всплывающим окном доната
    this.donate = function (e) {
        B.toggleClass('isDonate');
    };

    // Отправляет сообщение в ядро расширения
    this.coreMsg = function (data, callback) {
        chrome.runtime.sendMessage(data, callback);
    };

    // Получает настройки и после этого выполняет переданную функцию
    this.init_settings = function (callback) {
        that.coreMsg({
            action: 'get_settings_page_data'
        }, function (data) {
            C.log('Received core data:', data);
            if (('settings' in data) && ('lang_data' in data) && ('statics' in data)) {
                that.settings = data.settings;
                that.lang_data = data.lang_data;
                that.statics = data.statics;
                callback();
            } else {
                alert('Runtime error #1.');
                window.close();
            }
        });
    };

    // Установить внешние ссылки
    this.init_links = function () {
        $('[data-link]').each(function () {
            var item = $(this);

            that.coreMsg({
                action: 'get_external_link',
                link: item.attr('data-link')
            }, function (link) {
                item.attr('href', link);
            });
        });
    };

    // Функция инициализации звуков
    this.init_sounds = function () {
        if (that.statics.sounds) {
            for (var i = 0; i < that.statics.sounds; i++) {
                that.sounds[i] = document.createElement('audio');
                that.sounds[i].src = ('/assets/sounds/notify_sound_' + i + '.mp3');
            }
        }
    };

    // Скрывает и показывает панель "Нужно обновление вкладок ВК"
    this.settings_saved_visibility = function (action) {
        B[action == 'show' ? 'addClass' : 'removeClass']('ss-shown');
    };

    // "Перерисовывает" панель "Нужно обновление вкладок ВК"
    this.settings_saved_redraw = function (e) {
        var bottom = D.scrollTop() + W.height() - content.offset().top - content.height() - settings_saved.outerHeight();
        settings_saved.css('bottom', Math.max(0, bottom) + 'px');
        B[bottom > -10 ? 'addClass' : 'removeClass']('ss-pinned');  
    };

    // Выполняет мгновенное обновление страницы настроек при изменении некоторых параметров (например, языка)
    this.permanent_refresh = function () {
        if (isNeedRefreshTabs) {
            C.ls_set('settings_need_refresh_tabs', 'true');
        }
        location.reload();
    };

    // Передаёт функции callback массив с id вкладок с ВК
    this.get_vk_tabs = function (callback) {
        chrome.tabs.query({ url: '*://*.vk.com/*' }, callback);        
    };

    // Обновляет все вкладки с ВК
    this.reload_vk_tabs = function () {
        that.get_vk_tabs(function (tabs) {
            for (var i in tabs) {
                chrome.tabs.reload(tabs[i].id);
            }
            isNeedRefreshTabs = false;
            that.settings_saved_visibility('hide');
        });
    };

    // Проверяет нужно ли обновление вкладок с ВК
    // ДА - когда isNeedRefreshTabs == true и есть вкладки с ВК. НЕТ - когда isNeedRefreshTabs == false или нет вкладок с ВК
    this.check_vk_tabs = function () {
        that.get_vk_tabs(function (tabs) {
            that.settings_saved_visibility(tabs.length && isNeedRefreshTabs ? 'show' : 'hide');
        });
    };

    // Проверяет, нужно ли длеать кнопку восп. звука активной
    this.sound_button_visibility = function (value) {
        sound_play_button[value === false ? 'addClass' : 'removeClass']('disabled');
    };

    // Воспроизведение текущего звука уведомления
    this.sound_play = function () {
        if (that.settings.notifications.sound !== false) {
            that.sounds[that.settings.notifications.sound].play();
        }
    };

    // Срабатывает при изменении полей формы
    this.onFormChange = function (e) {
        var input = $(e.target),
            id = input.attr('id'),
            ids = id.split('--'),
            type = input.attr('type'),
            value;

        // Для преобразования некоторых типов
        var values_conversion = {
            'false': false,
            'true': true
        };

        // Получаем значение в зависимости от типа поля
        if (C.inArray(type, ['hidden', 'text', 'password'])) {
            value = input.val();
        } else if (C.inArray(type, ['checkbox', 'radio'])) {
            value = input.is(':checked');
        }

        // Если получено значение
        if (!C.isUndefined(value)) {

            // Преобразовать тип, если нужно
            if (C.isString(value)) {
                var value_cmp = value.toLowerCase();

                // Через массив преобразования типов
                if (value_cmp in values_conversion) {
                    value = values_conversion[value_cmp];

                // Отпарсить как целое чило, если в строке только цифры
                } else if (C.isNum(value)) {
                    value = parseInt(value, 10);
                }
            }

            // Если меню
            if (ids[0] == 'menu') {
                if (ids[1]) {
                    that.settings.menu[ids[1]].show = value;

                } else {
                    value = value.split(';');
                    for (var i = 0; i < value.length; i++) {
                        that.settings.menu[value[i]].order = i;
                    }
                }

            // Если звук
            } else if (id == 'notifications--sound') {
                that.settings.notifications.sound = value;
                that.sound_button_visibility(value);
                that.sound_play(); 

            // Все остальные настройки                         
            } else {
                // Рекурсивное прохождение по ключам объекта настроек
                (function walker (obj, idx) {
                    if (ids[idx] in obj) {
                        if ((ids.length - 1) == idx) {
                            obj[ids[idx]] = value;
                        } else {
                            walker(obj[ids[idx]], ++idx);
                        }
                    }                            
                })(that.settings, 0);
            }

            // Отправка настроек в ядро для сохранения
            that.coreMsg({
                action: 'set_settings',
                data: that.settings
            }, function () {
                // Определяет нужно ли обновление вкладок с ВК
                isNeedRefreshTabs = isNeedRefreshTabs || !C.isUndefined(input.attr('data-refresh-tabs'));

                // После всех манипуляций со значением поля
                // если нужно перманентное обновление
                if (!C.isUndefined(input.attr('data-permanent-refresh'))) {
                    that.permanent_refresh();
                } else {
                    that.check_vk_tabs();
                }
            });
        }
    };

    // Устанавливает настройки по умолчанию
    this.set_default_settings = function () {
        if (confirm(that.lang_data['confirm_defaults'])) {
            // Отправка настроек в ядро для сохранения
            // В ядро отправляется пустой объект настроек. Тогда при их сохранении этот объект будет заполнен дефолтами
            that.coreMsg({
                action: 'set_settings',
                data: {}
            }, function () {
                // Обязательно обновить вкладки с ВК
                isNeedRefreshTabs = true;

                // Обновление страницы настроек
                that.permanent_refresh();
            });            
        }
    };

    // Инициализирует интерфейс и выставляет значения
    this.UI = function () {

        // Элементы списка для "Меню пользователя"
        var user_menu_list = [];

        // Функция инициализации "Меню пользователя"
        var init_user_menu = function () {
            var item_height = 51,                         // Высота элемента списка
                menu_list = $('.menu-list'),              // Главный родительский объект
                menu_list_items = $('.menu-list-items'),  // Родителский объект для элементов списка
                input = menu_list.find('input#menu'),     // Инпут, в котором хранится порядок итемов    
                menu_list_height,                         // Отступ сверху текущего элемента списка
                value = [];                               // id элементов списка в нужном порядке

            // Отсортировать список пунктов меню
            user_menu_list.sort(function (a, b) {
                return a.order < b.order ? -1 : (a.order > b.order ? 1 : 0);
            });

            // Добавление элементов списка
            for (var i = 0; i < user_menu_list.length; i++) {
                value.push(user_menu_list[i].id);
                menu_list_height = item_height * i;
                menu_list_items.append(
                    '<div class="menu-list-item" data-index="' + i + '" style="top: ' + menu_list_height + 'px;"> \
                        <div class="menu-list-item-drag"></div> \
                        <div class="menu-list-item-data"> \
                            <input type="checkbox" id="menu--' + user_menu_list[i].id + '"' + (user_menu_list[i].value ? ' checked="checked"' : '') + ' data-form-input="true"> \
                            <label for="menu--' + user_menu_list[i].id + '" class="ns"> \
                                <div class="cbx"></div> \
                                <div class="cbx-lbl">' + that.lang_data['user_menu_' + user_menu_list[i].label] + '</div> \
                            </label> \
                        </div> \
                    </div>'
                ).append('<div class="menu-list-fake-item"></div>');                       
            }

            // Установить текущее значение
            input.val(value.join(';'));

            // В этом объекте хранятся данные перемещаемого в данный момент элемента списка
            var item = {};

            // Добавление событий
            B.on('mousedown', '.menu-list-item', function (e) {
                if ($(e.target).hasClass('menu-list-item-drag')) {
                    item.obj = $(this).addClass('menu-list-item-no-transition');    // Текущий элемент списка
                    item.itemY = e.pageY - item.obj.offset().top;                   // Y-координата курсора относительно верха текущего элемента списка
                    item.current_idx = parseInt(item.obj.attr('data-index'), 10);   // Текущий индекс по атрибуту 'data-index'
                    item.last_idx = item.current_idx;                               // Сначала последний индекс равен текущему индексу элемента списка
                }
            }).on('mouseup', function (e) {
                if (item.obj) {
                    item.obj.removeClass('menu-list-item-no-transition')
                            .css('top', item_height * item.current_idx + 'px');
                    item = {};

                    var items = menu_list_items.find('.menu-list-item'),
                        value = [];

                    items.each(function () {
                        var item = $(this),
                            index = parseInt(item.attr('data-index'), 10),
                            id = item.find('input').attr('id').split('--')[1];

                        value[index] = id;
                    });

                    value = value.join(';');

                    if (value != input.val()) {
                        input.val(value).trigger('change');  
                    }                  
                }
            }).on('mousemove', function (e) {
                if (item.obj) {
                    var Ymin = menu_list_items.offset().top + item.itemY,
                        poh = menu_list_items.outerHeight(),
                        top = Math.min(Ymin + poh - item_height, Math.max(Ymin, e.pageY)) - Ymin;

                    item.obj.css('top', top + 'px');

                    item.current_idx = Math.round((top + item_height) / item_height) - 1;

                    if (item.current_idx != item.last_idx) {
                        var swap_item = $('.menu-list-item[data-index="' + item.current_idx + '"]');
                        swap_item.attr('data-index', item.last_idx).css('top', item_height * item.last_idx);
                        item.obj.attr('data-index', item.current_idx);
                        item.last_idx = item.current_idx;
                    }

                    e.preventDefault();
                }
            });
        };

        // Функция инициализации слайдера частоты обновлений
        var init_update_delays_slider = function () {
            var slider = null,
                parent = null,
                value = 0,
                points = [],
                range = $('.range'),
                input = range.find('input'),
                rail_width = range.width();
            
            var max_point_width = 0,
                point_outer_width;

            var time_format = function (ms) {
                var result;
                ms = ms / 1000;

                if (ms < 60) {
                    result = ms + ' ' + that.lang_data['time_sec'];
                } else {
                    result = (ms % 60 ? (ms / 60).toFixed(1) : parseInt(ms / 60, 10)) + ' ' + that.lang_data['time_min'];
                }

                return result;
            };

            for (var i = 0; i < that.statics.update_delays.length; i++) {
                points[i] = $('<div class="range-point">' + time_format(that.statics.update_delays[i]) + '</div>');
                range.append(points[i]);
                point_outer_width = points[i].outerWidth();
                if (max_point_width < point_outer_width) {
                    max_point_width = point_outer_width;
                }
            }

            range.css('margin-right', max_point_width / 2 + 'px');

            var space_width = Math.max(0, (rail_width - max_point_width * (points.length - 1)) / (points.length - 1));

            for (var i = 0; i < points.length; i++) {
                points[i].css({
                    left: (space_width + max_point_width) * i - max_point_width / 2,
                    width: max_point_width
                });
            }

            value = parseInt(input.val(), 10);
            range.find('.range-slider')
                 .css('left', range.outerWidth() / (points.length - 1) * (isNaN(value) ? 0 : value))
                 .removeClass('hidden');

            B.on('mousedown mouseup', function (e) {
                var t = $(e.target);
                if (e.type == 'mousedown') {
                    if (t.hasClass('range-slider')) {
                        last_value = value;
                        slider = t;
                        parent = t.parent();                        
                    }
                } else {
                    if (slider && input.val() != value) {
                        input.val(value).trigger('change');
                    }
                    slider = null;
                    parent = null;
                }

            }).on('mousemove', function (e) {
                if (slider) {
                    var Xmin = parent.offset().left,
                        pow = parent.outerWidth(),
                        ppp = pow / (points.length - 1); // pixels per point

                    value = Math.round((Math.min(Xmin + pow, Math.max(Xmin, e.pageX)) - Xmin) / ppp);

                    slider.css('left', value * ppp + 'px');
                    e.preventDefault();
                }
            });
        };

        // Функция инициализации дропдаунов
        var init_dropdowns = function () {
            $('.dropdown').each(function () {
                var dropdown = $(this),
                    item = dropdown.find('li[data-value="' + dropdown.find('input').val() + '"]');

                if (item.length) {
                    dropdown.find('.dropdown-label').html(item.html()); 
                }       
            });

            // Показ, скрытие и изменение значений дропдаунов
            B.on('click', '.dropdown-label, .dropdown-arrow, .dropdown-list li', function (e) {
                var toggler = $(this),
                    dropdown = toggler.closest('.dropdown');

                if (toggler.is('.dropdown-list li')) {
                    var value = toggler.attr('data-value'),
                        input = dropdown.find('input');

                    if (value != input.val()) {
                        dropdown.find('.dropdown-label').html(toggler.html());
                        input.val(value).trigger('change');
                    }
                }

                if (!dropdown.hasClass('opened')) {
                    $('.dropdown.opened').removeClass('opened');
                }

                dropdown.toggleClass('opened');

            // Скрыть все дропдауны, если клик был не внутри какого-то из них
            }).on('mousedown', function (e) { 
                if (!$(this).hasClass('.dropdown') && !$(e.target).closest('.dropdown').length) {
                    $('.dropdown.opened').removeClass('opened');
                }
            });

            // Скролер для меню дропдаунов
            $(".dropdown-items").nanoScroller({ 
                alwaysVisible: true,
                contentClass: 'dropdown-list',
                paneClass: 'dropdown-scroll-rail',
                sliderClass: 'dropdown-scroll-slider'
            });
        };

        // Функция устанавливает элементы списков дропдаунов
        var set_dropdown = function (list, id, value) {
            var input = $('#' + id);

            if (input) {
                var dropdown = input.closest('.dropdown'),
                    items = dropdown.find('.dropdown-list');

                input.val(value);

                for (var i in list) {
                    items.append('<li data-value="' + list[i].value + '"' + (i % 2 ? '' : ' class="odd"') + '>' + list[i].label + '</li>');
                }
            }
        };

        // Расстановка настроек по своим местам
        for (var sect in that.settings) {
            // Перебор вс
            for (var opt in that.settings[sect]) {
                if (sect == 'menu') {
                    user_menu_list.push({
                        id: opt, 
                        order: that.settings[sect][opt].order, 
                        value: that.settings[sect][opt].show, 
                        label: opt
                    });

                } else {
                    var id = (sect + '--' + opt),
                        val = that.settings[sect][opt];

                    // Если язык
                    if (id == 'common--language') {
                        var list = [];

                        if (that.statics.langs) {
                            for (var j in that.statics.langs) {
                                list.push({value: j, label: that.statics.langs[j].label});
                            }

                            list.sort(function (a, b) {
                                if (a.value == 'vk') {
                                    return -1;
                                } else if (b.value == 'vk') {
                                    return 1;
                                } else {
                                    return a.value < b.value ? -1 : (a.value > b.value ? 1 : 0);
                                }
                            });

                            set_dropdown(list, id, val); 
                        }

                    // Если частота обновлений
                    } else if (id == 'common--update_delay') {
                        $('#' + id).val(val);

                    // Если инфо об аудио
                    } else if (id == 'vk--audio_info') {
                        set_dropdown([
                            {value: 0, label: that.lang_data['dropdown_audio_info_disable']},
                            {value: 1, label: that.lang_data['dropdown_audio_info_bras']},
                            {value: 2, label: that.lang_data['dropdown_audio_info_br']},
                            {value: 3, label: that.lang_data['dropdown_audio_info_s']}
                        ], id, val);

                    // Если звук уведомления
                    } else if (id == 'notifications--sound') {
                        var list = [
                            {value: false, label: that.lang_data['dropdown_notifications_sound_disable']}/*,
                            {value: 'custom', label: that.lang_data['dropdown_notifications_sound_custom']}*/
                        ];

                        if (that.statics.sounds) {
                            for (var j = 0; j < that.statics.sounds; j++) {
                                list.push({value: j, label: that.lang_data['dropdown_notifications_sound_sound'] + ' #' + (j + 1)});
                            }

                            set_dropdown(list, id, val); 

                            that.sound_button_visibility(val);                   
                        }

                    // Если новые события
                    } else if (id == 'notifications--events') {
                        for (var j in val) {
                            if (val[j]) {
                                $('#' + id + '--' + j).attr('checked', 'checked');
                            }
                        }

                    // Чекбоксы, находящиеся сразу в секции
                    /*} else if (id == 'vk--fchat_size_control') {
                        set_dropdown([
                            {value: 0, label: that.lang_data['dropdown_fchat_control_disable']},
                            {value: 1, label: that.lang_data['dropdown_fchat_control_fit']},
                            {value: 2, label: that.lang_data['dropdown_fchat_control_remember']}
                        ], id, val);*/

                    // Если управление окном мини-чата
                    } else {
                        if (val) {
                            $('#' + id).attr('checked', 'checked');
                        }
                    }
                }
            }
        }

        // Инициализация "Меню пользователя"
        init_user_menu();

        // Инициализация слайдера частоты обновлений
        init_update_delays_slider();

        // Инициализация всех дропдаунов
        init_dropdowns();

        // Перерисовка кнопки "Обновить вкладки"
        W.on('scroll resize', that.settings_saved_redraw);

        // События изменения формы
        D.on('change', '[data-form-input]', that.onFormChange);

        // Воспроизвести текущий звук уведомления
        sound_play_button.on('click', that.sound_play);

        // При клике на кнопку "Обновить вкладки"
        $('#reload_vk_tabs').on('click', that.reload_vk_tabs);

        // При клике на кнопку "Обновить вкладки"
        $('.default-settings').on('click', that.set_default_settings);
    };

    // Функция локализации интерфейса
    this.i18n = function () {
        $('[data-i18n]').each(function () {
            var item = $(this),
                keys = item.attr('data-i18n').split(',');

            keys.forEach(function (key) {
                key = key.split(':');
                var attr = key.length == 2 ? key[0] : null;
                key = key.pop();

                if (key in that.lang_data) {
                    if (attr) {
                        item.attr(attr, that.lang_data[key]);
                    } else {
                        item.html(that.lang_data[key]);
                    }
                }
            });
        });
    };

    init();
}

// Когда DOM и демон готовы, запуск скрипта
$(document).ready(function () {
    var demon = chrome.extension.getBackgroundPage();

    (function check_demon_ready () {
        if (demon.isSettingsReady) {
            vkf_settings = new VKFlexSettings();
        } else {
            setTimeout(check_demon_ready, 20);
        }
    })();
});


})(jQuery);