/*
        const bindMethods = instance => {
            for (let key in instance) {
                if (typeof(instance[key]) === 'function') {
                    instance[key] = instance[key].bind(instance);
                }
            }
        };

        const now = (function () {
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

        // --------------

        const __drawConnectedPoints = (options) => {
            // console.log(options);
            options.ctx.fillStyle = options.fill || '#777';

            let prev = null;

            options.items.forEach(item => {
                options.ctx.beginPath();
                options.ctx.arc(item[0], item[1], options.pointRadius || 2, 0, Math.PI * 2);
                options.ctx.fill();

                if (prev) {
                    options.ctx.strokeStyle = options.fill || '#777';
                    options.ctx.strokeWidth = options.strokeWidth || 1;
                    options.ctx.beginPath();
                    options.ctx.moveTo(prev[0], prev[1]);
                    options.ctx.lineTo(item[0], item[1]);
                    options.ctx.closePath();
                    options.ctx.stroke();
                }

                prev = item;
            });
        };

        // --------------

        const EVENT_NONE = 0;


        const EVENT_MOVE = 1;

        const EVENT_MOVE_X = 2;
        const EVENT_MOVE_LEFT = 4;
        const EVENT_MOVE_RIGHT = 8;

        const EVENT_MOVE_Y = 16;
        const EVENT_MOVE_UP = 32;
        const EVENT_MOVE_DOWN = 64;


        const EVENT_SWIPE = 128;

        const EVENT_SWIPE_X = 256;
        const EVENT_SWIPE_LEFT = 512;
        const EVENT_SWIPE_RIGHT = 1024;

        const EVENT_SWIPE_Y = 2048;
        const EVENT_SWIPE_UP = 4096;
        const EVENT_SWIPE_DOWN = 8192;


        const EVENT_TAP = 16384;
        const EVENT_TAP_DOUBLE = 32768;


        // pan swipe tap double-tap pinch(2-fingers scale)
        class Gestures {
            constructor (el, _ctx) {
                bindMethods(this);

                this._ctx = _ctx;

                this.el = el;

                this.downStart = null;
                this.prevTap = null;

                this.firstMovement = null;
                this.prevMovement = null;
                this.lastMovement = null;

                this.lastMovements = [];

                this.detectedEvent = EVENT_NONE;

                this.el.addEventListener('mousedown', (e) => this.onMouseDown(e));
                this.el.addEventListener('mouseup', (e) => this.onMouseUp(e));
                this.el.addEventListener('mousemove', (e) => this.onMouseMove(e));
            }

            getDistance (x1, y1, x2, y2) {
                return Math.sqrt(Math.pow(Math.abs(x1 - x2), 2) + Math.pow(Math.abs(y1 - y2), 2));
            }

            onMouseDown (e) {
                this.downStart = e;
            }

            onMouseUp (e) {
                let synthEvent = this.detectedEvent;

                // swipe
                if (synthEvent & EVENT_MOVE) {
                    const lastMovementsLength = this.lastMovements.length;

                    let actualMovements = [],
                        lastActualMovement = null,
                        prevActualMovement = null;

                    for (let i = lastMovementsLength - 1; i > 0; i--) {
                        const
                            currentMovement = this.lastMovements[i],
                            prevMovement = this.lastMovements[i - 1];

                        if (
                            (this.lastMovement.timeStamp - currentMovement.timeStamp) < 150 &&
                            (this.lastMovement.timeStamp - prevMovement.timeStamp) < 150 &&
                            this.getDistance(currentMovement.clientX, currentMovement.clientY, prevMovement.clientX, prevMovement.clientY) > 10
                        ) {
                            lastActualMovement = currentMovement;
                            prevActualMovement = prevMovement;
                            break;
                        }
                    }

                    if (lastActualMovement && prevActualMovement) {
                        __drawConnectedPoints({
                            ctx: this._ctx,
                            fill: '#777',
                            strokeWidth: 2,
                            pointRadius: 4,
                            items: [
                                [ prevActualMovement.clientX, prevActualMovement.clientY ],
                                [ lastActualMovement.clientX, lastActualMovement.clientY ]
                            ]
                        });

                        // --

                        const dx = lastActualMovement.clientX - prevActualMovement.clientX;
                        const dy = prevActualMovement.clientY - lastActualMovement.clientY;

                        const movementAngle = Math.atan2(dy, dx) * 180 / Math.PI + (dy < 0 ? 360 : 0);
                        console.log(movementAngle);
                    } else {
                        console.log('!');
                    }

                    // --------------------
                    // --------------------

                    for (let i = lastMovementsLength; --i;) {
                        const movement = this.lastMovements[i];

                        if ((this.lastMovement.timeStamp - movement.timeStamp) < 300) {
                            actualMovements.push(movement);
                        } else {
                            break;
                        }
                    }

                    __drawConnectedPoints({
                        ctx: this._ctx,
                        fill: '#f28383',
                        items: actualMovements.reduce((acc, move) => {
                            acc.push([ move.clientX, move.clientY ]);
                            return acc;
                        }, [])
                    });

                    {
                        let velocity = 0,
                            velocityX = 0,
                            velocityY = 0;

                        for (let i = 1; i < lastMovementsLength; i++) {
                            const
                                prevMovement = this.lastMovements[i - 1],
                                movement = this.lastMovements[i],
                                timeDiff = movement.timeStamp - prevMovement.timeStamp;

                            velocity += this.getDistance(movement.clientX, movement.clientY, prevMovement.clientX, prevMovement.clientY) / timeDiff * 1000;
                            velocityX += (movement.clientX - prevMovement.clientX) / timeDiff * 1000;
                            velocityY += (movement.clientY - prevMovement.clientY) / timeDiff * 1000;
                        }

                        velocity /= lastMovementsLength;
                        velocityX /= lastMovementsLength;
                        velocityY /= lastMovementsLength;
                        // console.log(Math.round(velocityX), Math.round(velocityY), Math.round(velocity));
                    }

                    // --------------------
                    // --------------------

                // tap || double-tap
                } else {
                    synthEvent = EVENT_TAP;
                    const pressingDuration = e.timeStamp - this.downStart.timeStamp;  // 250 - max time of the pointer to be down (like finger on the screen)

                    //->>> console.log('tap');

                    if (pressingDuration <= 250 && this.prevTap && (e.timeStamp - this.prevTap.timeStamp) < 300) {
                        synthEvent |= EVENT_TAP_DOUBLE;
                        this.prevTap = null;
                    } else {
                        this.prevTap = e;
                    }
                }

                // --------

                this.downStart = this.firstMovement = this.prevMovement = this.lastMovement = null;
                this.lastMovements = [];
                this.detectedEvent = EVENT_NONE;
            }

            onMouseMove (e) {
                if (this.downStart) {
                    if (!this.firstMovement) {
                        this.lastMovement = this.firstMovement = e;
                        return;
                    }

                    // move detected
                    if ((this.detectedEvent & EVENT_MOVE) || Math.abs(e.clientX) > 10 || Math.abs(e.clientY) > 10) {
                        const prevDetectedEvent = this.detectedEvent;

                        this.detectedEvent = EVENT_MOVE;

                        const
                            absX = Math.abs(e.clientX - this.lastMovement.clientX),
                            absY = Math.abs(e.clientY - this.lastMovement.clientY);

                        // pan
                        if (absX > absY) {  // move x
                            this.detectedEvent |= EVENT_MOVE_X;
                            if (e.clientX > this.lastMovement.clientX) {
                                this.detectedEvent |= EVENT_MOVE_RIGHT;
                                //->>> console.log('pan-right');
                            } else {
                                this.detectedEvent |= EVENT_MOVE_LEFT;
                                //->>> console.log('pan-left');
                            }
                        } else {  // move y
                            this.detectedEvent |= EVENT_MOVE_Y;
                            if (e.clientY < this.lastMovement.clientY) {
                                this.detectedEvent |= EVENT_MOVE_UP;
                                //->>> console.log('pan-up');
                            } else {
                                this.detectedEvent |= EVENT_MOVE_DOWN;
                                //->>> console.log('pan-down');
                            }
                        }

                        // ----

                        if (
                            (prevDetectedEvent & EVENT_MOVE_LEFT) && (this.detectedEvent & EVENT_MOVE_RIGHT) ||
                            (prevDetectedEvent & EVENT_MOVE_UP) && (this.detectedEvent & EVENT_MOVE_DOWN)
                        ) {
                            this.lastMovements = [];
                        }

                        this.lastMovements.push(e);
                    }

                    this.prevMovement = this.lastMovement;
                    this.lastMovement = e;
                }
            }
        }


        const init = () => {
            const
                canvas = document.querySelector('canvas');
                ctx = canvas.getContext('2d');

            const resize = () => {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            };

            window.addEventListener('resize', resize);
            resize();

            // --------------

            const gestures = new Gestures(canvas, ctx);

            // {
            //     pointers : any[],
            //     changedPointers : EVENT_TYPE[],
            //     pointerType : POINTER_TYPE,
            //     srcEvent : EVENT_TYPE,
            //     isFirst : boolean,
            //     isFinal : boolean,
            //     eventType : INPUT,
            //     center : {
            //         x : number,
            //         y : number,
            //     },
            //     timeStamp : number,
            //     deltaTime : number,
            //     angle : number,
            //     distance : number,
            //     deltaX : number,
            //     deltaY : number,
            //     offsetDirection : DIRECTION,
            //     overallVelocityX : number,
            //     overallVelocityY : number,
            //     overallVelocity : number,
            //     scale : number,
            //     rotation : number,
            //     maxPointers : number,
            //     velocity : number,
            //     velocityX : number,
            //     velocityY : number,
            //     direction : DIRECTION,
            //     target : HTMLElement,
            //     additionalEvent : string,
            //     type : string
            // }
};

document.readyState == 'complete' ? init() : window.addEventListener('load', init);
*/