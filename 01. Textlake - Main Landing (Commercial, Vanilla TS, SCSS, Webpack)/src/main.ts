// Polyfills
require('./js/polyfills/raf');

// Modules
import { Power1, TweenLite } from 'gsap/all';

const routes = {
    'landing': /^\/?$/i,
    'tutorial': /^\/?tutorial(\/.*)?$/i
};

const normalizeLocation = () => {
    // .com/?route=/sadasdsadas/asdasdd?param1=1&param2=2#333
    let route = window.location.pathname;

    const query = (
        window.location.search
            .split(/[?&]+/g)
            .reduce((acc, item) => {
                if (item.length) {
                    const [ key, value='' ] = item.split('=');

                    if (key === 'route') {
                        route = decodeURIComponent(value);
                    } else {
                        acc.push(key + '=' + value);
                    }
                }

                return acc;
            }, [])
            .join('&')
    );

    history.replaceState(
        null,
        null,
        route + (query.length ? ('?' + query) : '') + window.location.hash
    );
};

const init = () => {
    normalizeLocation();

    const path = window.location.pathname;
    let moduleName = 'error-404';

    for (let key in routes) {
        if (routes[key].test(path)) {
            moduleName = key;
            break;
        }
    }

    import(
        /* webpackChunkName: `${moduleName}` */
        /* webpackMode: "lazy" */
        `./components/${ moduleName }/index`
    ).then(module => {
        module.default().then((loader : any) => {
            (<any>window).textlake = loader;

            const
                loaderWrap = document.body.querySelector('#page-loader'),
                loaderContent = loaderWrap.querySelector('#page-loader-inner');

            TweenLite.to(loaderContent, 0.5, { scale: 2, ease: Power1.easeInOut });
            TweenLite.to(loaderWrap, 0.5, {
                opacity: 0,
                ease: Power1.easeInOut,
                onComplete: () => {
                    loaderWrap.parentNode.removeChild(loaderWrap);
                    loader.bootstrap.execute();
                }
            });
        });
    });
};

// document.addEventListener('DOMContentLoaded', init);
(/^(interactive|complete)$/).test(document.readyState) ? init() : window.addEventListener('load', init);

// -------------------------------
// -------------------------------

// TODO:
// + Полифиллы или своя реализация: polyfills: Promise, rAF, Array(.isArray/.find/.from/.includes), Object(.entries/.values), String(.includes)
// - Стилизовать типографику в попапах
// - Сделать попапы мобильными
// - Улучшить конфиги tsconfig.json, webpack...js и добавить стейджинг-сборку. Возможно, убрать babel.useBuiltIns: false
// - При прокрутке страницы видно cookie panel
// - Сделать preloader
// - Проверять строки по их .length, а не просто так !''

// - Избавиться от jQuery и написать свои функции делегиррования событий и тд
// - Жесты в видео-/фотогалерее и навигации
// - Анимировать видео-/фотогалерею, попапы
// - Сделать класс/функцию, которая будет управлять отключением скролла на странице, а в css использовать
//   класс для избавления от джеркинга при отключении скролла
// - В прайсинге приделать листенер window.resize
// - Зарефакторить utils.ts
// - Приделать reset.css
// - В css: will-change, pointer-events, no-select, touch-action, -webkit-user-drag
// - Разобраться с отступами внутри секций
// - Разметка schema.org, aria-, meta-теги, manifest.json
// - Приделать google analytics
// - В футере сделать контакты в несколько рядов
// - Отключать анимацию на время инициализации
// - У постеров к видео сделать динамический путь, не привязанный к video_covers
// - Использовать класс Subscriber
// - Улучшить DependencyInjector
// - Инициализировать все модули только методом init
// - Переименовать querySelector в $
// - Компенсировать скрываемый скролл в fixed-элементах
// - Переименовать Scheme -> Workflow
// - indexOf -> includes
// - Горячие клавиши
// - DevServer -> Watch
// - При попадании Screenshots в область экрана, зумить активный очень медленно на точке фокуса
// - Анимировать волнистые границы секций как на https://discordapp.com/ и https://smartslider3.com/shape-divider/#three
// - Сделать кнопки модульными и правильно анимировать active state
// - Компенсация скроллбара должна быть динамической: на десктопах - 17px, на мобильниках - 0px
// - Исправить проблему со шрифтами в IE http://got-quadrat.ru/blog/eots-n-css3111/

// set или парсинг значения по умолчанию
// to
// анимация нескольких элементов и свойств одновременно
// хуки
// анимация свойств любого объекта

// Проверить:
// - Google Page Speed
// - HTML5 Validation

// Заметки:
// - Все ссылки на странице, начинающиейся с # перехватываются обработчиками событий.
//   Ссылки, начинающиеся с #poppup=ID открывают попап с id == ID. Попап подгружает файл: locale/<locale>/<ID>.html
//   Ссылки, начинающиеся с #image=ID открывают изображение с id == ID. Галерея подгружает изображение из config.json
// - Изображения в config.json расположены в двух секциях: standalone - отдельные изображения, gallery - отображаются в секции скриншотов
// - Подписи у изображений для галереи в config.json могут начинаться с i18n=<ключ.локализации>

// z-index:
// - .footer__mimic            : 0
// - .footer__fixed-container  : 1
// - .sections                 : 2
// - .section-main__intro      : 100
// - .panel                    : 200
// - .nav                      : 300
// - .cookie-panel             : 400
// - .popup                    : 500
// - .gallery                  : 600

// Схема config.json:
/*
{
    "languages": [
        {
            "code": "en",       // соответствует директории locale/<code>
            "name": "English",  // имя, которое видит пользователь
            "isDefault": true   // true - должен быть только у одного языка
        },
        ...
    ],
    "video": [
        {
            "image": "_video1.jpg",
            "youtubeId": "Rv9hn4IGofM"
        },
        ...
    ],
    "images": {
        // изображения, которые должны открываться только при клике на какую-то ссылку на странице
        "standalone": [
            {
                "id": "si",                         // id, по которому открывается изображение
                "url": "video_covers/_video1.jpg",  // путь к изображению
                "caption": "i18n=test.caption1"     // подпись. если начинается с i18n=, то подпись сначала пройдёт i18n
            },
            ...
        ],

        // Изображени в галерее скриншотов
        "gallery": [
            {
                "id": "...",
                "url": "...",
                "caption": "..."
            },
            ...
        ]
    }
}
*/
