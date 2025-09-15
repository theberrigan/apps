const INPUT_START = 1;
const INPUT_MOVE = 2;
const INPUT_END = 4;
const INPUT_CANCEL = 8;

const STATE_POSSIBLE = 1;
const STATE_BEGAN = 2;
const STATE_CHANGED = 4;
const STATE_ENDED = 8;
const STATE_RECOGNIZED = STATE_ENDED;
const STATE_CANCELLED = 16;
const STATE_FAILED = 32;

const DIRECTION_NONE = 1;
const DIRECTION_LEFT = 2;
const DIRECTION_RIGHT = 4;
const DIRECTION_UP = 8;
const DIRECTION_DOWN = 16;
const DIRECTION_HORIZONTAL = DIRECTION_LEFT | DIRECTION_RIGHT;
const DIRECTION_VERTICAL = DIRECTION_UP | DIRECTION_DOWN;
const DIRECTION_ALL = DIRECTION_HORIZONTAL | DIRECTION_VERTICAL;

type DIRECTION = DIRECTION_NONE | DIRECTION_LEFT | DIRECTION_RIGHT | DIRECTION_UP | DIRECTION_DOWN | DIRECTION_HORIZONTAL | DIRECTION_VERTICAL | DIRECTION_ALL;
type INPUT = INPUT_START | INPUT_MOVE | INPUT_END | INPUT_CANCEL;
type POINTER_TYPE = 'touch' | 'mouse' | 'pen' | 'kinect';
type EVENT_TYPE = TouchEvent | MouseEvent | PointerEvent;

type EVENT_HANDLER_ARG_TYPE = (ev: {
    pointers : any[],
    changedPointers : EVENT_TYPE[],
    pointerType : POINTER_TYPE,
    srcEvent : EVENT_TYPE,
    isFirst : boolean,
    isFinal : boolean,
    eventType : INPUT,
    center : {
        x : number,
        y : number,
    },
    timeStamp : number,
    deltaTime : number,
    angle : number,
    distance : number,
    deltaX : number,
    deltaY : number,
    offsetDirection : DIRECTION,
    overallVelocityX : number,
    overallVelocityY : number,
    overallVelocity : number,
    scale : number,
    rotation : number,
    maxPointers : number,
    velocity : number,
    velocityX : number,
    velocityY : number,
    direction : DIRECTION,
    target : HTMLElement,
    additionalEvent : string,
    type : string
}) => any;

type MANAGER_OPTIONS_TYPE = {
    touchAction? : string,
    domEvents? : boolean,
    enable? : boolean,
    cssProps? : any,
    recognizers? : any[]
};

export class Hammer {
    public static INPUT_START : INPUT_START;
    public static INPUT_MOVE : INPUT_MOVE;
    public static INPUT_END : INPUT_END;
    public static INPUT_CANCEL : INPUT_CANCEL;

    public static STATE_POSSIBLE : STATE_POSSIBLE;
    public static STATE_BEGAN : STATE_BEGAN;
    public static STATE_CHANGED : STATE_CHANGED;
    public static STATE_ENDED : STATE_ENDED;
    public static STATE_RECOGNIZED : STATE_RECOGNIZED;
    public static STATE_CANCELLED : STATE_CANCELLED;
    public static STATE_FAILED : STATE_FAILED;

    public static DIRECTION_NONE : DIRECTION_NONE;
    public static DIRECTION_LEFT : DIRECTION_LEFT;
    public static DIRECTION_RIGHT : DIRECTION_RIGHT;
    public static DIRECTION_UP : DIRECTION_UP;
    public static DIRECTION_DOWN : DIRECTION_DOWN;
    public static DIRECTION_HORIZONTAL : DIRECTION_HORIZONTAL;
    public static DIRECTION_VERTICAL : DIRECTION_VERTICAL;
    public static DIRECTION_ALL : DIRECTION_ALL;

    public static Manager : Manager;
    public static Input;
    public static TouchAction;

    public static TouchInput;
    public static MouseInput;
    public static PointerEventInput;
    public static TouchMouseInput;
    public static SingleTouchInput;

    public static Recognizer : Recognizer;
    public static AttrRecognizer : AttrRecognizer;
    public static Tap : TapRecognizer;
    public static Pan : PanRecognizer;
    public static Swipe : SwipeRecognizer;
    public static Pinch : PinchRecognizer;
    public static Rotate : RotateRecognizer;
    public static Press : PressRecognizer;

    // public static PinchRecognizer : any;
    public static VERSION : string;

    public static defaults : {
        domEvents : false,
        touchAction : TOUCH_ACTION_COMPUTE,
        enable : true,
        inputTarget : null,
        inputClass : null,
        preset : [
            [ RotateRecognizer, { enable : false } ],
            [ PinchRecognizer, { enable : false },
                [ 'rotate' ]
            ],
            [ SwipeRecognizer, { direction : DIRECTION_HORIZONTAL } ],
            [ PanRecognizer, { direction : DIRECTION_HORIZONTAL },
                [ 'swipe' ]
            ],
            [ TapRecognizer ],
            [ TapRecognizer, { event : 'doubletap', taps: 2 },
                [ 'tap' ]
            ],
            [ PressRecognizer ]
        ],
        cssProps : {
            userSelect : 'none',
            touchSelect : 'none',
            touchCallout : 'none',
            contentZooming : 'none',
            userDrag : 'none',
            tapHighlightColor : 'rgba(0,0,0,0)'
        }
    };

    public static on (element : HTMLElement, types : string, handler : Function) : void;
    public static off (element : HTMLElement, types : string, handler : Function) : void;
    public static each (obj : any, handler : (item : any, index : string | number, src : any) => void) : void;
    public static merge (obj1 : any, obj2 : any) : any;
    public static extend (obj1 : any, obj2 : any) : any;
    public static inherit (child : any, base : any, properties? : any) : void;
    public static bindFn (fn : Function, scope : any) : any;
    public static prefixed (obj : any, name : string) : string;

    constructor (element : HTMLElement, options? : MANAGER_OPTIONS_TYPE);

    public set (options : MANAGER_OPTIONS_TYPE) : Manager;
    public stop (force? : boolean) : void;
    public recognize (inputData : any) : void;
    public get (recognizer : Recognizer | string) : Recognizer | null;
    public add (recognizer : Recognizer | string) : Recognizer | Manager;
    public remove (recognizer : Recognizer | String) : Manager;
    public on (events : string, handler : Function) : EventEmitter;
    public off (events : string, handler? : Function) : EventEmitter;
    public emit (event : string, data : any) : void;
    public destroy () : void;
}

Hammer.Manager = class Manager {
    constructor (element : HTMLElement, options? : MANAGER_OPTIONS_TYPE);

    public set (options : MANAGER_OPTIONS_TYPE) : Manager;
    public stop (force? : boolean) : void;
    public recognize (inputData : any) : void;
    public get (recognizer : Recognizer | string) : Recognizer | null;
    public add (recognizer : Recognizer | string) : Recognizer | Manager;
    public remove (recognizer : Recognizer | String) : Manager;
    public on (events : string, handler : Function) : EventEmitter;
    public off (events : string, handler? : Function) : EventEmitter;
    public emit (event : string, data : any) : void;
    public destroy () : void;
}

Hammer.Recognizer = class Recognizer {
    constructor(options? : { enabled : boolean });

    public set (options : { enabled : boolean }) : Recognizer;
    public recognizeWith (otherRecognizer : Recognizer) : Recognizer;
    public dropRecognizeWith (otherRecognizer : Recognizer) : Recognizer;
    public requireFailure (otherRecognizer : Recognizer) : Recognizer;
    public dropRequireFailure (otherRecognizer : Recognizer) : Recognizer;
}

Hammer.AttrRecognizer = class AttrRecognizer extends Recognizer {}
Hammer.Tap = class TapRecognizer extends Recognizer {}
Hammer.Pan = class PanRecognizer extends Recognizer {}
Hammer.Swipe = class SwipeRecognizer extends Recognizer {}
Hammer.Pinch = class PinchRecognizer extends Recognizer {}
Hammer.Rotate = class RotateRecognizer extends Recognizer {}
Hammer.Press = class PressRecognizer extends Recognizer {}

class EventEmitter {}