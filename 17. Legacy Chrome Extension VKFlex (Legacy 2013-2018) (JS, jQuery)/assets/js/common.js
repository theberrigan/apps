// VK Flex Chrome Extension: common.js
// Dependencies: jQuery.js

var vkf_common;

(function ($) {

function VKFlexCommon () {

    var that = this,
        LS = localStorage,
        __isURLMC = false; // 'is URL Malformed Catched' (For long-time debug)

    // Префикс ключей в localStorage
    this.ls_prefix = 'vkf_';

    // Функция логирования в консоль
    this.log = function () {
        var args = (['VK Flex:']).concat(Array.prototype.slice.call(arguments));
        console.log.apply(console, args);
    }; 

    // Функция логирования ошибок в консоль
    this.error = function (e) {
        var args = ['VK Flex Error:'];

        if (e.name && e.message) {
            args.push(e.name + ':');
            args.push(e.message);
        } else {
            args = args.concat(Array.prototype.slice.call(arguments));
        }

        console.error.apply(console, args);
    }; 

    // Разделяет строку переданными разделителями
    // str - строка
    // sep - 1 разделитель или массив из разделителей
    // ees - исключать пустые строки
    this.multisplit = function (str, sep, ees) { 
        if (that.isString(sep)) {
            sep = [sep];
        }

        if (!that.isString(str) || !that.isArray(sep)) {
            that.error('Multisplit args type error.');
            return false;
        }

        // Результирующий массив
        var result = [];

        // Если входная строка пустая
        if (!str) {
            // Если не пропускать пустые строки
            if (!ees) { 
                result.push(str);
            }
        } else {
            var tail = str,
                msi, // min sep index
                msp, // min sep position
                csp, // cur sep position
                ps;  // push slice

            // До тех пор, пока хвост не станет пустым
            while (tail) {
                // Индекс и позиция пока не определены
                msp = msi = false;

                // Перебрать все разделители
                for (var i in sep) {
                    // Найти делитьтель в хвосте
                    csp = tail.indexOf(sep[i]);

                    // Если делитель найден, а самая левая позиция делителя ещё не определена или меньше текущей
                    if (csp != -1 && (msp === false || msp > csp)) {
                        msp = csp; // Установить мин позицию в текущую
                        msi = i;   // Установить индекс минимальной позиции

                        // Если текущая минимальная позиция равна нулю, то другую искать не надо,
                        // потому что 0 - это минимально возможное значение
                        if (csp == 0) {
                            break;
                        } 
                    }
                }
                
                // Если позиция делителя найдена
                if (msp !== false && msi !== false) {
                    // Получить строку до делителя
                    ps = tail.slice(0, msp);

                    // Если полученный кусок удовлетворяет условиям, добавить его в результат
                    if (ps || (!ps && !ees)) result.push(ps);

                    // Обрубить хвост
                    tail = tail.slice(msp + sep[msi].length);

                    // Если хвост стал пустой строкой, возможно, его нужно добавить в результат
                    if (!tail && !ees) result.push(tail);

                // Если больше ни один делитель не найден в строке
                } else {

                    // Если у хвоста есть длина, или её нет И в результат нужно добавлять пустые строки :)
                    if (tail || (!tail && !ees)) result.push(tail);

                    // Явно указать, что хвоста нет
                    tail = false;
                }
            }
        }

        return result;
    };

    // Возвращает настоящий тип переменной
    // undefined, null, NaN, integer, float, array,
    // object, function, boolean, string, regexp
    this.get_type = function (variable) {
        var t = Object.prototype.toString.call(variable).toLowerCase().split(' ')[1].slice(0, -1);
        
        if (t == 'number') {
            t = isNaN(variable) ? 'NaN' : (parseInt(variable, 10) === variable ? 'integer' : 'float');
        }

        return t;
    };

    // Очищает имя от html-тегов и запрещённых в ОС символов и заменяет многократный пробелы одним
    this.clear_file_title = function (title) {
        var filter = document.createElement('div');

        filter.innerHTML = title;
        title = filter.innerText.replace(/[\\\/:\*\?"<>\|]/g, '').trim().replace(/\s+/g, ' ');

        return title;
    };

    // Переводит строку из windows-1251 в utf-8
    this.win2utf = function (s) { 
        var r = '',       // result
            l = s.length, // original string length
            o,            // origin symbol
            c;            // converted symbol

        while (l--) { 
            o = s.charCodeAt(l); 

            if (o === 184) { 
                c = 1105; 
            } else if (o === 168) { 
                c = 1025; 
            } else if (o > 191 && o < 256) { 
                c = o + 848; 
            } else { 
                c = o; 
            } 

            r = String.fromCharCode(c) + r; 
        } 

        return r; 
    };

    // Переводит строку из get-параметров в объект
    this.parse_get = function (get_str, decode_func) {
        var obj = {};

        if (that.isString(get_str)) {
            if (get_str[0] == '?') {
                get_str = get_str.slice(1);
            }

            if (get_str.length) {
                get_str = get_str.trim().split('&');

                for (var dec, pairs, i = 0; i < get_str.length; i++) {
                    pairs = get_str[i].split('=');
                    if (pairs.length == 1) {
                        pairs[1] = null;
                    } else if (that.isFunction(decode_func)) {
                        // Пробуем раскодировать строку
                        try {
                            dec = decode_func(pairs[1]);
                        } catch (e) {
                            // Если при декодировании произошла ошибка, скорее всего исходная строка была в windows-1251
                            // Пробуем перевести её из win1251 в utf8
                            // Если всё-равно ошибка, добавляем в результат нераскодированную строку
                            try {
                                dec = that.win2utf(unescape(pairs[1])); 
                            } catch (e) {
                                dec = pairs[1];

                                if (!__isURLMC) {
                                    that.error('URL Malformed: value:', pairs[1]);
                                    __isURLMC = true;
                                }
                            }
                        }
                        pairs[1] = dec;
                    }

                    obj[pairs[0]] = pairs[1];
                }
            }
        } else {
            that.error('that.parse_get error, "get_str" is not a string:', get_str);
        }

        return obj;
    };

    // Выделяет весь текст в текстовом инпуте
    this.input_select_all = function (input) {
        if (input) {
            var len = input.value.length;
            if (input.createTextRange) {
                var range = input.createTextRange();
                range.collapse(true);
                range.moveEnd('character', 0);
                range.moveStart('character', len);
                range.select();
            } else if (input.setSelectionRange) {
                input.setSelectionRange(0, len);
            }            
        }
    };

    // Состоитли аргумент только из чисел
    this.isNum = function (str) {
        if (that.isUndefined(str)) {
            return false;
        } else {
            if (!that.isString(str)) {
                try {
                    str = str.toString();
                } catch (e) {
                    return false;
                }
            }
            return (/^\d+$/.test(str));
        }
    };

    // Является ли переменная строкой
    this.isString = function (variable) {
        return (that.get_type(variable) === 'string');
    };

    // Является ли переменная массивом
    this.isArray = function (variable) {
        return (that.get_type(variable) === 'array');
    };

    // Является ли переменная объектом
    this.isObject = function (variable) {
        return (that.get_type(variable) === 'object');
    };

    // Является ли переменная функцией
    this.isFunction = function (variable) {
        return (that.get_type(variable) === 'function');
    };

    // Является ли переменная целым числом
    this.isInteger = function (variable) {
        return (that.get_type(variable) === 'integer');
    };

    // Является ли переменная числом с плавающей точкой
    this.isFloat = function (variable) {
        return (that.get_type(variable) === 'float');
    };

    // Является ли переменная неопределённой
    this.isUndefined = function (variable) {
        return (that.get_type(variable) === 'undefined');
    };

    // Проверяет наличие элемента в массиве
    this.inArray = function (item, array) {
        return (array.indexOf(item) !== -1);
    };

    // Создаёт глубокую копию массива или объекта
    this.clone = function (variable) {
        var empty = that.isObject(variable) ? {} : (that.isArray(variable) ? [] : null);
        return empty === null ? variable : $.extend(true, empty, variable);
    };

    // Отфильтровывает элементы массива по типу (-ам) 
    // и возвращает либо отфильтрованный массив, либо кол-во отфильтрованных элементов
    this.array_filter_by_types = function (array, types, only_count) {
        if (!that.isArray(types)) {
            types = [types];
        }

        var filtered = [];

        for (var i in array) {
            if (that.inArray(that.get_type(array[i]), types)) {
                filtered.push(array[i]);
            }
        }

        return only_count ? filtered.length : filtered;
    };

    // Получает список ключей объекта в виде массива
    this.object_get_keys = function (object) {
        var keys;

        if (Object.keys) {
            keys = Object.keys(object);
        } else {
            keys = [];
            var i = 0;
            for (keys[i++] in object);
        }  

        return keys;
    };

    // Проверяет, пустой ли объект
    this.isEmpty = function (obj) {
        return !Object.keys(obj).length;
    };

    // В обычном режиме возвращает все ключи объектов
    // В режиме intesect возвращает только общие ключи объектов
    // Одинаковые ключи удаляются
    this.objects_get_keys = function (objects, intesect) {
        // Отфильтровываем объекты
        objects = that.array_filter_by_types(objects, 'object');

        var keys = [],
            cur_obj,
            cur_obj_keys,
            isPushAllowed;

        // Перебор всех объектов
        for (var ooi in objects) { 

            // Получаем все ключи текущего объекта
            cur_obj_keys = that.object_get_keys(objects[ooi]);

            // Перебираем все ключи текущего объекта
            for (var ki in cur_obj_keys) {
                isPushAllowed = true;

                // Если только общие ключи
                if (intesect) {

                    // Перебираем все объекты, кроме текущего
                    for (var ioi in objects) {

                        // Если нет ключа в объекте, не добавляем этот ключ в конечный массив
                        // Так как режим intersect, и в данном объекте не найден текущий ключ,
                        // прерываем цикл, потому что нет смысла в проверке остальных объектов
                        if (!(cur_obj_keys[ki] in objects[ioi])) {
                            isPushAllowed = false;
                            break;
                        }
                    }
                }

                // Если разрешено добавление ключа в конеынй массив,
                // и этого ключа ещё нет в конечном массиве, добавляем
                if (isPushAllowed && !that.inArray(cur_obj_keys[ki], keys)) {
                    keys.push(cur_obj_keys[ki]);
                }
            }

            // В режиме intesect достаточно проверить только первый объект
            if (intesect) {
                break;
            }
        } 

        return keys;
    };

    // Функция объединяет несколько объектов в один.
    // В режиме рекурсии объединяет и вложенные объекты
    // Четыре правила объединения:
    // - normal - вносит все ключи-значения из объединяемых объектов в конечный объект
    // - intersect - объединяет только по общим (пересекающимся) ключам
    // - left - вносит в конечный объект все ключи из левого объекта и те ключи из правого объекта, которые есть в левом
    // - right - вносит в конечный объект все ключи из правого объекта и те ключи из левого объекта, которые есть в правом
    // Особенность left и right в том, что из массива объектов берутся только первые 2. Если объектов больше, то все остальные игнорируются
    this.objects_merge = function (objects, recursion, rule) {
        // Конечный объект
        var result = {};

        objects = that.array_filter_by_types(objects, 'object');

        rule = (rule || 'normal').toLowerCase();

        // Правило для объединения
        if (!that.inArray(rule, ['normal', 'left', 'right', 'intersect'])) {
            rule = 'normal';
        }

        // Функция объединения
        (function walker (obj, objs) {
            var isLOR = that.inArray(rule, ['left', 'right']),  // Является ли объедиение left или right
                obj_max_i = objs.length - 1,                    // Индекс последнего объекта в массиве
                keys = (isLOR ? that.object_get_keys(objs[(rule == 'left' || obj_max_i === 0) ? 0 : 1]) : that.objects_get_keys(objs, rule == 'intersect')); // Ключи переданных объектов, собранные по правилу rule

            // Перебор всех собранных ключей
            for (var key in keys) {
                key = keys[key];

                // Перебор массива с объектами С КОНЦА.
                // Если left || right, то перебрать только первые 2 объекта в массиве, в противном случае перебрать все объекты массива
                for (var ooi = isLOR ? Math.min(1, obj_max_i) : obj_max_i, done = 0; ooi >= 0; ooi--, done++) {

                    // Если данный элемент - объект && данный ключ есть в данном объекте
                    if (that.isObject(objs[ooi]) && key in objs[ooi]) {

                        // Значение под данным ключом в данном объекте
                        var val = objs[ooi][key]; 

                        // Если значение под ключом является объектом
                        if (that.isObject(val)) {

                            // Если рекурсивное объединение
                            if (recursion) {

                                // Создать в конечном объекте пустой объект под данным ключом
                                obj[key] = {};

                                // Массив для коллекционирования ПОДобъектов
                                var inner_objects = [];

                                // Перебрать каждый объект из массива объектов, переданных данной функции
                                for (var ioi in objs) {

                                    // Определить, существует ли данный ключ в данном объекте, и является ли значение объектом
                                    // Если данное значение - объект, закинуть его в массив
                                    if (key in objs[ioi] && that.isObject(objs[ioi][key])) {
                                        inner_objects.push(objs[ioi][key]);
                                    }
                                }

                                // Отправить ссылку на пустой подобъект и массив с объектами рекурсивно в эту же функцию
                                walker(obj[key], inner_objects);

                            // Если _НЕ_рекурсивное объединение
                            } else {

                                // Внести клона данного объекта под данный ключ в конечный объект
                                obj[key] = that.clone(val);
                            }

                        // Если значение под ключом _НЕ_ является объектом
                        } else {
                            
                            // Внести данное значение под данный ключ в конечный объект
                            obj[key] = that.clone(val);
                        }
                        break;
                    }

                    // Если left || right && уже проверены 2 первых элемента из массива, прервать цикл
                    if (isLOR && done == 2) {
                        break;
                    }
                }
            }

            //console.log(rule, keys);
        })(result, objects);

        return result;
    };

    // Получает значение под ключом из localStorage
    // Возвращает результат или null
    // key - ключ в localStorage (к нему добавляется префикс)
    // parse_as - указывает на то, как парсить значение
    // default_val - значение по умолчанию, которое будет возвращено, если значение в LS не верное
    // force_merge - (только для объектов) в значении true насильно объединяет значение из LS и default_val
    this.ls_get = function (key, parse_as, default_val, force_merge) {
        // Валидация ключа
        if (!that.isString(key)) {
            throw new Error('First argument must be a string.');
            return null;
        }

        // Валидация режима парсинга (или false)
        parse_as = that.isString(parse_as) ? parse_as.toLowerCase() : false;
        if (!that.inArray(parse_as, ['integer', 'float', 'json', 'eval', 'decodeuri'])) {
            parse_as = false;
        }

        var val = LS.getItem(that.ls_prefix + key),     // Значение из LS
            isDefVal = !that.isUndefined(default_val),  // Передано ли значение по умолчанию в функцию
            isRestore = false;                          // Флаг, который в значении true говорит о том, что нужно записать обработанное значение обратно в LS 

        // Обработка значения 
        switch (parse_as) {

            // Обработать как целое или вещественное число
            case 'integer':
            case 'float':
                val = parse_as === 'integer' ? parseInt(val, 10) : parseFloat(val);
                if (isNaN(val)) {
                    if (isDefVal) {
                        val = default_val;
                        isRestore = true;
                    } else {
                        val = null;
                    }
                }
                break;

            // Обработать как массив или объект
            case 'json': 

                // Если значение не получено из LS, то вернуть либо значение по умолчанию, либо null
                if (val === null) {
                    if (isDefVal) {
                        val = default_val;
                        isRestore = true;
                    } else {
                        val = null;
                    }

                // Если значение из LS не null
                } else {
                    try {
                        val = JSON.parse(val);

                        // Если значение из LS - объект, и значение по умолчанию - объект, и насильное объединение объектов, то сделать левое объединение объектов в пользу значения по умолчанию
                        if (that.isObject(val)) {
                            if (that.isObject(default_val) && force_merge) {
                                val = that.objects_merge([default_val, val], true, 'left');
                                isRestore = true;
                            }

                        // Если полученное значение не объект и не массив,  
                        } else if (!that.isArray(val)) {
                            val = isDefVal ? default_val : null;
                        }
                    } catch (e) {
                        if (isDefVal) {
                            val = default_val;
                            isRestore = true;
                        } else {
                            val = null;
                        }
                    }
                }
                break;

            // Обработка значения с помощью эвалюации
            case 'eval': 
                try {
                    val = eval(val);
                } catch (e) {
                    if (isDefVal) {
                        val = default_val;
                        isRestore = true;
                    } else {
                        val = null;
                    }
                }
                break;

            // Обработка значения функцией decodeURI
            case 'decodeuri': 
                if (val === null) {
                    if (isDefVal) {
                        val = default_val;
                        isRestore = true;
                    } else {
                        val = null;
                    }
                } else {
                    val = decodeURI(val);
                }
                break;

            // Иначе вернуть само значение или значение по умолчанию или null
            default:
                if (val === null) {
                    if (isDefVal) {
                        val = default_val;
                        isRestore = true;
                    } else {
                        val = null;
                    }
                }
                break;
        }

        // При необходимости восстанавливает значение в LS
        if (isRestore) {
            that.ls_set(key, val, that.isObject(val) ? 'json' : false);
        }

        return val;
    };

    // Устанавливает значение под ключ в localStorage
    // key - ключ
    // data - данные для записи под ключ
    // stringify_func - (не обязательный параметр) указывает то, как что должен быть обработан аргумент data перед записью в LS
    this.ls_set = function (key, data, stringify_func) {
        // Валидация ключа
        if (!that.isString(key)) {
            throw new Error('First argument must be a string.');
            return null;
        }

        // При необходимости обработать значение перед записью в LS
        if (stringify_func) {
            stringify_func = stringify_func.toLowerCase();

            switch (stringify_func) {
                case 'json':
                    data = JSON.stringify(data);
                    break;
                case 'encodeuri':
                    data = encodeURI(data);
                    break;
            };
        }

        // Запись в LS
        LS.setItem(that.ls_prefix + key, data);
    };

    // Удаляет ключ из localStorage
    // key - ключ
    this.ls_remove = function (key) {
        // Валидация ключа
        if (!that.isString(key)) {
            throw new Error('First argument must be a string.');
            return null;
        }

        // Удаление из LS
        LS.removeItem(that.ls_prefix + key);
    };
}

$.fn.hasAttr = function (attr) {
    var val = $(this).attr(attr);
    return val !== false && val != null && typeof(val) !== 'undefined';
};

vkf_common = new VKFlexCommon();

// --------------

window.c = {};

c.inArray = function (item, array) {
    return array.indexOf(item) !== -1;
};

// Build node tree
c.bnt = function (obj, parent) {
    var tag = obj.tag,
        node = document.createElement(tag),
        val;

    delete obj.tag;

    for (var key in obj) {
        val = obj[key];

        if (c.inArray(key, ['href', 'id', 'innerHTML', 'innerText'])) {
            node[key] = val;
        } else if (key == 'class' && (val = [val]) || key == 'classes') {
            node.className = val.join(' ');
        } else if (key == 'child' && (val = [val]) || key == 'children') {
            val.forEach(function (child) {
                c.bnt(child, node);
            });
        } else {
            node.setAttribute(key, val); 
        }
    }

    parent && parent.appendChild(node);

    return node;
};

c.aClass = function (el, cls) {
    if (el && cls) {
        var cn = (el.className || '').replace(/\s+/, ' ').trim().split(' ');

        for (var i in cn) {
            if (cls == cn[i]) {
                return;
            }
        }

        cn.push(cls);

        el.className = cn.join(' ');
    }
};

c.rClass = function (el, cls) {
    if (el && cls) {
        var cn = (el.className || '').replace(/\s+/, ' ').trim().split(' '),
            new_cn = [];

        for (var i in cn) {
            cls != cn[i] && new_cn.push(cn[i]);
        }

        el.className = new_cn.join(' ');
    }
};

})(jQuery);