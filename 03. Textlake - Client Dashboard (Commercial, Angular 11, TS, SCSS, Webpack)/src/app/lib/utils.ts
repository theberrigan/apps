import {cloneDeep, forEachRight, forOwn, isArray, isEqual, isUndefined, keys as objKeys} from 'lodash';

export const INTEGER_REGEXP : RegExp = /^-?\d+$/;
export const FLOAT_REGEXP : RegExp = /^-?(\d+(\.\d*)?|\d*\.\d+|\d+e[+\-]?\d+)$/;

// Проблемы встроенных функций:
// 1. parseInt и parseFloat корректно парсят строки, начинающиеся с цифр с минусом или без.
// 2. Number() возвращает 0 вместо NaN, когда ему передают '', [] или null.
// 3. isFinite() возвращает true, когда ей передают '0'.
// 4. Number.isFinite(), Number.isInteger() и прочие функции этого объекта не поддерживаются старыми браузерами.

// Уникальный идентификатор
export const uniqueId : (prefix? : string) => string = (() => {
    let counter : number = 0;

    return (prefix : string = '') => {
        return (prefix + (
            [
                Math.random().toString(36).slice(2),
                Math.random().toString(16).slice(2),
                String(counter++)
            ].join('-').toUpperCase()
        ));
    };
})();

// Текущий таймштамп
export const getTimestamp : () => number = (() => {
    if (Date.now) {
        return Date.now.bind(Date);
    }

    if (+(new Date()) > 0) {
        return () => (+(new Date()));
    }

    return () => (new Date()).getTime();
})();

// Отложить выполнение функции до следующего тика
export const defer = (callback : any) => setTimeout(() => callback(), 0);

// Является ли значение пустым, часто используется с пайпами
export const isEmpty = (value : any) => {
    return value === null || typeof(value) === 'undefined' || value === '';
};

// Проверяет, является ли переменная корректным числом.
export const isFinite : (value : any) => boolean = (() => {
    if ((<any>window).Number && Number.isFinite) {
        return Number.isFinite.bind ? Number.isFinite.bind(Number) : Number.isFinite;
    }

    return (value : any) => {
        return typeof(value) === 'number' && !isNaN(value) && value === value && value !== Infinity && value !== -Infinity;
    };
})();

// Проверяет, является ли value целым числом, а не числом с плавающей точкой.
export const isInt = (value : any) => {
    return isFinite(value) && value === parseInt(<any>(value), 10) && !(value % 1);
};

// Проверяет, является ли value числом с плавающей точкой, а не целым.
export const isFloat = (value : any) => {
    return isFinite(value) && value === parseFloat(value) && (value % 1) !== 0;
};

// Проверяет, представляет ли собой строка корректное целое число.
export const isIntString = (value : any) => {
    return typeof(value) === 'string' && INTEGER_REGEXP.test(value);
};

// Проверяет, представляет ли собой строка корректное число (number или float).
export const isFloatString = (value : any) => {
    return typeof(value) === 'string' && FLOAT_REGEXP.test(value);
};

// Для строк: парсит строку в число. Важно: если строка содержит мусор или число с плавающей точкой, то возвращает NaN
// Для чисел: урезает дробную часть
// Возвращает: number | NaN
export const int = (value : string | number) => {
    return isFinite(value) || isIntString(value) ? parseInt(<any>value, 10) : NaN;
};

// Для строк: парсит строку в число.
// Для чисел: ничего важного не делает.
// В отличие от parseFloat, возвращает NaN, если строка содержит мусор.
// Возвращает: number | NaN
export const float = (value : any) => {
    return isFinite(value) || isFloatString(value) ? parseFloat(parseFloat(value).toPrecision(15)) : NaN;
};

// Выполняет умножение чисел с повышенной точностью.
// Пример:
// 76.6 * 100           -> 7659.999999999999
// mulFloat(76.6, 100)  -> 7660
export const mulFloat = (leftOp : number, rightOp : number) => {
    return isFinite(leftOp) && isFinite(rightOp) ? parseFloat((leftOp * rightOp).toPrecision(15)) : NaN;
};

// Выполняет деление чисел с повышенной точностью.
export const divFloat = (leftOp : number, rightOp : number) => {
    return isFinite(leftOp) && isFinite(rightOp) ? parseFloat((leftOp / rightOp).toPrecision(15)) : NaN;
};

// Усекает дробную часть числа до количества знаков fraction.
// Если опустить второй параметр или передать в него 0, то полностью отбросит дробную часть.
// Примеры:
// truncateFraction(1.5789, 2) -> 1.57
// truncateFraction(1.5, 2)    -> 1.5
export const truncateFraction = (num : number, fraction : number = 0) => {
    const k : number = parseInt(<any>Math.pow(10, fraction < 0 ? 0 : fraction), 10);
    return divFloat(parseInt(<any>(mulFloat(num, k)), 10), k);
};

// Эквивалент метода String.toFixed(), только не округляет дробную часть.
// Превращает число в строку с фиксированным количеством знаков после запятой.
// Примеры:
// toFixedFraction(1.5789, 2) -> "1.57"
// toFixedFraction(1.5, 2)    -> "1.50"
// toFixedFraction(1, 2)      -> "1.00"
// toFixedFraction(1)         -> "1.0"
export const toFixedFraction = (num : number, fraction : number = 1) => {
    return truncateFraction(num, fraction).toFixed(fraction);
};

// Возвращает количество знаков в числе после запятой.
// Ведёт себя по-разному для строк и чисел.
// getFractionLength(1.5700)   -> 2
// getFractionLength('1.5700') -> 4
export const getFractionLength = (value : string | number) => {
    return (String(value).split('.')[1] || '').length;
};

// Вставляет одну строку внутрь другой.
// insertToString('watermelon', 'g', 2, 8) -> 'wagon'
// insertToString('abcd', 'X', 4, 0)       -> 'abcdXabcd'
export const insertToString = (target : string, subject : string, start : number = null, end : number = null) => {
    target = String(target);

    if (!subject) {
        return target;
    }

    start == null && (start = 0);
    end == null && (end = start);

    return target.slice(0, start) + String(subject) + target.slice(end);
};

// Форматирует числовую строку или число, отделяя разряды разделителем delimiter.
// 100000.005 -> 100 000.005
export const formatNumber = (value : number | string, delimiter : string = ' ') => {
    value = String(value);

    if (!delimiter) {
        return value;
    }

    let [ decimal, fractional ] = value.split('.');

    value = fractional ? ('.' + fractional) : '';

    for (let len = decimal.length - 1, i = len; i >= 0; i--) {
        const
            j = len - i,
            char = decimal[i];

        value = char + (j && j % 3 === 0 && char != '-' ? delimiter : '') + value;
    }

    return value;
};

export const getType = (entity : any) : string =>  {
    return Object.prototype.toString.call(entity).slice(8, -1).toLowerCase();
};

export const isObject = (entity : any) => {
    return Object.prototype.toString.call(entity) === '[object Object]';
};

// Сравнивает структуру объектов по ключам
export const isSameObjectsLayout = (o1 : any, o2 : any) => {
    if (!o1 || !o2 || !isEqual(objKeys(o1).sort(), objKeys(o2).sort())) {
        return false;
    }

    for (let key in o1) {
        if (o1.hasOwnProperty(key) && o2.hasOwnProperty(key)) {
            const
                val1 = o1[key],
                val2 = o2[key],
                isVal1Obj = isObject(val1);

            if (isVal1Obj !== isObject(val2) || isVal1Obj && !isSameObjectsLayout(val1, val2)) {
                return false;
            }
        }
    }

    return true;
};

export const updateObject = (...objs) => {
    if (!objs.length) {
        return;
    }

    const [ first, ...others ] = objs;
    const result = {};

    if (objs.length === 1) {
        return isObject(first) ? cloneDeep(first) : first;
    }

    for (let key in first) {
        if (!first.hasOwnProperty(key)) {
            continue;
        }

        let isValueFound = false;
        let value = first[key];
        const isObjectExpected = isObject(value);

        for (let i = others.length; i--;) {
            const obj = others[i];
            const val = obj[key];

            if (!obj.hasOwnProperty(key) || isUndefined(val)) {
                continue;
            } else if (isObjectExpected !== isObject(val)) {
                break;
            } else if (isObjectExpected) {
                value = updateObject(value, val);
            } else if (isArray(val)) {
                value = cloneDeep(val);
            } else {
                value = val;
            }

            isValueFound = true;
        }

        if (isValueFound) {
            result[key] = value;
        } else if (isObjectExpected || isArray(value)) {
            result[key] = cloneDeep(value);
        } else {
            result[key] = value;
        }
    }

    return result;
};

export const cloneDate : (date : Date) => Date = (date : Date) => {
    return date && new Date(date.getTime());
};

// (window as any).updateObject = updateObject;
// ----------------------------------------------------


// Возвращает информацию о выделении текста внутри поля ввода.
// start - начала выделения
// end - конец выделения
// caret - позиция каретки (курсора) в поле
// Возвращает null, если не удалось определить информацию о выделении.
export function getSelectionRange (input : any) : any {
    let start : number = 0,
        end : number = 0,
        caret : number = 0;

    // Chrome, Firefox, Safari, IE 9-11
    if ('selectionStart' in input) {
        caret = Number(input.selectionDirection == 'forward' ? input.selectionEnd : input.selectionStart);
        start = Number(input.selectionStart);
        end = Number(input.selectionEnd);

        // IE < 9
    } else if ('selection' in document) {
        input.focus();  // focus to input

        const range : any = (<any>document).selection.createRange();

        if (range && range.parentElement() == input) {
            const valueLength : number = input.value.length;
            const value : string = input.value.replace(/\r\n/g, '\n');

            const textRange : any = (<any>input).createTextRange();
            textRange.moveToBookmark(range.getBookmark());

            const endRange : any = (<any>input).createTextRange();
            endRange.collapse(false);

            if (textRange.compareEndPoints('StartToEnd', endRange) > -1) {
                start = end = valueLength;
            } else {
                start = -1 * textRange.moveStart('character', -1 * valueLength);
                start += value.slice(0, start).split('\n').length - 1;

                if (textRange.compareEndPoints('EndToEnd', endRange) > -1) {
                    end = valueLength;
                } else {
                    end = -1 * textRange.moveEnd('character', -1 * valueLength);
                    end += value.slice(0, end).split('\n').length - 1;
                }
            }
        }
    } else {
        return null;
    }

    return { caret, start, end };
}

export const isCopyingSupported : () => boolean = () => {
    return Boolean(
        /(chrome|webkit)/i.test(navigator.userAgent) &&
        document.queryCommandSupported &&
        document.queryCommandSupported('copy')
    );
};

export const deleteFromArray : (a : any[], e : any) => any[] = (array : any[], element : any) => {
    const index : number = array.indexOf(element);

    if (index > -1) {
        array.splice(index, 1);
    }

    return array;
};

export const setSelectionRange : (input : any, start : number, end? : number) => boolean = (input, start, end = null) => {
    (!end || end < start) && (end = start);

    if ('selectionStart' in input) {
        input.selectionStart = start;
        input.selectionEnd = end;
        return true;
    } else if (input.setSelectionRange) {
        input.setSelectionRange(start, end);
        return true;
    } else if ((<any>input).createTextRange) {
        const range : any = (<any>input).createTextRange();
        range.collapse(true);
        range.moveEnd('character', start);
        range.moveStart('character', end);
        range.select();
        return true;
    }

    return false;
};

export const str2regexp : (_ : string) => string = (str : string) => {
    str = str.replace(/\s+/g, ' ');

    let result : string = '';

    for (let i : number = 0, len : number = str.length; i < len; i++) {
        const char = str[i];
        result += char == ' ' ? '\\s+' : ('\\u' + ('000' + char.charCodeAt(0).toString(16)).slice(-4));
    }

    return result;
};

export const findByRegexp = (toFind : string, findIn : string, caseSensitive : boolean = false, regexp : RegExp = null) => {
    if (toFind === findIn) {
        return true;
    }

    return (regexp || new RegExp(str2regexp(toFind), caseSensitive ? null : 'i')).test(findIn);
};

export const EMAIL_REGEXP : RegExp = /^[a-z\d\-+._]+@[a-z\d\-.]+\.[a-z]{2,}$/i;
export const isEmailValid : (email : string) => boolean = (email : string) => EMAIL_REGEXP.test(email);

export const trimProperties : (obj : any, isRecursive? : boolean) => any = (obj : any, isRecursive : boolean = false) => {
    for (let key in obj) {
        if (!obj.hasOwnProperty(key)) {
            continue;
        }

        const
            value : any = obj[key],
            type : string = typeof(value);

        if (type == 'string') {
            obj[key] = value.trim();
        } else if (isRecursive && type == 'object' && !Array.isArray(obj)) {
            trimProperties(value, true);
        }
    }

    return obj;
};
