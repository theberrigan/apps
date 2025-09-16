(() => {
    'use strict';

    const now : () => number = (function () {
        if (performance && performance.now) {
            return performance.now.bind(performance);  // more precisely
        }

        if (Date.now) {
            return Date.now.bind(Date);  // faster
        }

        if (+(new Date()) > 0) {
            return function () {
                return +(new Date());
            };
        }

        return function () {
            return (new Date()).getTime();  // worst
        };
    })();

    let rAF : any = window.requestAnimationFrame,
        cAF : any = window.cancelAnimationFrame;

    if (!rAF) {
        const p = 'o ms moz webkit'.split(' ');

        for (let i = p.length - 1; !rAF && i >= 0; --i) {
            rAF = window[ p[i] + 'RequestAnimationFrame' ];
            cAF = window[ p[i] + 'CancelAnimationFrame' ] || window[ p[i] + 'CancelRequestAnimationFrame' ];
        }

        if (!rAF) {
            // polyfill for IE9
            rAF = (function () {
                const msPerFrame : number = 1000 / 60;
                let last : number = 0;

                return (callback : (time : number) => void, element? : Element) : number => {
                    const time : number = now();
                    let delay : number = msPerFrame - (time - last);

                    if (delay < 0) {
                        delay = 0;
                    }

                    const timerId : number = window.setTimeout(() => {
                        callback(time + delay);
                    }, delay);

                    last = time + delay;

                    return timerId;
                }
            })();

            cAF = window.clearTimeout;
        }
    }

    if (!cAF) {
        // Sorry, you can't cancel frame request. :(
        // Are you using Firefox 1?!
        cAF = function () {};
    }

    window.requestAnimationFrame = rAF.bind(window);
    window.cancelAnimationFrame = cAF.bind(window);
})();