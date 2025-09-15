// VK Flex Chrome Extension: injection.js
// Error decoding: ?to=https%3A%2F%2Fru.wikipedia.org%2Fwiki%2F%CA%F3%E4%E0%E9%E1%E5%F0%E3%E5%ED%EE%E2%2C_%C4%E8%ED%EC%F3%F5%E0%EC%E5%F2_%CA%E0%ED%E0%F2%EE%E2%E8%F7,https%3A%2F%2Fru.wikipedia.org%2Fwiki%2F%CA%F3%E4%E0%E9%E1%E5%F0%E3%E5%ED%EE%E2%2C_%C4%E8%ED%EC%F3%F5%E0%EC%E5%F2_%CA%E0%ED%E0%F2%EE%E2%E8%F7

(function () {

'use strict';

const copyText = (text) => {
    navigator.clipboard.writeText(text);
};

const htmlToElement = html => {
    return new DOMParser().parseFromString(html, 'text/html').body.firstChild;
};

const addListeners = (el, listeners) => {
    const els = el.querySelectorAll('[data-event-handlers]');

    els.forEach(el => {
        el.dataset.eventHandlers
            .replace(/\s+/g, '')
            .split(',')
            .forEach(pair => {
                const [ eventName, listenerName ] = pair.split(':');
                el.addEventListener(eventName, e => listeners[listenerName](e, el));
            });

        delete el.dataset.eventHandlers;
    });
};

class Injection {
    constructor () {
        // TODO: Check is demon ready
        this.extensionId = window.vkfExtensionId;

        this.modules = {};
        this.cache = {};
        this.observer = null;

        this.hooks = {
            addedNodes: [],
            removedNodes: [],
            onSidebarChanged: [],
            onLocationChanged: []
        };

        this.hideStyles = [
            'opacity: 0 !important;',
            'position: fixed !important;',
            'z-index: -5 !important;',
            'height: 0 !important;',
            'width: 0 !important;',
            'max-height: 0 !important;',
            'max-width: 0 !important;',
            'overflow: hidden !important;',
            'left: -99999px !important;',
            'top: -99999px !important;',
            'display: block !important;'
        ].join(' ');

        //document.body.classList.remove('new_header_design');

        this.coreMessage('getInjectionData', (injectionData) => {
            this.settings = injectionData.settings;
            this.langData = injectionData.langData;

            this.loadModules();
            this.initObserver();

            if (injectionData.welcomeMessage) {
                this.showFastBox(injectionData.welcomeMessage, 1000, null, (isSuccess) => {
                    isSuccess && this.coreMessage('welcomeMessageIsShown');
                });
            }

            // TODO: Show omnibox tip
            /*
            that.showFastBox(that.lang_data['msg_obt']);
            that.coreMsg({
                action: 'omnibox_tip_is_shown'
            });
            */
        });

        this.log('And away we go...');
    }

    showFastBox (message, delay = 0, title = null, callback = () => {}) {
        setTimeout(() => {
            if (window.showFastBox) {
                window.showFastBox({
                    dark: 1,
                    title: title || this.lang('msg_title'),
                    bodyStyle: 'padding: 20px; line-height: 160%;'
                }, message);
                callback(true);
            } else {
                this.warn('[Injection.showFastBox] Can\'t show fastbox, global function showFastBox doesn\'t exist');
                callback(false);
            }
        }, delay);
    }

    getType (target) {
        return Object.prototype.toString.call(target).toLowerCase().match(/^\[\w+\s(\w+)\]$/)[1];
    }

    isObj (target) {
        return this.getType(target) === 'object';
    }

    isFunc (target) {
        return this.getType(target) === 'function';
    }

    isStr (target) {
        return this.getType(target) === 'string';        
    }

    log (...args) {
        console.log.call(console, '%c[VK Flex]', 'font-weight: bold;', ...args);
    }

    error (...args) {
        console.error.call(console, '%c[VK Flex]', 'font-weight: bold;', ...args);
    }

    warn (...args) {
        console.warn.call(console, '%c[VK Flex]', 'color: #bb7d0b; font-weight: bold;', ...args);
    }

    info (...args) {
        console.info.call(console, '%c[VK Flex]', 'color: blue; font-weight: bold;', ...args);
    }

    initObserver () {
        this.subscribe({
            name: 'injection',
            events: {
                addedNodes: { callback: this.onAddNode, context: this },
                removedNodes: { callback: this.onRemoveNode, context: this }
            } 
        });

        this.observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                [ 'addedNodes', 'removedNodes' ].forEach((eventType) => {
                    mutation[eventType].forEach((node) => {
                        if (/^html.*element$/.test(this.getType(node)) && !node.vkfSkip) {
                            this.triggerEvent(eventType, node, mutation);
                        }
                    });
                });
            });
        });

        this.observer.observe(document.body, { 
            childList: true, 
            subtree: true
        });

        this.checkLocation();

        this.triggerEvent('addedNodes', document.body, {});
    }

    checkLocation () {
        if (window.location.href !== this.cache.lastLocationHref) {
            this.cache.lastLocationHref = window.location.href;
            this.triggerEvent('onLocationChanged', Object.assign({}, window.location));
        }

        requestAnimationFrame(() => this.checkLocation());
    }

    subscribe (options) {
        for (let eventType in options.events) {
            this.hooks[eventType].push({
                name: options.name,
                callback: options.events[eventType].callback,
                context: options.events[eventType].context
            });
        }        
    }

    onAddNode (node, mutation) {
        let sidebar = node.id == 'side_bar' ? node : node.querySelector('#side_bar');

        if (sidebar && sidebar !== this.cache.sidebar) {
            this.cache.sidebar = sidebar;
            this.triggerEvent('onSidebarChanged', sidebar);
        }
    }

    onRemoveNode (node, mutation) {

    }

    triggerEvent (eventType, ...handlerArgs) {
        this.hooks[eventType].forEach((hook) => {
            hook.callback.call(hook.context, ...handlerArgs);
        });
    }

    triggerDomEvent (target, eventType) {
        target.dispatchEvent(new Event(eventType));
    }

    loadModules () {
        // TODO: Calendar & URL Shortener disappear when user changes visibility of menu items

        // Left menu fix
        if (this.settings.fix_menu) {
            document.documentElement.classList.add('vkf-fixed-menu');
        }

        // Hide potential friends
        if (this.settings.hide_potential_friends) {
            document.documentElement.classList.add('vkf-hide-potential-friends');
        }

        // Hide big like in photo gallery
        if (this.settings.hide_photo_like) {
            document.documentElement.classList.add('vkf-hide-photo-like');            
        }

        // Calendar
        if (this.settings.add_calendar) {
            this.modules.calendar = new Calendar(this);
        }

        // Url shortener
        if (this.settings.url_shortener) {
            this.modules.urlShortener = new UrlShortener(this);
        }

        if (this.settings.simplify_audio_ui) {
            this.modules.audioUiSimplifier = new AudioUiSimplifier(this);
        }

        // Video
        if (this.settings.video_downlink) {
            this.modules.videoProcessor = new VideoProcessor(this);
        }

        // Middlename field
        if (this.settings.add_middlename) {
            this.modules.middlenameField = new MiddlenameField(this);            
        }

        // Link "My video"
        if (this.settings.change_videos_link) {
            this.modules.myVideoLink = new MyVideoLink(this); 
        }

        // Ads Shredder
        if (this.settings.hide_advert) {
            this.modules.adsShredder = new AdsShredder(this);  
        }

        this.hpc = () => {
            this.modules.adsShredder && this.modules.adsShredder.hpc();
        };

        // Age and zodiac
        if (this.settings.show_user_age || this.settings.show_user_zodiac) {
            this.modules.userAgeAndZodiac = new UserAgeAndZodiac(this); 
        }

        // Away.php
        if (this.settings.skip_redirect) {
            this.modules.awaySkip = new AwaySkip(this); 
        }

        this.modules.hideMusicCurators = new HideMusicCurators(this); 
        this.modules.clearMusicLinks = new ClearMusicLinks(this); 

        // Force redraw
        requestAnimationFrame(() => this.triggerDomEvent(window, 'scroll'));
    }

    coreMessage (...args) { // action, data, callback
        window.chrome.runtime.sendMessage(
            this.extensionId, 
            Object.assign({ _action: args[0] }, this.isObj(args[1]) ? args[1] : {}), 
            this.isFunc(args[1]) ? args[1] : (this.isFunc(args[2]) ? args[2] : () => {})
        );
    }

    lang (key) {
        return (key in this.langData) ? this.langData[key] : key;
    }

    clearFileTitle (title) {
        let htmlFilter = document.createElement('div');
        htmlFilter.innerHTML = title;
        return htmlFilter.innerText.replace(/[\\\/:\*\?"<>\|]/g, '').trim().replace(/\s+/g, ' ');
    }

    formatSize (bytes) {
        let size = '';

        if (bytes < 1000) {
            size = bytes + ' ' + this.lang('units_b');
        } else if (bytes < 943718) {
            size = (Math.round(bytes / 1024 * 10) / 10).toFixed(1) + ' ' + this.lang('units_kb');
        } else if (bytes < 966367642) {
            size = (Math.round(bytes / 1048576 * 10) / 10).toFixed(1) + ' ' + this.lang('units_mb');
        } else {
            size = (Math.round(bytes / 1073741824 * 10) / 10).toFixed(2) + ' ' + this.lang('units_gb');
        }

        return size;
    }

    bindEventHandler (target, eventFullName, handler, context) {
        let handlerWrap = (event) => {
            if (handler.call(context, event, target) === false) {
                event.preventDefault();
                event.stopPropagation();
            }                
        };

        let [ eventName, eventNamespace ] = eventFullName.split('.');

        // Link handler with node for future unbind
        if (eventNamespace) {
            !target.vkfEventsMap && (target.vkfEventsMap = {});
            target.vkfEventsMap[eventFullName] = handlerWrap;
        }

        return target.addEventListener(eventName, handlerWrap, false);
    }

    unbindEventHandler (target, eventFullName) {
        let [ eventName, eventNamespace ] = eventFullName.split('.');

        if (!eventNamespace) {
            this.warn('unbindEventHandler: only events with namespace can be unbinded');
            return;
        }

        let handler = (target.vkfEventsMap || {})[eventFullName];
        handler && target.removeEventListener(eventName, handler, false);
    }

    downloadFile (e, target) {
        e.stopPropagation();

        switch (e.type) {
            case 'click':
                e.preventDefault();

                if (target.href) {
                    this.coreMessage('downloadFile', {
                        href: target.href,
                        download: target.download || ''
                    });
                }

                break;

            case 'dragstart':
                if (target.tagName.toLowerCase() != 'a') {
                    target = target.querySelector('a');
                }

                if (target && target.href) {
                    let mimeType = target.dataset.type,
                        filename = target.download || target.href.split('/').pop();

                    if (mimeType) {
                        e.dataTransfer.setData('DownloadURL', `${mimeType}:${filename}:${target.href}`);
                    }
                }

                break;
        }
    }

    inArray (item, array) {
        return array.indexOf(item) !== -1;
    }

    createNode (model, parent) {
        let node;

        if (model.tag) {
            node = document.createElement(model.tag);
            delete model.tag;

            for (let key in model) {
                let val = model[key];

                if (this.inArray(key, ['href', 'id', 'innerHTML', 'innerText'])) {
                    node[key] = val;
                } else if (key == 'class') {
                    node.className = Array.isArray(val) ? val.join(' ') : val;
                } else if (key == 'child') {
                    val = Array.isArray(val) ? val : [val];
                    val.forEach((childModel) => this.createNode(childModel, node));
                } else if (key == 'data') {
                    for (let dataKey in val) {
                        node.dataset[dataKey] = val[dataKey];
                    }
                } else if (key == 'events') {
                    val.forEach((eventOptions) => this.bindEventHandler(node, ...eventOptions));
                } else {
                    node.setAttribute(key, val); 
                }
            }

            // Add this flag to all nodes created by VK Flex
            // Mutation observers will skip these nodes
            node.vkfSkip = true;
        } else if ('text' in model) {
            node = document.createTextNode(model.text);
        }

        parent && parent.appendChild(node);

        return node;
    };

    prependNode (parentNode, childNode) {
        parentNode = this.isObj(parentNode) ? this.createNode(parentNode) : parentNode;
        childNode = this.isObj(childNode) ? this.createNode(childNode) : childNode;
        parentNode.insertBefore(childNode, parentNode.firstChild);
    }

    inputSelectAll (input) {
        input.setSelectionRange(0, input.value.length);
    }

    makeNodeInvisible (node) {
        node.removeAttribute('style');
        node.dataset.invisibleNode = 'true';
    }
}

class HideMusicCurators {
    constructor (app) {
        this.app = app;
    }

}

class ClearMusicLinks {
    constructor (app) {
        this.app = app;

        this.app.subscribe({
            name: 'clearMusicLinks',
            events: {
                addedNodes: { callback: this.onCheckTabs, context: this }
            } 
        });

        this.onCheckTabs(document.body);
    }

    onCheckTabs (el) {
        const selector = '.audio_page_content_block_wrap .page_block_h2 .ui_tabs_container > ._audio_section_tab__my:not(.vkf-has-playlists)';
        const myTab = el.matches(selector) ? el : el.querySelector(selector); 

        if (!myTab) {
            return;
        }

        myTab.classList.add('vkf-has-playlists');

        const myLink = myTab.querySelector(':scope > a.ui_tab');

        if (!myLink) {
            return;
        }

        const url = new URL(myLink.href);

        url.searchParams.set('block', 'my_playlists');
        // url.searchParams.delete('section');

        myTab.insertAdjacentHTML('afterend', `<li class="_audio_section_tab _audio_section_tab__all">
            <a href="${ url.href }" class="ui_tab ui_tab_new" onclick="return nav.go(this, event);">
                <span class="ui_tab_content_new">ѕлейлисты</span>
            </a>
        </li>`);
    }
}

class AwaySkip {
    constructor (app) {
        this.app = app;
    
        this.app.subscribe({
            name: 'awaySkip',
            events: {
                addedNodes: { callback: this.onAddNode, context: this }
            } 
        });
    }

    clearLink (anchor) {
        if (anchor.href.toLowerCase().includes('utf')) {
            console.warn(anchor.href);
        }

        let href = anchor.href.match(/(?:\?|&)to=([^\?&]*)/);

        if (href) {
            try {
                href = decodeURIComponent(href[1]);
            } catch (e) {
                this.app.warn('[AwaySkip.clearLink]', 'Cant\'t decodeURIComponent href:', anchor.href);
                return;
            }

            if (href.indexOf('://') != -1) {
                anchor.href = href;
            }            
        }
    }

    onAddNode (node) {
        if (node.href && node.href.startsWith('/away.php')) {
            this.clearLink(hode);
        }

        node.querySelectorAll("a[href^='/away.php']").forEach((anchor) => {
            this.clearLink(anchor);
        });      
    }
}

class AudioUiSimplifier {
    constructor (app) {
        this.app = app;

        this.app.subscribe({
            name: 'audioUiSimplifier',
            events: {
                onLocationChanged: { callback: this.onLocationChanged, context: this }
            } 
        });
    }

    onLocationChanged (location) {
        if (!(/^\/(audio|audios\-?\d+)$/.test(location.pathname) || window.cur && window.cur.module == 'audio')) {
            return;
        }

        const layout = document.querySelector('.audio_page_layout');

        if (!layout) {
            return;
        }

        layout.classList.add('vkf-simplified-ui');

        const playlists = layout.querySelector('.audio_page_layout.vkf-simplified-ui > .audio_page_content_block_wrap > ._audio_page_content_block > .audio_page_sections > .audio_section__all ._audio_page__playlists');

        if (playlists && playlists.parentNode.classList.contains('_audio_page_titled_block')) {
            const sep = playlists.parentNode.nextElementSibling;

            sep && sep.classList.contains('audio_page_separator') && sep.remove();
            playlists.parentNode.remove();
        }
    }
}

class UserAgeAndZodiac {
    constructor (app) {
        this.app = app;

        this.screenName = null;

        this.app.subscribe({
            name: 'userAgeAndZodiac',
            events: {
                onLocationChanged: { callback: this.onLocationChanged, context: this }
            } 
        });
    }

    onLocationChanged (location) {
        let urlParts = location.pathname.match(/[^\/]+/g);

        if (urlParts && urlParts.length == 1) {
            let screenName = this.screenName = urlParts[0],
                profileRowsWrap = document.body.querySelector('#profile #profile_short');

            if (profileRowsWrap && !profileRowsWrap.vkfAgeAndZodiac) {
                profileRowsWrap.vkfAgeAndZodiac = true;

                this.app.coreMessage(
                    'getUserAge', 
                    { 
                        screenName: screenName
                    }, 
                    (birthday) => {
                        if (birthday && this.screenName == screenName) {
                            let [ day, month, year ] = birthday.split('.').map((num) => Number(num));

                            // Zodiac
                            if (this.app.settings.show_user_zodiac && day && month && !profileRowsWrap.querySelector('[data-zodiac]')) {
                                this.showZodiac(profileRowsWrap, day, month);
                            }

                            // Age
                            if (this.app.settings.show_user_age && day && month && year && !profileRowsWrap.querySelector('[data-age]')) {
                                this.showAge(profileRowsWrap, day, month, year);
                            }
                        }
                    }
                );
            }
        } else {
            this.screenName = null;
        }
    }

    showZodiac (profileRowsWrap, day, month) {
        let zodiac = null;

             if (month == 12 && day > 21 || month == 1  && day < 20) { zodiac = 1;  }
        else if (month == 1  && day > 19 || month == 2  && day < 19) { zodiac = 2;  }   
        else if (month == 2  && day > 18 || month == 3  && day < 21) { zodiac = 3;  }
        else if (month == 3  && day > 20 || month == 4  && day < 20) { zodiac = 4;  }
        else if (month == 4  && day > 19 || month == 5  && day < 21) { zodiac = 5;  }
        else if (month == 5  && day > 20 || month == 6  && day < 22) { zodiac = 6;  }
        else if (month == 6  && day > 21 || month == 7  && day < 23) { zodiac = 7;  }
        else if (month == 7  && day > 22 || month == 8  && day < 23) { zodiac = 8;  }
        else if (month == 8  && day > 22 || month == 9  && day < 23) { zodiac = 9;  }
        else if (month == 9  && day > 22 || month == 10 && day < 23) { zodiac = 10; }
        else if (month == 10 && day > 22 || month == 11 && day < 22) { zodiac = 11; }
        else if (month == 11 && day > 21 || month == 12 && day < 22) { zodiac = 12; }

        if (zodiac) {
            this.app.prependNode(
                profileRowsWrap,
                {
                    tag: 'div',
                    class: [ 'clear_fix', 'profile_info_row' ],
                    data: { zodiac: 'true' },
                    child: [
                        {
                            tag: 'div',
                            class: 'label fl_l',
                            innerHTML: this.app.lang('profile_label_zodiac') + ':'
                        },
                        {
                            tag: 'div',
                            class: 'labeled',
                            innerHTML: this.app.lang('zodiac_' + zodiac)                                               
                        }
                    ]
                }
            );                                    
        }
    }

    showAge (profileRowsWrap, day, month, year) {
        let ageCases = this.app.lang('profile_age').split('|'),
            currentDate = new Date(),
            age = (currentDate.getFullYear() - year - ((currentDate.getMonth() - --month || currentDate.getDate() - day) < 0)),
            ageCase = (age % 10 == 0 || age % 10 >= 5 && age % 10 <= 9 || age % 100 >= 5 && age % 100 <= 20) ? 0 : (age % 10 == 1 ? 1 : 2);

        this.app.prependNode(
            profileRowsWrap,
            {
                tag: 'div',
                data: { age: 'true' },
                class: [ 'clear_fix', 'profile_info_row' ],
                child: [
                    {
                        tag: 'div',
                        class: 'label fl_l',
                        innerHTML: this.app.lang('profile_label_age') + ':'
                    },
                    {
                        tag: 'div',
                        class: 'labeled',
                        child: {
                            tag: 'a',
                            href: `/search?c[section]=people&c[age_from]=${age}`,
                            innerHTML: age + ' ' + ageCases[ageCase]
                        }
                                                                     
                    }
                ]
            }
        ); 
    }
}

class AdsShredder {
    static get SELECTORS () {
        const removeAudioSepFn = (el, ancEl) => {
            if (ancEl && ancEl.nextElementSibling && ancEl.nextElementSibling.matches('.CatalogBlock__separator')) {
                ancEl.nextElementSibling.remove();
            }
        };

        return [
            [ '.apps_feedRightAppsBlock' ],
            [ `[class*='_recommend_apps']` ],
            [ '.feed_friends_recomm' ],
            [ '.profile_friends_recomm' ],
            [ '.CatalogBlock__header_promo_banners', '.CatalogSection' ],
            [ '.page_block.post_marked_as_ads' ],
            [ '.page_block .wall_marked_as_ads', '.page_block' ],
            [ '._ads_block_data_w, .ads_ads_news_wrap', '.feed_row, .feed_row_unshown' ],
            [ '.page_block #group_recom_wrap', '.page_block' ],
            [ '#stories_feed_wrap' ],
            [ '#side_bar #ads_left' ],
            [ '#ads_special_promo_wrap' ],
            [ '.CatalogBlock__my_curators_header', '.CatalogBlock' ],
            [ '.CatalogBlock__my_curators', '.CatalogBlock' ],
            [ '.CatalogSection__my .CatalogBlock__my_playlists', '.CatalogBlock' ],
            [ '.CatalogBlock.CatalogBlock--separator' ],
            [ '.CatalogBlock__subscription_banners' ],
            [ '.CatalogBlock__recent_audios', '.CatalogBlock' ],
            [ '#block_aliexpress-recommendations-carousel', '.feed_row' ],
            [ '[href="/video-211229778_456239494"]', '[class*="GridItem-module__root"]' ],
            [ '[href="/video-211229778_456239493"]', '[class*="GridItem-module__root"]' ],
            [ '[href="/video-110135406_456243055"]', '[class*="GridItem-module__root"]' ],
            [ '[href="/video-110135406_456243061"]', '[class*="GridItem-module__root"]' ],
        ];
    }

    static get SELECTORS2 () {
        return [
            [ `//span[@class='PostHeaderSubtitle__item'][contains(., '–еклама')]`, '.feed_row' ],
        ];
    }

    constructor (app) {
        this.app = app;

        this.app.subscribe({
            name: 'adsShredder',
            events: {
                onSidebarChanged: { callback: this.onSidebarChanged, context: this },
                addedNodes: { callback: this.onAddNode, context: this }
            } 
        });

        this.disableAudioAds();
        this.hpc_check();
    }

    hpc () {        
        window.localStorage.setItem('vkf_hpc', '1');
        this.hpc_check();
    }

    hpc_check () {
        if (window.localStorage.getItem('vkf_hpc')) {
            document.documentElement.classList.add('vkf-hide-post-comments');
        }
    }

    disableAudioAds () {
        if (!window.AudioPlayer) {
            return setTimeout(() => this.disableAudioAds(), 3000);
        }

        const AP = window.AudioPlayer;

        AP.prototype._adsIsAllowed = (window.ap || {})._adsIsAllowed = function () { 
            return {
                type: 'ADS_ALLOW_DISABLED' in AP ? AP.ADS_ALLOW_DISABLED : 1
            }; 
        };
    }

    // Ads in sidebar
    onSidebarChanged (sidebar) {
        if (sidebar) {
            const ads = sidebar.querySelector('#ads_left');
            ads && ads.remove();
        }
    }

    // Ads in feed
    onAddNode (node) {
        AdsShredder.SELECTORS.forEach(([ sel, ancSel, customFn ]) => {
            const nodes = node.matches(sel) ? [ node ] : Array.from(document.querySelectorAll(sel));

            nodes.forEach((el) => {
                // if (el.matches('.audio_promo')) {
                //     const closeEl = el.querySelector('.BannerItem__close');

                //     if (closeEl) {
                //         closeEl.click();
                //         return;
                //     }
                // }

                const ancEl = ancSel && el.closest(ancSel) || null;

                customFn && customFn(el, ancEl);

                (ancEl || el).remove();
            });
        });

        AdsShredder.SELECTORS2.forEach(([ sel, ancSel ]) => {
            const els = document.evaluate(sel, node, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);

            for (let i = 0; i < els.snapshotLength; i++) {
                const el = els.snapshotItem(i);
                const ancEl = ancSel && el.closest(ancSel) || null;

                ancEl?.remove();
            }
        });
    }
}

class MyVideoLink {
    constructor (app) {
        this.app = app;

        this.observer = null;

        this.app.subscribe({
            name: 'myVideoLink',
            events: {
                onSidebarChanged: { callback: this.onSidebarChanged, context: this }
            } 
        });
    }

    onSidebarChanged (sidebar) {
        if (sidebar) {
            let anchor = sidebar.querySelector('#l_vid > a');

            if (anchor) {
                anchor.href = '/video/subscriptions';
            }

            if ((anchor = sidebar.querySelector('#l_aud > a'))) {
                anchor.href += (anchor.href.includes('?') ? '&' : '?') + 'section=all';
            }

            this.setObserver(sidebar);
        }
    }

    setObserver (sidebar) {
        this.observer && this.observer.disconnect();

        this.observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.target.parentNode.id == 'l_vid') {
                    if (mutation.target.href.indexOf('/videos') == -1) {
                        mutation.target.href = '/videos';
                    }
                } else if (mutation.target.parentNode.id == 'l_aud') {
                    mutation.target.href += (mutation.target.href.includes('?') ? '&' : '?') + 'section=all';
                }
            });
        });

        this.observer.observe(sidebar, { 
            attributes: true, 
            subtree: true,
            attributeFilter: [ 'href' ]
        });
    }
}

class MiddlenameField {
    constructor (app) {
        this.app = app;
    
        this.app.subscribe({
            name: 'middlenameField',
            events: {
                addedNodes: { callback: this.onAddNode, context: this }
            } 
        });
    }

    onAddNode (node) {
        let lastNameRow = node.querySelector('input#pedit_last_name');

        if (lastNameRow) {
            lastNameRow = lastNameRow.closest('.pedit_row');

            if (!lastNameRow.parentNode.querySelector('input#pedit_middle_name')) {
                lastNameRow.parentNode.insertBefore(
                    this.app.createNode({
                        tag: 'div',
                        class: [ 'pedit_row', 'clear_fix' ],
                        child: [
                            {
                                tag: 'div',
                                class: 'pedit_label',
                                innerText: this.app.lang('middlename_label') + ':'
                            },
                            {
                                tag: 'div',
                                class: 'pedit_labeled',
                                child: {
                                    tag: 'input',
                                    class: 'dark',
                                    id: 'pedit_middle_name',
                                    type: 'text',
                                    autocomplete: 'off'
                                }
                            }
                        ]
                    }),
                    lastNameRow.nextSibling
                );
            }
        }        
    }
}

class VideoProcessor {
    // static get QUALITIES () {
    //     return [ 240, 360, 480, 720, 1080 ];
    // }

    constructor (app) {
        this.app = app;

        this.videoId = null;
        this.videoWrap = null;
        this.prevVideoId = null;
        this.linksNode = null;
        this.layerNode = null;

        this.app.subscribe({
            name: 'videoProcessor',
            events: {
                onLocationChanged: { 
                    callback: this.onLocationChanged, 
                    context: this 
                }
            } 
        });
    }

    extractVideoExtension (url, defaultValue = '.mp4') {
        return (url.match(/^.*(\.\w+)(?:\?.*)?$/) || [ null, defaultValue ])[1];
    }

    extractVideoQuality (url, defaultValue = 720) {
        return Number((url.match(/^.*\.(\d+)\.\w+(?:\?.*)?$/) || [ null, defaultValue ])[1]);
    }

    onLocationChanged (location) {
        let videoIdMatch = location.href.match(/(?:\/|=)video(\-?\d+_\d+)/);

        this.videoWrap = null;

        if (this.linksNode) {
            this.linksNode.remove();
            this.linksNode = null;
        }

        if (this.layerNode) {
            this.app.unbindEventHandler(this.layerNode, 'scroll.layerScroll');
            this.layerNode = null;
        }

        if (videoIdMatch) {
            this.prevVideoId = this.videoId || null;
            this.videoId = videoIdMatch[1];
            setTimeout(() => this.findVideoBoxWrap(), 0); // fork
        } else {
            this.prevVideoId = null;
            this.videoId = null;
        }
    }

    findVideoBoxWrap () {
        if (!this.videoId) {
            return;
        }

        let videoWrap = document.querySelector('.video_box_wrap'),
            videoWrapId = videoWrap && videoWrap.id || '';

        if (videoWrap && (!this.prevVideoId || this.prevVideoId && videoWrapId.indexOf(this.prevVideoId) === -1)) {
            if (videoWrapId.indexOf(this.videoId) !== -1) {
                this.videoWrap = videoWrap;
                this.findVideoVars();
            }
        } else {
            if (!document.querySelector('.mv_video_unavailable_message_wrap')) { // !claimed
                setTimeout(() => this.findVideoBoxWrap(), 50);
            }
        }
    }

    findVideoVars () {
        if (!this.videoId) {
            return;
        }

        let videoVars = null;

        try { videoVars = mvcur.player.getVars(); } catch (e) {}

        if (videoVars && this.videoId == ((videoVars.oid || '') + '_' + (videoVars.vid || ''))) {
            this.processVideoVars(videoVars);
        } else {
            setTimeout(() => this.findVideoVars(), 50);
        }
    }

    /*
    async showHls (videoVars) {
        const hlsUrl = videoVars?.hls;

        if (!hlsUrl) {
            console.warn('No videoVars.hls found:', videoVars);
            return;
        }

        const response = await fetch(hlsUrl, {
            method: 'GET',
            mode: 'cors',
            credentials: 'omit'
        }).then((response) => {
            return response.text();
        }).catch((e) => {
            console.warn('Failed to get hls', e, videoVars);
            return null;
        });

        if (!response) {
            return;
        }

        const lines = response.split('\n');

        let sources = [];
        let params = null;

        for (let line of lines) {
            line = line.trim();

            if (!line) {
                continue;
            }

            if (params) {
                params.url = this.getAbsQualityUrl(hlsUrl, line);

                sources.push(params);

                params = null;
            } else if (line.startsWith('#EXT-X-STREAM-INF:')) {
                const pairs = line.slice(18).split(',').map((pair) => {
                    return pair.split('=');
                });

                params = {};

                for (let [ key, value ] of pairs) {
                    switch (key) {
                        case 'BANDWIDTH':
                            value = Number(value);
                            break;
                        case 'RESOLUTION':
                            value = value.split('x').map(n => Number(n));
                            break;
                        default:
                            continue;
                    }

                    params[key.toLowerCase()] = value;
                }

                params.score = (BigInt(params.resolution[0] * params.resolution[1]) << BigInt(64)) | BigInt(params.bandwidth); 
            }
        }

        sources = sources.sort((a, b) => {
            const z = BigInt(0);
            const r = a.score - b.score;

            if (r < z) {
                return -1;
            } else if (r > z) {
                return 1;
            }

            return 0;
        });

        const out = [ null ];
        const info = [];
        const title = videoVars.md_title;

        info.push(' ');

        if (title) {
            out.push('font-size: 18px; line-height: 26px; font-weight: bold; color: #ee3333;');

            info.push(`%c${ title }`);
        }

        sources.forEach(({ resolution, url }) => {
            const y = String(resolution[1]).padStart(4);

            out.push(
                'font-size: 18px; line-height: 26px; font-weight: bold; color: #ee3333;',
                'font-size: 16px; line-height: 26px; font-weight: normal; color: inherit;'
            );

            info.push(`%c${ y }p %c${ url }`);
        });
        
        info.push(' ');

        out[0] = info.join('\n');

        console.log(...out);
    }*/

    getAbsQualityUrl (masterUrl, qualityUrl) {
        // if (/^https?:\/\//i.test(qualityUrl.toLowerCase())) {
        //     return qualityUrl;
        // }

        return String(new URL(qualityUrl, masterUrl));
        
        /*
        masterUrl  = new URL(masterUrl);
        qualityUrl = new URL(qualityUrl, masterUrl.origin);
        */

        // const path = masterUrl.pathname
        //     .replace(/\/+$/, '')
        //     .split('/')
        //     .slice(0, -1)
        //     .join('/');

        // masterUrl.pathname = path + qualityUrl.pathname;

        /*
        const params = qualityUrl.pathname
            .replace(/^\/+|\/+$/g, '')
            .split('/');

        const maxParam = Math.trunc(params.length / 2) * 2;
        const paramMap = {};

        for (let i = 0; i < maxParam; i += 2) {
            paramMap[params[i]] = params[i + 1];
        }

        for (let [ key, value ] of masterUrl.searchParams.entries()) {
            if (key in paramMap) {
                continue;
            }

            if (qualityUrl.searchParams.has(key)) {
                continue;
            }

            if ([ 'cmd' ].includes(key)) {
                continue;
            }

            qualityUrl.searchParams.set(key, value);
        }

        return qualityUrl.toString();
        */
    }

    /*
    #EXTM3U
    #EXT-X-VERSION:3
    #EXT-X-INDEPENDENT-SEGMENTS
    #EXT-X-STREAM-INF:QUALITY=mobile,BANDWIDTH=212992,RESOLUTION=256x144,FRAME-RATE=25.000,CODECS="avc1.42001e,mp4a.40.2"
    CP6VxMDXigESFAj-lcTA14oBEP6VxMDXigEYNyABGhQI_pXEwNeKARD-lcTA14oBGDcgAiABMAM4Anj1A6oBCAoGCIACEJABsgEECMTYAtIBBBACKBfaAQIICJhWC886rOKm/fn/track.m3u8
    #EXT-X-STREAM-INF:QUALITY=lowest,BANDWIDTH=538112,RESOLUTION=424x240,FRAME-RATE=25.000,CODECS="avc1.42001e,mp4a.40.2"
    CP6VxMDXigESFAj-lcTA14oBEP6VxMDXigEYNyABGhQI_pXEwNeKARD-lcTA14oBGDcgAiACKAEwAzgCePUDqgEICgYIqAMQ8AGyAQQIxNgC0gEEEAIoF9oBAggQ__MAQM-MNYc/fn/track.m3u8
    #EXT-X-STREAM-INF:QUALITY=low,BANDWIDTH=1052672,RESOLUTION=640x360,FRAME-RATE=25.000,CODECS="avc1.42001e,mp4a.40.2"
    CP6VxMDXigESFAj-lcTA14oBEP6VxMDXigEYNyABGhQI_pXEwNeKARD-lcTA14oBGDcgAiADKAIwAzgCePUDqgEICgYIgAUQ6AKyAQQIxNgC0gEEEAIoF9oBAggQ1Vnud6W5vB4/fn/track.m3u8
    #EXT-X-STREAM-INF:QUALITY=medium,BANDWIDTH=1774592,RESOLUTION=856x480,FRAME-RATE=25.000,CODECS="avc1.4d001e,mp4a.40.2"
    CP6VxMDXigESFAj-lcTA14oBEP6VxMDXigEYNyABGhQI_pXEwNeKARD-lcTA14oBGDcgAiAEKAMwAzgCePUDqgEICgYI2AYQ4AOyAQQIxNgC0gEGCAEQAigX2gECCBBiMPxLW1T4YQ/fn/track.m3u8
    #EXT-X-STREAM-INF:QUALITY=high,BANDWIDTH=3883008,RESOLUTION=1280x720,FRAME-RATE=25.000,CODECS="avc1.64001f,mp4a.40.2"
    CP6VxMDXigESFAj-lcTA14oBEP6VxMDXigEYNyABGhQI_pXEwNeKARD-lcTA14oBGDcgAiAFKAQwAzgCePUDqgEICgYIgAoQ0AWyAQQIxNgC0gEGCAMQAigX2gECCBj1-K5W_8fxaA/fn/track.m3u8
    #EXT-X-STREAM-INF:QUALITY=fullhd,BANDWIDTH=5436671,RESOLUTION=1920x1080,FRAME-RATE=25.000,CODECS="avc1.4d0028,mp4a.40.2"
    CP6VxMDXigESFAj-lcTA14oBEP6VxMDXigEYNyABGhQI_pXEwNeKARD-lcTA14oBGDcgAiAGKAUwAzgCePUDXp1JtsY6o2o/fn/track.m3u8

    https://vkvd477.mycdn.me/srcIp/5.165.172.20/expires/1706590072409/srcAg/CHROME/fromCache/1/ms/185.226.53.221/mid/5837150824702/type/2/sig/ptIs3c0wXrA/ct/28/urls/45.136.20.169/clientType/13/id/4765133114110/ondemand/hls4_4765133114110.CP7RtIrxqQE4mcayoAJIj-CCl_______AVAoWA0EoDHVxB0PrQ%3D%3D.m3u8
    */
    async getHlsLinks (videoVars) {
        const hlsUrl = videoVars?.hls || videoVars?.hls_ondemand;

        console.log('getHlsLinks', hlsUrl);

        if (!hlsUrl) {
            console.warn('No videoVars.hls found:', videoVars);
            return [];
        }

        const response = await fetch(hlsUrl, {
            method: 'GET',
            mode: 'cors',
            credentials: 'omit'
        }).then((response) => {
            return response.text();
        }).catch((e) => {
            console.warn('Failed to get hls', e, videoVars);
            return null;
        });

        if (!response) {
            return [];
        }

        const lines = response.split('\n');

        let sources = [];
        let params = null;

        for (let line of lines) {
            line = line.trim();

            if (!line) {
                continue;
            }

            if (params) {
                params.url = this.getAbsQualityUrl(hlsUrl, line);

                sources.push(params);

                params = null;
            } else if (line.startsWith('#EXT-X-STREAM-INF:')) {
                const pairs = line.slice(18).split(',').map((pair) => {
                    return pair.split('=');
                });

                params = {};

                for (let [ key, value ] of pairs) {
                    switch (key) {
                        case 'BANDWIDTH':
                            value = Number(value);
                            break;
                        case 'RESOLUTION':
                            value = value.split('x').map(n => Number(n));
                            break;
                        default:
                            continue;
                    }

                    params[key.toLowerCase()] = value;
                }

                params.score = (BigInt(params.resolution[0] * params.resolution[1]) << BigInt(64)) | BigInt(params.bandwidth); 
            }
        }

        sources = sources.sort((a, b) => {
            const z = BigInt(0);
            const r = a.score - b.score;

            if (r < z) {
                return -1;
            } else if (r > z) {
                return 1;
            }

            return 0;
        });

        return sources.map(({ url, resolution }) => {
            return {
                url,
                quality: resolution[1]
            };
        });        
    }

    async processVideoVars (videoVars) {
        if (!this.videoId) {
            return;
        }

        // this.showHls(videoVars);
        const hlsLinks = await this.getHlsLinks(videoVars);

        console.log(hlsLinks);

        let qualities = [];

        let title = 
            this.app.clearFileTitle(
                videoVars.md_title ||
                this.videoWrap.closest('#mv_box').querySelector('#mv_title').innerText ||
                'Untitled'
            );

        const resolutions = Object.keys(videoVars).reduce((acc, key) => {
            const match = key.match(/^(?:url|cache)(\d+)$/);

            if (match) {
                const quality = Number(match[1]);

                if (!acc.includes(quality)) {
                    acc.push(quality);
                }
            }
            
            return acc;
        }, []);

        resolutions.sort((a, b) => a - b);

        resolutions.forEach((quality) => {
            let url = videoVars['url' + quality] || videoVars['cache' + quality];

            if (url) {
                qualities.push({
                    quality: quality,
                    filename: title + this.extractVideoExtension(url),
                    url: url,
                    size: null,
                    hlsUrl: null
                });
            }
        });

        if (!qualities.length && videoVars.postlive_mp4) {
            let url = videoVars.postlive_mp4;

            qualities.push({
                quality: this.extractVideoQuality(url),
                filename: title + this.extractVideoExtension(url),
                url: url,
                size: null,
                hlsUrl: null
            });
        }

        hlsLinks.forEach(({ url, quality }) => {
            const item = qualities.find(info => {
                return Math.abs(info.quality - quality) <= 10;
            });

            if (item) {
                item.hlsUrl = url;
            } else {
                qualities.push({
                    quality,
                    filename: null,
                    url: null,
                    size: null,
                    hlsUrl: url
                });
            }
        });

        qualities.sort((a, b) => a.quality - b.quality);

        if (qualities.length) {
            let playerNode = this.videoWrap.closest('#mv_main');

            if (this.app.settings.video_show_size) {
                let requestCount = qualities.filter(q => q.url).length;

                if (requestCount) {                    
                    qualities.forEach((quality) => {
                        if (!quality.url) {
                            return;
                        }

                        this.app.coreMessage(
                            'getFileSize', 
                            { 
                                url: quality.url 
                            }, 
                            (size) => {
                                quality.size = size;

                                if (!--requestCount) {
                                    this.showVideoLinks(playerNode, qualities);
                                }
                            }
                        );
                    });
                } else {
                    this.showVideoLinks(playerNode, qualities);
                }
            } else {
                this.showVideoLinks(playerNode, qualities);
            }
        }
    }

    showVideoLinks (playerNode, qualities) {
        if (!this.videoId) {
            return;
        }

        // ---------------------

        const root = document.createElement('div');

        root.className = 'video-dl';

        qualities.forEach((quality) => {
            const q = document.createElement('div');

            q.className = 'video-dl__quality';

            const hasMP4 = !!quality.url;

            const mp4 = hasMP4 ? document.createElement('a') : document.createElement('span');

            mp4.className = 'video-dl__link video-dl__mp4';

            if (hasMP4) {
                mp4.href = quality.url;
                mp4.download = quality.filename;
            } else {
                mp4.classList.add('video-dl__link_disabled');
            }

            const res = document.createElement('span');

            res.className = 'video-dl__mp4-res';
            res.innerHTML = quality.quality + 'p';

            mp4.appendChild(res);

            if (this.app.settings.video_show_size) {
                const size = document.createElement('span');

                size.className = 'video-dl__mp4-size';

                if (quality.size === null) {
                    size.innerHTML = 'Ц.ЦЦ ћб';
                } else {
                    size.innerHTML = this.app.formatSize(quality.size);
                }

                mp4.appendChild(size);
            }

            q.appendChild(mp4);

            if (quality.hlsUrl) {            
                const hls = document.createElement('a');

                hls.className = 'video-dl__link video-dl__hls';
                hls.href = quality.hlsUrl;
                hls.innerHTML = 'HLS';

                hls.addEventListener('click', (e) => {
                    e.preventDefault();
                    copyText(quality.hlsUrl);
                });

                q.appendChild(hls);
            }

            root.appendChild(q);
        });

        playerNode.appendChild(root);

        this.layerNode = playerNode.closest('#mv_layer_wrap');

        this.app.bindEventHandler(this.layerNode, 'scroll.layerScroll', (e) => {
            let playerNodeRect = playerNode.getBoundingClientRect();

            if (playerNodeRect.top <= 0) {
                if (!root.classList.contains('video-dl_sticky')) {
                    let linksNodeRect = root.getBoundingClientRect();
                    root.style.width = linksNodeRect.width + 'px';
                    root.style.top = linksNodeRect.top + 'px';
                    root.style.right = 'auto';
                    root.style.left = playerNodeRect.right + 'px';
                    root.classList.add('video-dl_sticky');
                }
            } else {
                if (root.classList.contains('video-dl_sticky')) {
                    root.classList.remove('video-dl_sticky');
                    root.style.top = '';
                    root.style.left = '';
                    root.style.right = '';
                }
            }
        }, this);

        // ---------------------

        /*
        let linksModel = {
            tag: 'div',
            id: 'video-download-wrap',
            child: []
        };

        qualities.forEach((quality) => {
            let linkModel = {
                tag: 'div',
                child: {
                    tag: 'a',
                    href: quality.url,
                    download: quality.filename,
                    data: { type: 'video/mpeg' },
                    events: [ [ 'click', this.app.downloadFile, this.app ] ],
                    child: [
                        {
                            text: quality.quality + 'p'
                        }
                    ]
                }
            };

            if (this.app.settings.video_show_size && quality.size !== null) {
                linkModel.child.child.push({
                    tag: 'span',
                    innerHTML: this.app.formatSize(quality.size)
                });
            }

            linkModel.child.child.push({
                tag: 'span',
                innerHTML: 'HLS'
            });
                
            linksModel.child.push(linkModel);
        });

        this.linksNode = this.app.createNode(linksModel);

        playerNode.appendChild(this.linksNode);

        requestAnimationFrame(() => {
            this.linksNode.classList.add('animate');

            let linksNodeRect = this.linksNode.getBoundingClientRect();
            this.linksNode.style.width = linksNodeRect.width + 'px';
            this.linksNode.style.height = linksNodeRect.height + 'px';
        });

        // -------------------

        this.layerNode = playerNode.closest('#mv_layer_wrap');

        this.app.bindEventHandler(this.layerNode, 'scroll.layerScroll', (e) => {
            let playerNodeRect = playerNode.getBoundingClientRect();

            if (playerNodeRect.top <= 0) {
                if (!this.linksNode.classList.contains('sticky')) {
                    let linksNodeRect = this.linksNode.getBoundingClientRect();
                    this.linksNode.style.width = linksNodeRect.width + 'px';
                    this.linksNode.style.top = linksNodeRect.top + 'px';
                    this.linksNode.style.left = playerNodeRect.right + 'px';
                    this.linksNode.classList.add('sticky');
                }
            } else {
                if (this.linksNode.classList.contains('sticky')) {
                    this.linksNode.classList.remove('sticky');
                    this.linksNode.style.top = '';
                    this.linksNode.style.left = '';
                }
            }
        }, this);
        */
    }
}

class Calendar {
    constructor (app) {
        this.app = app;

        this.app.subscribe({
            name: 'calendar',
            events: {
                onSidebarChanged: { callback: this.onSidebarChanged, context: this }
            } 
        });
    }

    onSidebarChanged (sidebar) {
        if (sidebar && !sidebar.querySelector('#vkf-calendar-item')) {
            const listNode = sidebar.querySelector('ol');

            const itemElement = htmlToElement(
                `<li id="vkf-calendar-item">
                    <a href="#" class="left_row" data-event-handlers="click:onClick">
                        <div class="LeftMenu__icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20">
                                <path fill="currentColor" fill-rule="evenodd" d="M9.2,3.5h1.6l3.83.06a3.28,3.28,0,0,1,1.23.27,3,3,0,0,1,1.31,1.3,3.23,3.23,0,0,1,.28,1.37H3.55V6.37a3.29,3.29,0,0,1,.28-1.23,3,3,0,0,1,1.3-1.31,3.29,3.29,0,0,1,1.24-.27C7,3.5,7.9,3.5,9.2,3.5ZM3.5,8v2.8l.06,2.83a3.28,3.28,0,0,0,.27,1.23,3,3,0,0,0,1.3,1.31,3.29,3.29,0,0,0,1.24.27c.67.06,1.54.06,2.83.06h1.6l3.83-.06a3.28,3.28,0,0,0,1.23-.27,3,3,0,0,0,1.31-1.3,3.29,3.29,0,0,0,.27-1.24c.06-.67.06-1.55.06-2.83V8ZM2,9.2c0-2.52,0-3.78.5-4.74a4.4,4.4,0,0,1,2-2C5.42,2,6.68,2,9.2,2h1.6c2.52,0,4.78,0,5.74.5a4.4,4.4,0,0,1,2,2c.5,1,.5,2.22.5,4.74v1.6c0,2.52,0,3.78-.5,4.74a4.4,4.4,0,0,1-2,2c-1,.5-3.22.5-5.74.5H9.2c-2.52,0-3.78,0-4.74-.5a4.4,4.4,0,0,1-2-2C2,14.58,2,13.32,2,10.8ZM9,9H9a1,1,0,0,1,1,1h0a1,1,0,0,1-1,1H9a1,1,0,0,1-1-1H8A1,1,0,0,1,9,9Zm3,0h0a1,1,0,0,1,1,1h0a1,1,0,0,1-1,1h0a1,1,0,0,1-1-1h0A1,1,0,0,1,12,9Zm3,0h0a1,1,0,0,1,1,1h0a1,1,0,0,1-1,1h0a1,1,0,0,1-1-1h0A1,1,0,0,1,15,9ZM9,12H9a1,1,0,0,1,1,1h0a1,1,0,0,1-1,1H9a1,1,0,0,1-1-1H8A1,1,0,0,1,9,12ZM6,12H6a1,1,0,0,1,1,1H7a1,1,0,0,1-1,1H6a1,1,0,0,1-1-1H5A1,1,0,0,1,6,12ZM6,9H6a1,1,0,0,1,1,1H7a1,1,0,0,1-1,1H6a1,1,0,0,1-1-1H5A1,1,0,0,1,6,9Zm6,3h0a1,1,0,0,1,1,1h0a1,1,0,0,1-1,1h0a1,1,0,0,1-1-1h0A1,1,0,0,1,12,12Z"/>
                            </svg> 
                        </div>
                        <span class="left_label inl_bl">${ this.app.lang('calendar') }</span>
                    </a>
                    <div class="left_settings" onclick="menuSettings(0)">
                        <div class="left_settings_inner"></div>
                    </div>
                </li>`
            );

            addListeners(itemElement, {
                onClick: (e, target) => this.onClick(e, target),
            });

            listNode.insertBefore(
                itemElement,
                listNode.querySelector('.more_div')
            );
        }
    }

    onClick (event, target) {
        let url = window.location.href,
            wPattern = /(?!\?|&)w=[^\?&]+/;

        if (wPattern.test(url)) {
            url = url.replace(wPattern, 'w=calendar');
        } else {
            url += (/\?/.test(url) ? '&' : '?') + 'w=calendar';
        }

        target.href = url;

        return window.nav.go(target, event, { noback: true }); 
    }
}

class UrlShortener {
    constructor (app) {
        this.app = app;

        this.app.subscribe({
            name: 'urlShortener',
            events: {
                onSidebarChanged: { callback: this.onSidebarChanged, context: this }
            } 
        });
    }

    onSidebarChanged (sidebar) {
        if (!sidebar || sidebar.querySelector('#vkf-url-shortener-item')) {
            return;
        }

        const listNode = sidebar.querySelector('ol');

        const itemElement = htmlToElement(
            `<li class="vkf-sb-us-li" id="vkf-url-shortener-item">
                <span class="left_row">
                    <div class="LeftMenu__icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20">
                            <path fill="currentColor" d="M11.94 7.56a1.9 1.9 0 0 1 .32.38 3.23 3.23 0 0 1-.32 4.21L8.4 15.7a3.25 3.25 0 0 1-4.6-4.6L5.86 9a4.62 4.62 0 0 0 .32 1.8l-1.3 1.35a1.75 1.75 0 0 0 2.48 2.48l3.53-3.54A1.72 1.72 0 0 0 11.17 9a1.49 1.49 0 0 0-.7-.7l1.1-1.1a1.9 1.9 0 0 1 .38.35zm-3.5 4.2l1.1-1.1a1.49 1.49 0 0 1-.7-.7 1.72 1.72 0 0 1 .29-2.06l3.53-3.54a1.75 1.75 0 1 1 2.48 2.48l-1.3 1.3a4.62 4.62 0 0 1 .32 1.8L16.2 7.9a3.25 3.25 0 0 0-4.6-4.6L8.06 6.85a3.23 3.23 0 0 0-.32 4.21 1.9 1.9 0 0 0 .32.38 1.9 1.9 0 0 0 .38.32z"/>
                        </svg>
                    </div>
                    <span class="vkf-us-form">
                        <form action="/cc" method="POST" data-event-handlers="submit:onSubmit">
                            <input type="text" id="vkf-url-shortener-input" value="${ this.app.lang('url_shorten') }" placeholder="${ this.app.lang('enter_for_submit') }" data-event-handlers="focusin:onFocusChange,focusout:onFocusChange">
                        </form>
                    </span>
                </span>
                <div class="left_settings" onclick="menuSettings(0)">
                    <div class="left_settings_inner"></div>
                </div>
            </li>`
        );

        addListeners(itemElement, {
            onFocusChange: (e, target) => this.onFocusChange(e, target),
            onSubmit: (e, target) => this.onSubmit(e, target),
        });

        listNode.insertBefore(
            itemElement,
            listNode.querySelector('.more_div')
        );
    }

    onSubmit (event, target) {
        event.preventDefault();

        let listItem = target.closest('.vkf-sb-us-li');

        target = target.querySelector("input[type='text']");

        let setProgress = (isProgress) => {
            listItem.classList[isProgress ? 'add' : 'remove']('vkf-sb-us-li-progress');
        };

        let url = target.value.trim();

        if (url) {
            setProgress(true);

            this.app.coreMessage(
                'getShortUrl', 
                { url }, 
                (response) => {
                    setProgress(false);

                    if (response.error) {
                        this.app.showFastBox(response.error);
                    } else {
                        target.value = response.url;

                        setTimeout(() => target === document.activeElement && this.app.inputSelectAll(target), 0);
                    }
                }
            );
        }
    }

    onFocusChange (event, target) {
        let listItem = target.closest('.vkf-sb-us-li');

        if (listItem) {
            if (event.type == 'focusin') {
                listItem.classList.add('vkf-sb-us-li-focus');

                if (target.value == this.app.lang('url_shorten')) {
                    target.value = '';
                } else {
                    this.app.inputSelectAll(target);
                }
            } else {
                listItem.classList.remove('vkf-sb-us-li-progress', 'vkf-sb-us-li-focus');
                target.value = this.app.lang('url_shorten');
            }
        }
    }
}

let vkFlex = window.vkFlex = new Injection();

})();