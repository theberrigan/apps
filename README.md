# 😎 Резюме и портфолио

👱‍ Станислав  
📆 31 год  
🌍 Ярославль  
💻 10 лет опыта в коммерческой разработке. Два года работал fullstack-разработчиком в офисе. Восемь лет – фронтендером на удалёнке.
<p></p>

### ⭐ Опыт

* **Хороший:** JS (ES5-ES2024), TS, Angular 2-17 (Ivy, Standalone Components, Signals), RxJs, ngx-translate, Jest, Bootstrap, GSAP, Lottie, Webpack, Vite, Python, PHP, MySQL, Chrome Extensions, разные Web APIs, REST API, Git, Bitbucket, Jira, Trello, Мегаплан.
* **Базовый:** NgRx, Angular Material, React, Redux, Redux Toolkit, Zustand, Cypress, Node.js, D3, Three.js, WebGL2, компьютерная графика и математика, Rust, C/C++, C#.
* **Нет:** Vue, NgXs, Tailwind, Storybook, Playwright, CI/CD.

💡 Помните, что я всегда готов учиться новому. Например, React, Vue, WebGL, Phaser, Three.js и Pixi.js.
<p></p>

### ⭐ Качества

* Пунктуальный
* Исполнительный
* Самостоятельный
* Всегда на связи
* Быстро учусь
* Перфекционист в рамках разумного

### ⭐ Портфолио

👇 Ниже представлены мои хобби-проекты и урезанные исходники некоторых коммерческих проектов, над которыми я работал в разных компаниях.

## ![BinTools](<./.images/icon_bintools.png>) [BinTools](<./00. BinTools (Vanilla TS, Jest, Webpack)>) <sup><sub>хобби</sub></sup>

📝 Моя новая библиотека для чтения и записи бинарных файлов в браузере или Node.js.  
⚙️ **Typescript 5**, **Webpack**, **Jest**.  
💡  Полностью готова, почти целиком покрыта юнит-тестами на Jest, _пока_ нет документации. Когда доделаю, опубликую в npm.

**Пример использования:**
```ts
import { BinBuffer, EBBIntWriteMode, U8A } from '@berrigan/bin-tools';

const buffer = BinBuffer.create({
    size:          1024,                    // initial buffer size
    autoCapacity:  true,                    // determine capacity automatically on buffer grow
    zeroMemOnGrow: true,                    // clear dirty mem on grow
    maxPageSize:   2048,                    // grow step in bytes
    readOnly:      false,                   // allow writing
    intWriteMode:  EBBIntWriteMode.Strict,  // throw when writing number is OOB of the corresponding int type
    bigEndian:     false                    // by default prefer little endian
});

buffer.writeStr('Адвокааааат! 🤬', 'utf-8');
buffer.align(64);
buffer.writeU32(0xFFFFFFFF);
buffer.seek(0);
buffer.xor(new U8A([ 0xFF, 0x77, 0x33, 0x11 ]));

if (buffer.peekU32() === 0xFFFFFFFF) {
    const unused = buffer.readU64();
}

console.log(buffer.getData());  // Uint8Array

// In browser environment you can download buffer as file:
// buffer.download('useless-data.bin', 'application/x-binary');

buffer.close();
```

## ![](<./.images/icon_textlake_crm.png>) [Лендинг Textlake](<./01. Textlake - Main Landing (Commercial, Vanilla TS, SCSS, Webpack)>) <sup><sub>коммерческий</sub></sup>
📝 С 2016 по 2021 год я работал в компании Openlect LLC. Мы разрабатывали с нуля основной продукт компании – [CRM Textlake](http://textlake.com). Пользователи продукта – бюро переводов. Я занимался дизайном и разработкой всего фронтенда: лендинга и двух дашбордов. Конкретно этот проект — лендинг.  
⚙️ Чистый **Typescript**, **SCSS**, **GSAP**, **Webpack**. Код разбит на модули и компоненты с Dependency Injection.  
👀 Посмотреть можно **[здесь](https://theberrigan.github.io/demos/textlake-landing/)**.

![](<./.images/textlake_landing.webp>)

## ![](<./.images/icon_textlake_crm.png>) [Textlake CRM](<./02. Textlake - CRM (Commercial, Angular 11, TS, SCSS, Webpack)>) <sup><sub>коммерческий</sub></sup>

📝 Это основной дашборд – [CRM](https://tsm.textlake.com). Именно в нём сотрудники бюро организуют всю свою работу и общаются с заказчиками. Всё разработано с нуля без готовых UI Kits.  
⚙️ **Angular 2-11**, **Angular Animations**, **ngx-translate**, **Lodash**, **Typescript**, **SCSS**, **Webpack**, **AWS Cognito**, **MQTT**, **Stripe**, **Sofort**.  
👀 **[Здесь](https://theberrigan.github.io/demos/textlake-landing/#screenshots)** и **[здесь](https://youtu.be/772IOQsjZwg)** можно посмотреть, как выглядит дашборд внутри.

![](<./.images/textlake_crm.png>)

## ![](<./.images/icon_textlake_cdb.png>) [Textlake Client Dashboard](<./03. Textlake - Client Dashboard (Commercial, Angular 11, TS, SCSS, Webpack)>) <sup><sub>коммерческий</sub></sup>

📝 А это дашборд для клиентов бюро. Там они могут просматривать и оплачивать заказы.  
⚙️ Тот же стек, что и у CRM.  
👀 На скриншоте ниже страница оплаты заказа.

![](<./.images/textlake_client_dashboard.jpg>)

## ![](<./.images/icon_linguardia.png>) [Лендинг Linguardia](<./04. Textlake - Linguardia Landing (Commercial, Angular 11, TS, SCSS, Webpack)>) <sup><sub>коммерческий</sub></sup>

📝 Лендинг, который я делал для нашего первого клиента – бюро [NSGroup](http://www.nsgroup.info/).  
⚙️ **Angular**, **ngx-translate**, **Typescript**, **SCSS**, **Webpack**.  
👀 **[Здесь](https://theberrigan.github.io/demos/linguardia-landing/)** можно посмотреть демо.

![](<./.images/linguardia_landing.webp>)

**💼 С января 2021 я перешёл в компанию AETolls LLC для работы над её новым продуктом TapNPay – веб-приложением для оплаты проезда по платным дорогам США. Я занимал ту же должность – разработчик фронтенда.**  

**👇 Следующие несколько проектов являются частью этого продукта.**  

## ![](<./.images/icon_tnp_client.png>) [Лендинги Tapnpay](<./05. Tapnpay Landings (WP-theme) (PHP, Wordpress, SCSS, TS, SCSS, Gulp)>) <sup><sub>коммерческий</sub></sup>

📝 Два лендинга в одной теме для WordPress. Один общий для продукта, другой – конкретно для Флориды.  
⚙️ **WordPress**, **PHP**, **Typescript**, **SCSS**, **Gulp** + **tsc**.  
👀 **[Демо один](https://theberrigan.github.io/demos/tapnpay-landing/)**, **[демо два](https://theberrigan.github.io/demos/tapnpay-sunpass-landing/)**.

![](<./.images/tapnpay_landing.webp>)
![](<./.images/tapnpay_sunpass_landing.webp>)

## ![](<./.images/icon_tnp_client.png>) [Tapnpay Client Dashboard](<./06. Tapnpay - Client Dashboard (Commercial, Angular 17, TS, SCSS, Webpack, Cypress)>) <sup><sub>коммерческий</sub></sup>

📝 Дашборд, в котором пользователи оплачивают проезд.  
⚙️ **Angular 11-17**, **ngx-translate**, **SCSS**, **Typescript**, **Webpack**, **Cypress**, **Jest**, **Stripe**, **Vimeo**, **PayPal**, **Braintree**.  
👀 **[Демо](https://tapnpaydemo.com/auth)**, если удастся зарегистрироваться. **[Здесь](https://disk.yandex.ru/i/OX2HIeMzx6xYoA)** можно посмотреть, как сервис работает на смартфоне. 

![](<./.images/tapnpay_dashboard.png>)

## ![](<./.images/icon_tnp_admin.png>) [Tapnpay Admin Dashboard](<./07. Tapnpay - Admin Dashboard (Commercial, Angular 14, TS, SCSS, Webpack)>) <sup><sub>коммерческий</sub></sup>

📝 В этом дашборде администраторы... администрируют 🙂  
⚙️ **Angular 11-14**, в остальном тот же стек.  
👀 К сожалению, демо нет.  

**⚔ В 2024 году компанию AETolls LLC поглотил конкурент – NeoRide Inc., а наш проект передали их команде.**

## 🎯 [Тестовое задание](<./08. Vacancy Test Project (Angular 20, Signals, Less, Vite)>) <sup><sub>тестовое</sub></sup>

📝 Тестовое задание от компании с hh: сделать список пользователей с фильтрацией по имени и активности.  
⚙️ **Angular 20**, **Angular Material**, **Signals**, **Vite**, **Less**.  
👀 Внутри есть README с инструкцией, как собрать и запустить проект.  

![](<./.images/vacancy_test.png>)

**👇 Далее идут несколько расширений для браузера, которые я делал для себя.**

## ![](<./09. Chrome Extension Currency Rate (Vanilla JS)/images/icon_16.png>) [Chrome Extension Currency Rate](<./09. Chrome Extension Currency Rate (Vanilla JS)>) <sup><sub>хобби</sub></sup>

📝 Расширение для Chromium-браузеров, которое отображает текущий курс продажи доллара в [Альфа-Банке](https://alfabank.ru/currency/).  
⚙️ Чистый **JS**, **Chrome Extension API**.  
👀 Подробности внутри. 

## ![](<./10. Chrome Extension Steam Tools (Vanilla JS)/images/icons/icon_16.png>) [Chrome Extension Steam Tools](<./10. Chrome Extension Steam Tools (Vanilla JS)>) <sup><sub>хобби</sub></sup>

📝 Расширение для Chromium-браузеров, которое приводит в порядок сайдбар на странице игры в [Steam](https://store.steampowered.com/) и добавляет туда время прохождения игры из [How Long To Beat](https://howlongtobeat.com/) и [SteamHunters](https://steamhunters.com/).  
⚙️ Чистый **JS**, **Chrome Extension API**.  
👀 Подробности внутри.  

![](<./.images/ce_steam.webp>)

## ![](<./11. Chrome Extension Tab Unloader (Vanilla JS)/images/icons/icon_16.png>) [Chrome Extension Tab Unloader](<./11. Chrome Extension Tab Unloader (Vanilla JS)>) <sup><sub>хобби</sub></sup>

📝 Расширение для Chromium-браузеров, которое позволяет вручную выгружать вкладки для экономии ресурсов компьютера.  
⚙️ Чистый **JS**, **Chrome Extension API**.  
👀 Подробности внутри.  

## ![](<./12. Chrome Extension Yar Weather (Vanilla JS)/images/icon_16.png>) [Chrome Extension Yar Weather](<./12. Chrome Extension Yar Weather (Vanilla JS)>) <sup><sub>хобби</sub></sup>

📝 Расширение для Chromium-браузеров, которое отображает текущую температуру воздуха в Ярославле на основе данных из [Gismeteo](https://www.gismeteo.ru/weather-yaroslavl-4313/now/).  
⚙️ Чистый **JS**, **Chrome Extension API**.  
👀 Подробности внутри.  

## ![](<./13. Chrome Extension Headhunter Vacancies Watcher (Vanilla JS)/images/icon_16.png>) [Chrome Extension Headhunter Vacancies Watcher](<./13. Chrome Extension Headhunter Vacancies Watcher (Vanilla JS)>) <sup><sub>хобби</sub></sup>

📝 Расширение для Chromium-браузеров, которое каждые несколько минут запрашивает вакансии на [hh.ru](https://hh.ru/) по заданным фильтрам (хардкоднуто в js-файле) и уведомляет о новых.  
⚙️ Чистый **JS**, **Chrome Extension API**.  
👀 Подробности внутри. 

## ![](<./.images/icon_fssbe.png>) [Fallout Shelter Save Backuper & Editor](<./14. Fallout Shelter Save Backuper & Editor (Vanilla JS, Node.js, Crypto API)>) <sup><sub>хобби</sub></sup>

📝 Node.js-скрипт для редактирования и создания резервных копий файлов сохранения игры Fallout Shelter.  
⚙️ Чистый **JS**, **Node.js**, **Web Crypto API**.

## ![](<./.images/icon_steam.png>) [Steam Achievement Manager](<./15. Steam Achievement Manager (JS, Bootstrap, Python 3, Flask)>) <sup><sub>хобби</sub></sup>

📝 Менеджер достижений игрока в играх из Steam.  
⚙️ Чистый **JS**, **Bootstrap 5**, **Python**, **Flask**, **Request**.

![](<./.images/steam_achievment_manager.webp>)

## ![](<./.images/icon_gtasa.png>) [Карта предметов в GTA San Andreas](<./16. GTA San Andreas Collectibles Map (Vanilla JS, Tippy.js, Python 3.11, Flask)>) <sup><sub>хобби</sub></sup>

📝 Карта коллекционных предметов в GTA San Andreas.  
⚙️ Чистый **JS**, **Python**, **Flask**.  
👀 Подробности внутри.  

![](<./.images/gtasa_map.webp>)

## ![](<./.images/icon_vk.png>) [VK Flex](<./17. Legacy Chrome Extension VKFlex (Legacy 2013-2018) (JS, jQuery)>) <sup><sub>хобби</sub></sup>

📝 Это расширение для Chromium-браузеров, которое меняет интерфейс ВК и добавляет новые функции. Я разрабатывал и поддерживал его с 2013 по 2018 год. В 2019 проект выкупили. Оно в портфолио, на случай если работодателю важно моё умение работать с устаревшим кодом.  
⚙️ Чистый **JS**, **jQuery**.  
👀 Новый владелец его забросил, но оно до сих пор доступно в **[Chrome Store](https://chromewebstore.google.com/detail/VK%20Flex/ljbmkjikheoaglnnifnghjbknejbmhap)**.  

![](<./.images/vk_flex.webp>)

**👇 Остальные проекты не связаны с frontend-разработкой. В свободное время я люблю заниматься реверс-инжинирингом компьютерных игр из нулевых. Ниже идут инструменты, разработанные мной для этих целей.**

## ![](<./.images/icon_gtavc.png>) [Парсер файлов GTA Vice City](<./18. GTA Vice City Game Files Parser (Python 3.11)>) <sup><sub>хобби</sub></sup>

📝 Парсер файлов игры GTA Vice City.  
⚙️ **Python 3**.  
👀 Большая часть кода **[здесь](<./18. GTA Vice City Game Files Parser (Python 3.11)/packages/converter/src/vcc/formats>)**.

## ![](<./.images/icon_hl.png>) [Парсер файлов Half-Life](<./19. Half-Life Game Files Parser (Python 3.11)>) <sup><sub>хобби</sub></sup>

📝 Парсер файлов игры Half-Life.  
⚙️ **Python 3**.  
👀 Большая часть кода **[здесь](<./19. Half-Life Game Files Parser (Python 3.11)/packages/converter/src/hlc/formats>)**. 

## 🛠️ [Data Reverse Engineering Framework](<./20. Data Reverse Engineering Framework (Python 3.11)>) <sup><sub>хобби</sub></sup>

📝 Многофункциональный фреймворк: чтение/запись разных файлов, парсеры форматов, обёртки вокруг DLL-библиотек и EXE-файлов, алгоритмы сжатия данных и т.д.  
⚙️ **Python 3**.

## 🎮 [Game Tools](<./21. GameTools (Python 3.11)>) <sup><sub>хобби</sub></sup>

📝 Инструменты для конкретных игр. В основном это распаковщики игровых файлов.  
⚙️ **Python 3**.

## 🗜️ [Oodle Python Bindings](<./22. Oodle Python Bindings (Python 3.8)>) <sup><sub>хобби</sub></sup>

📝 Python-биндинги для библиотеки сжатия данных Oodle, которая часто используется в современных играх.  
⚙️ **Python 3**.

## ![](<./.images/icon_yamusic.png>) [Yandex Music Albums Collector](<./23. Yandex Music Albums Collector (Python 3.8, SQLite, Threading, Requests)>) <sup><sub>хобби</sub></sup>

📝 Многопоточный сборщик музыкальных альбомов из Яндекс Музыки. Собирает, сжимает и кладёт их в SQLite базу данных.  
⚙️ **Python 3**, **SQLite**.





