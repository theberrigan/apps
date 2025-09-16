import {
    AfterViewInit,
    Component,
    ElementRef,
    forwardRef,
    Input,
    OnChanges,
    OnDestroy,
    OnInit,
    Renderer2,
    SimpleChanges,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from '@angular/forms';
import {DatetimeService} from '../../../../services/datetime.service';
import {cloneDate, int, isEmpty, isFinite} from '../../../../lib/utils';
import {DeviceService} from '../../../../services/device.service';
import {TranslateService} from '@ngx-translate/core';
import { forEach, includes, padStart, range} from 'lodash';
import {DomService} from '../../../../services/dom.service';
import {Subscription} from 'rxjs';

// TODO:
// - маска ввода
// - unlisten/unsub
// - обновление при смене языка
// - как должен вести себ попап при изменении isDisabled
// - не пересчитывать месяц, когда не переключается страница


// -------------------
// 1. Главная модель
// 2. Главное поле ввода
// 3. Календарь
// 4. Поля ввода веремени
// 5. Слайдеры времени
// 6. emitOnChange()
// 7. onTouch()
// ----------------------
// Поле ввода минут/часов:
// 1. если основной модели ещё не существует (главный инпут пуст),
//    создать new Date() и заполнить время нулями. Сохранить
//    этот объект в гланую модель.
// 2. Из главной модели (она теперь по-любому есть) сделать резервную копию.
// 3. При вводе часов/минут, если состояние этого поля становится неваидным,
//    то брать резервную копию, подставлять в главную модель и обновлять ВСЁ!
//    (слайдер, соседнее поле часов/мин, календарь, основное поле ввода и главную модель)
// 4. При блюре в главной модели по-любому находится валиное значение, и весь UI
//    находится в правильном состоянии. Нужно лишь обновить из модели
//    только что заблюренное поле. И удалить резервную копию даты.
// ------------------------
// Слайдер:
// 1. рассчитывать значение ползунка; вычислять часы и минуты;
//    конвертировать 12 -> 24, если нужно; обновить интерфейс.
// ------------------------
// object, date, moment, iso, timestamp
// ------------------------
// Календарь нужно обновлять после обнвления времени только в том случае, если mainModel создана с нуля

// при кейапе проверять время, если валидно, то писать в модель и обновлять главный инпут
// при блюре проверять валидность


// - Поменялся язык -> обновить поле, обновить пикер
// - value поменялось через writeValue -> распарсить, обновить поле, обновить пикер
//   если распарсенное значение инвалидно -> сбросить в null, обновить поле, обновить пикер, уведомить через onChange
// - Пользователь изменил ввод в UI -> вычислить value, обновить поле, уведомить через onChange
// - Пользователь ввёл неверное значение в поле
// ------------------------
// required будет проверяться FormBuilder'ом
// валидность даты будет проверяться валидатором, который напишу позже

// console.log('after conversion:', this.datetimeService.getMoment(this.mainModel).format('DD.MM.YYYY HH:mm:ss'));


const BUBBLE_WIDTH = 462;
const BUBBLE_HEIGHT = 334;

let instanceId = -1;


@Component({
    selector: 'datepicker',
    exportAs: 'datepicker',
    templateUrl: './datepicker.component.html',
    styleUrls: [ './datepicker.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => DatepickerComponent),
            multi: true
        }
    ],
    // animations: [
    //     trigger('togglePopup', [
    //         transition(':enter', [
    //             style({ 'transform': 'translateY(10px)', 'opacity': '0' }),
    //             animate('0.1s ease-out', style({ 'transform': 'translateY(0)', 'opacity': '1' }))
    //         ]),
    //         transition(':leave', [
    //             style({ 'transform': 'translateY(0)', 'opacity': '1' }),
    //             animate('0.1s ease-out', style({ 'transform': 'translateY(10px)', 'opacity': '0' }))
    //         ]),
    //     ])
    // ],
    host: {
        'class': 'datepicker',
        '[class.datepicker_active]': 'isActive',
    }
})
export class DatepickerComponent implements OnInit, OnDestroy, OnChanges, AfterViewInit, ControlValueAccessor {
    @ViewChild('inputEl')
    public inputEl : ElementRef;

    public subs : Subscription[] = [];

    // ---------------------

    public moment : any = null;

    public inputModel : string = '';

    //
    // ------------------------

    public onTouched : any = () => {};

    public onChange : any = (_ : any) => {};

    // Options
    // ------------------------

    private _isDisabled : boolean = false;

    @Input()
    public set isDisabled (value : boolean) {
        if ((this._isDisabled = value)) {
            this.deactivate();
        }
    }

    public get isDisabled () : boolean {
        return this._isDisabled;
    }

    public _firstDayOfWeek : 'mon' | 'sun' | 'auto';

    @Input()
    public firstDayOfWeek : 'mon' | 'sun' | 'auto' = 'auto';

    public _format : string;

    @Input()
    public format : string = 'YYYY-MM-DD'; // TODO: set default format

    public _type : 'timestamp' | 'iso' | 'date' | 'moment' | 'object' = 'timestamp';

    @Input()
    public type : 'timestamp' | 'iso' | 'date' | 'moment' | 'object';

    public _boundingEl : ElementRef;

    @Input()
    public boundingEl : ElementRef;

    @Input()
    public placeholder : string = '';

    public hasTimePicker : boolean;

    public isTwelveHoursFormat : boolean;

    // defaultValue: null, // well be set by client component
    // isRequired: true  // checked by formBuilder

    // -----------------------------

    public isActive : boolean = false;
    public isInputFocus : boolean = false;

    public bubbleLayout : 'calendar' | 'years' | 'months' = null;
    public calendarGrid : any[];
    public calendarYear : number;
    public calendarMonth : number;
    public calendarMonthName : string;
    public calendarFullDate : Date;
    public yearsGrid : number[];
    public monthsGrid : any[];
    public weekdaysShort : string[];
    public now : any;

    // -------------------------------------

    @ViewChild('hoursSlider')
    public set hoursSlider (el : ElementRef) {
        this.setupSlider(el, 'h');
    }

    @ViewChild('minutesSlider')
    public set minutesSlider (el : ElementRef) {
        this.setupSlider(el, 'm');
    }

    public slidersUnlistens : any = {};
    public activeTimeSlider : HTMLDivElement;
    public activeTimeSliderType : 'h' | 'm';
    public hoursSliderValue : number = 0;
    public minutesSliderValue : number = 0;
    public mainModel : Date;
    public mainModelBackup : Date;
    public timeSuffix : 'am' | 'pm' = 'am';
    public activeTimeInput : 'h' | 'm';
    public hoursInputModel : string = '';
    public minutesInputModel : string = '';

    public isLastClickByBubble : boolean = false;
    public bubblePosition : number;

    // --------------------------------------

    public listeners : any[] = [];

    public readonly dtPickerToggleClickEventMark : string;
    public readonly dtPickerBubbleClickEventMark : string;
    public readonly dtPickerBubbleMouseDownEventMark : string;

    constructor (
        public el : ElementRef,
        public renderer : Renderer2,
        public deviceService : DeviceService,
        public domService : DomService,
        public datetimeService : DatetimeService,
        public translateService : TranslateService
    ) {
        const currentInstanceId = ++instanceId;

        this.dtPickerToggleClickEventMark = `dtPickerToggleClick-${ currentInstanceId }`;
        this.dtPickerBubbleClickEventMark = `dtPickerBubbleClick-${ currentInstanceId }`;
        this.dtPickerBubbleMouseDownEventMark = `dtPickerBubbleMouseDown-${ currentInstanceId }`;

        this.addSub(
            this.translateService.onLangChange.subscribe(() => {
                this.parseOptions();
                this.updateInputFromMainModel();
            })
        );

        this.parseOptions();
    }



    // NG hooks
    // ---------------------------

    public ngOnInit () : void {
        this.listeners = [
            ...this.listeners,
            this.renderer.listen(document.documentElement, 'click', e => this.onDocumentClick(e)),
            this.renderer.listen(document.documentElement, 'mousedown', e => this.onMouseDown(e)),
            this.renderer.listen(document.documentElement, 'mouseup', () => this.onMouseUp()),
        ];
    }

    public ngAfterViewInit () : void {
    }

    public ngOnDestroy () : void {
        this.listeners.forEach(unlisten => unlisten());

        if (this.bubbleListeners) {
            this.bubbleListeners.forEach(unlisten => unlisten());
            this.bubbleListeners = null;
        }

        this.subs.forEach(sub => sub.unsubscribe());
    }

    public ngOnChanges (changes : SimpleChanges) : void {
        this.parseOptions();  // TODO: parse only if options changed
    }

    public parseOptions () : void {
        this._firstDayOfWeek = this.firstDayOfWeek === 'auto' ? this.datetimeService.getFirstDayOfWeek() : this.firstDayOfWeek;
        this._format = this.datetimeService.getFormatByAlias((this.format || '').trim()) || 'YYYY-MM-DD';
        //console.log(this._format);
        this._type = includes([ 'timestamp', 'iso', 'date', 'moment', 'object' ], this.type) ? this.type : 'timestamp';
        this._boundingEl = this.boundingEl;

        this.hasTimePicker = this.datetimeService.hasFormatTime(this._format);
        this.isTwelveHoursFormat = this.hasTimePicker && this.datetimeService.isTwelveHoursFormat(this._format);

        // console.log(this.mode, this.isTwelveHoursFormat);
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }



    // ControlValueAccessor impl.
    // ---------------------------

    // source - object, date, moment, iso, timestamp
    public writeValue (source : Object | string | number | Date | any) : void {
        const empty = isEmpty(source);
        let moment = null;

        if (empty && !this.mainModel) {
            return;
        }

        if (!empty) {
            moment = this.datetimeService.parse(source);
        }

        this.mainModel = moment && moment.toDate();
        this.updateInputFromMainModel();
        this.emitOnChange();
    }

    public registerOnChange (fn : any) : void {
        this.onChange = fn;
    }

    public registerOnTouched (fn : any) : void {
        this.onTouched = fn;
    }

    public setDisabledState (isDisabled : boolean) : void {
        this._isDisabled = isDisabled;
    }



    // MAIN INPUT & MODEL
    // ---------------------------

    public updateInputFromMainModel () : void {
        this.inputModel = this.mainModel && this.datetimeService.getMoment(this.mainModel).format(this._format) || '';
        // console.warn('moment -> input', this.inputModel);
    }

    public updateMainModelFromInput () : void {
        const moment  = this.datetimeService.parse((this.inputModel || '').trim(), this._format);
        this.mainModel = moment && moment.toDate();
        // console.warn('input -> moment', this.mainModel);
    }

    public onInputFocus () : void {
        this.isInputFocus = true;
    }

    public onInputBlur () : void {
        this.isInputFocus = false;

        this.updateMainModelFromInput();
        this.updateInputFromMainModel();

        this.emitOnChange();
        this.onTouched();
    }

    public onInputType () : void {
        this.updateMainModelFromInput();
        this.emitOnChange();
    }

    public emitOnChange () : void {
        let value : any = null;

        if (this.mainModel) {
            const moment = this.datetimeService.getMoment(this.mainModel);

            switch (this._type) {
                case 'timestamp':
                    value = moment.toDate().getTime();
                    break;
                case 'iso':
                    value = moment.toISOString();
                    break;
                case 'date':
                    value = moment.toDate();
                    break;
                case 'moment':
                    value = moment;
                    break;
                case 'object':
                    value = moment.toObject();
                    break;
            }
        }

        this.onChange(value);
        this.onTouched();
    }



    // COMMON
    // ---------------------------

    // @HostListener('document:click', [ '$event' ])
    public onDocumentClick (e : any) {
        if (this.isLastClickByBubble || !this.isActive) {
            return;
        }

        const isToggleClick = this.domService.hasEventMark(e, this.dtPickerToggleClickEventMark);
        const isBubbleClick = this.domService.hasEventMark(e, this.dtPickerBubbleClickEventMark);

        if (!isToggleClick && !isBubbleClick) {
            this.setBubbleState(false);
        }
    }

    public onToggleClick (e : any) : void {
        this.domService.markEvent(e, this.dtPickerToggleClickEventMark);
        this.isActive ? this.deactivate() : this.activate();
    }

    public activate () : void {
        if (this.isActive) {
            return;
        }

        this.setBubbleState(true);
    }

    public deactivate () : void {
        this.setBubbleState(false);
        this.onTouched();
    }

    // BUBBLE
    // ---------------------------

    public bubbleListeners : any[];

    public onBubbleClick (e : any) : void {
        this.domService.markEvent(e, this.dtPickerBubbleClickEventMark);
    }

    public onBubbleMouseDown (e : any) : void {
        this.domService.markEvent(e, this.dtPickerBubbleMouseDownEventMark);
    }

    public runNowUpdater () : void {
        this.stopNowUpdater();

        const update = () => {
            const date = this.datetimeService.getMoment();

            let timeSuffix : string;
            let hours : number = date.hours();

            if (this.isTwelveHoursFormat) {
                timeSuffix = hours < 12 ? 'AM' : 'PM';
                hours = hours % 12 || 12;
            }

            this.now = {
                date: date.date(),
                month: this.datetimeService.getMonthName(date),
                year: date.year(),
                hours: this.zeroPad(hours),
                minutes: this.zeroPad(date.minutes()),
                timeSuffix,
                timeout: setTimeout(() => update(), 61 - date.seconds())
            };
        };

        update();
    }

    public stopNowUpdater () : void {
        if (this.now) {
            clearTimeout(this.now.timeout);
            this.now = null;
        }
    }

    public setBubbleState (isActive : boolean) : void {
        if (isActive) {
            this.generateCalendarGrid(this.mainModel || this.getToday());
            this.generateMonthsGrid();
            this.generateWeekdays();
            this.updateTimeSection();
            this.bubbleLayout = 'calendar';
            this.runNowUpdater();
            this.calcBubblePosition();
            if (this.hasTimePicker) {
                this.bubbleListeners = [
                    this.renderer.listen(document.documentElement, 'mousemove', e => this.calcSlider(e)),
                ];
            }
            this.isActive = true;
        } else {
            this.isActive = false;

            if (this.bubbleListeners) {
                this.bubbleListeners.forEach(unlisten => unlisten());
                this.bubbleListeners = null;
            }

            this.calendarGrid = null;
            this.calendarYear = null;
            this.calendarMonth = null;
            this.calendarMonthName = null;
            this.calendarFullDate = null;

            this.yearsGrid = null;
            this.monthsGrid = null;
            this.weekdaysShort = null;
            this.bubbleLayout = null;
            this.stopNowUpdater();
        }
    }

    public calcBubblePosition () : void {
        const boundEl = this.boundingEl && this.boundingEl.nativeElement || this.getParentBounding() || document.body;
        const boundRect : ClientRect = boundEl.getBoundingClientRect();
        const rootRect = this.el.nativeElement.getBoundingClientRect();
        const bubbleSquare = BUBBLE_WIDTH * BUBBLE_HEIGHT;
        const viewportSize = this.deviceService.viewportClientSize;

        const positions = [
            [ 'bottom', 'right', 'left',  1 ],
            [ 'bottom', 'left',  'right', 2 ],
            [ 'top',    'right', 'left',  3 ],
            [ 'top',    'left',  'right', 4 ]
        ];

        let pos = <number>positions[0][3];
        let posFreeSquare = 0;

        forEach(positions, ([ posY, posX, oppositePosX, posId ]) => {
            const bound = {
                top: Math.max(0, boundRect.top),
                bottom: Math.min(viewportSize.y,  boundRect.bottom)
            };

            const freeX = Math.abs(rootRect[posX] - boundRect[oppositePosX]);
            const freeY = Math.abs(bound[posY] - rootRect[posY]);
            const freeSquare = Math.min(BUBBLE_WIDTH, freeX) * Math.min(BUBBLE_HEIGHT, freeY);

            if (posFreeSquare < freeSquare) {
                posFreeSquare = freeSquare;
                pos = <number>posId;
            }

            // is perfect pos?
            if (bubbleSquare <= freeSquare) {
                return false;
            }
        });

        this.bubblePosition = pos;
    }

    public getParentBounding () : any {
        const widgetEl = this.el.nativeElement;
        let parent = widgetEl.parentElement || widgetEl.parentNode;

        while (parent && (!parent.dataset || !parent.dataset.bounding)) {
            parent = parent.parentElement || parent.parentNode;
        }

        return parent;
    }

    public onSelectCurrentDate () : void {
        const today = new Date();

        this.activateDate({
            year: today.getFullYear(),
            month: today.getMonth(),
            date: today.getDate()
        });
    }

    public onGridSlide (direction : number) : void {
        switch (this.bubbleLayout) {
            case 'calendar':
                this.generateCalendarGrid(
                    direction === 1 ?
                    this.getNextMonth(this.calendarFullDate) :
                    this.getPrevMonth(this.calendarFullDate)
                );
                break;
            case 'years':
                const startYear = this.yearsGrid[0] + (12 * direction);
                this.yearsGrid = range(startYear, startYear + 12);
                break;
        }
    }

    public switchToMonths () : void {
        this.bubbleLayout = 'months';
    }

    public switchToYears () : void {
        const currentYear = this.calendarYear;

        if (!this.yearsGrid || !includes(this.yearsGrid, currentYear)) {
            this.yearsGrid = range(currentYear - 4, currentYear + 8);
        }

        this.bubbleLayout = 'years';
    }

    public switchToCalendar () : void {
        this.bubbleLayout = 'calendar';
    }

    public activateYear (year : number) {
        const date = new Date(year, this.calendarMonth, 1);
        this.generateCalendarGrid(date);
        this.switchToMonths();
    }

    public activateMonth (month : number) : void {
        const date = new Date(this.calendarYear, month, 1);
        this.generateCalendarGrid(date);
        this.switchToCalendar();
    }

    public activateDate (source : any) : void {
        let updateTimeSection = false;


        if (this.mainModel) {
            this.mainModel.setFullYear(source.year, source.month, source.date);
        } else {
            this.mainModel = new Date(source.year, source.month, source.date, 0, 0, 0, 0);
            updateTimeSection = true;
        }

        this.generateCalendarGrid(this.mainModel);
        this.updateInputFromMainModel();
        this.emitOnChange();

        if (updateTimeSection) {
            this.updateTimeSection();
        }

        if (!this.hasTimePicker) {
            this.deactivate();
        }
    }

    public isLeapYear (year : number) : boolean {
        return (year % 4 === 0) && (year % 100 !== 0) || (year % 400 === 0);
    }

    public getDaysInMonth (date : Date) : number {
        const february = 28 + Number(this.isLeapYear(date.getFullYear()));
        return [ 31, february , 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ][ date.getMonth() ];
    }

    public getFirstDayOfMonth (date : Date) : number { // 0-6 (0 - sun)
        return (new Date(date.getFullYear(), date.getMonth(), 1)).getDay();
    }

    public getPrevMonth (date : Date) : Date {
        const month = date.getMonth();
        return new Date(date.getFullYear() - Number(month === 0), (month || 12) - 1, 1);
    }

    public getNextMonth (date : Date) : Date {
        const month = date.getMonth();
        return new Date(date.getFullYear() + Number(month === 11), (month + 1) % 12, 1);
    }

    public getToday (hours : number = 0, minutes : number = 0, seconds : number = 0, ms : number = 0) : Date {
        const date = new Date();
        date.setHours(hours, minutes, seconds, ms);
        return date;
    }

    public zeroPad (value : number | string) : string {
        return padStart(String(value), 2, '0');
    }

    public roundMinutes (minutes : number) : number {
        return Math.min(59, Math.round(minutes / 5) * 5);
    }

    // --------------------------------------

    public generateWeekdays () : void {
        this.weekdaysShort = this.datetimeService.getShortWeekdays(<'mon' | 'sun'>this.firstDayOfWeek);
    }

    public generateMonthsGrid () : void {
        this.monthsGrid = this.datetimeService.getShortMonths().map((name, month) => ({ name, month }));
    }

    public generateCalendarGrid (date : Date) : void {
        const now = new Date();
        const nowYear = now.getFullYear();
        const nowMonth = now.getMonth();
        const nowDate = now.getDate();

        const activeYear = this.mainModel ? this.mainModel.getFullYear() : null;
        const activeMonth = this.mainModel ? this.mainModel.getMonth() : null;
        const activeDate = this.mainModel ? this.mainModel.getDate() : null;

        const daysCount = this.getDaysInMonth(date);
        const firstDayOfMonth = this.getFirstDayOfMonth(date); // 0 (sun) - 6 (mon)

        const year = date.getFullYear();
        const month = date.getMonth();
        const monthName = this.datetimeService.getMonthName(month);
        const grid = [];

        const tail = (this.firstDayOfWeek === 'mon' ? ((firstDayOfMonth || 7) - 1) : firstDayOfMonth) || 7;
        const head = (7 * 6) - tail - daysCount;

        const prevMonth = this.getPrevMonth(date);
        const prevMonthDaysCount = this.getDaysInMonth(prevMonth);
        const prevMonthYear = prevMonth.getFullYear();
        const prevMonthMonth = prevMonth.getMonth();

        const nextMonth = this.getNextMonth(date);
        const nextMonthYear = nextMonth.getFullYear();
        const nextMonthMonth = nextMonth.getMonth();

        for (let date : number = (prevMonthDaysCount - tail + 1); date <= prevMonthDaysCount; date++) {
            grid.push({
                isTail: true,
                isHead: false,
                isActive: false,
                year: prevMonthYear,
                month: prevMonthMonth,
                date
            });
        }

        for (let date : number = 1; date <= daysCount; date++) {
            grid.push({
                isTail: false,
                isHead: false,
                isActive: false,
                year,
                month,
                date
            });
        }

        for (let date : number = 1; date <= head; date++) {
            grid.push({
                isTail: false,
                isHead: true,
                isActive: false,
                year: nextMonthYear,
                month: nextMonthMonth,
                date
            });
        }

        grid.forEach((day : any, i : number) => {
            day.isHoliday = false;
            day.isWeekend = includes((this.firstDayOfWeek == 'mon' ? [ 5, 6 ] : [ 0, 6 ]), i % 7);
            day.isToday = day.year === nowYear && day.month === nowMonth && day.date === nowDate;
            day.isActive = day.year === activeYear && day.month === activeMonth && day.date === activeDate;
        });

        this.calendarGrid = grid;
        this.calendarYear = year;
        this.calendarMonth = month;
        this.calendarMonthName = monthName;
        this.calendarFullDate = date;
    }

    // public patchCalendarGrid () : boolean {
    //     const isSameMonth = (
    //         this.calendarGrid && this.calendarFullDate && this.mainModel &&
    //         this.calendarFullDate.getFullYear() === this.mainModel.getFullYear() &&
    //         this.calendarFullDate.getMonth() === this.mainModel.getMonth()
    //     );
    //
    //     if (!isSameMonth) {
    //         return false;
    //     }
    //
    //     const date = this.mainModel.getDate();
    //
    //     this.calendarGrid = this.calendarGrid.map(day => {
    //         if (!day.isTail && !day.isHead) {
    //             day.isActive = date === day.date;
    //         }
    //
    //         return day;
    //     });
    //
    //     return true;
    // }


    // ----------------------------
    // TIME
    // ----------------------------

    public setupSlider (el : ElementRef, type : 'h' | 'm') : void {
        if (el){
            const nativeElement = el.nativeElement;

            this.slidersUnlistens[type] = this.renderer.listen(nativeElement, 'mousedown', e => {
                this.activeTimeSlider = nativeElement;
                this.activeTimeSliderType = type;
                this.onTimeSliderMouseDown(e);
            });
        } else {
            this.activeTimeSlider = null;
            this.activeTimeSliderType = null;

            if (this.slidersUnlistens[type]) {
                this.slidersUnlistens[type]();
                this.slidersUnlistens[type] = null;
            }
        }
    }

    public onTimeSliderMouseDown (e : any) : void {
        // e.stopPropagation();
        // e.preventDefault();
        this.domService.toggleDragging(true);
        this.calcSlider(e);
    }

    // @HostListener('document:mousedown', [ '$event' ])
    public onMouseDown (e : any) : void {
        this.isLastClickByBubble = this.domService.hasEventMark(e, this.dtPickerBubbleMouseDownEventMark);
    }

    // @HostListener('document:mouseup')
    public onMouseUp () : void {
        if (this.activeTimeSliderType || this.activeTimeSlider) {
            this.domService.toggleDragging(false);
            this.activeTimeSliderType = null;
            this.activeTimeSlider = null;
        }
    }

    // @HostListener('document:mousemove', [ '$event' ])
    public calcSlider (e : any) : void {
        if (!this.activeTimeSliderType || !this.activeTimeSlider) {
            return;
        }

        if (!this.mainModel) {
            this.mainModel = this.getToday();
            this.generateCalendarGrid(this.mainModel);
        }

        const parts = this.activeTimeSliderType === 'h' ? 23 : 12;
        const sliderRect = this.activeTimeSlider.getBoundingClientRect();
        const cursorX = Math.min(sliderRect.right, Math.max(sliderRect.left, e.clientX)) - sliderRect.left;
        const scale = Math.round(cursorX / (sliderRect.width / parts));
        const sliderWidth = Math.round(100 / parts * scale);

        let update = false;

        if (this.activeTimeSliderType === 'h') {
            update = this.mainModel.getHours() !== scale;
            this.mainModel.setHours(scale);
            this.hoursSliderValue = sliderWidth;
        } else {
            const minutes = Math.min(59, scale * 5);
            update = this.mainModel.getMinutes() !== minutes;
            this.mainModel.setMinutes(minutes);
            this.minutesSliderValue = sliderWidth;
        }

        if (update) {
            this.updateTimeSection();
            this.updateInputFromMainModel();
            this.emitOnChange();
        }
    }

    public onTimeInputFocus (type : 'h' | 'm') : void {
        this.activeTimeInput = type;
        this.mainModelBackup = cloneDate(this.mainModel);
    }

    public onTimeInputBlur () : void {
        this.activeTimeInput = null;
        this.mainModelBackup = null;
        this.updateTimeSection();
        this.updateInputFromMainModel();
        this.emitOnChange();
        // console.log('blur:', this.datetimeService.getMoment(this.mainModel).format('DD.MM.YYYY HH:mm:ss'));
    }

    public onTimeInputChange (value : any, isHours : boolean) : void {
        if (!this.mainModel) {
            this.mainModel = this.getToday();
            this.mainModelBackup = cloneDate(this.mainModel);
            this.generateCalendarGrid(this.mainModel);
        }

        let num = int((value || '').trim());
        const isNumber = isFinite(num);

        if (isNumber) {
            num = Math.max(0, Math.min(isHours ? 23 : 59, num));
        }

        if (!isNumber) {
            this.mainModel = cloneDate(this.mainModelBackup);
        } else if (isHours) {
            this.mainModel.setHours(num);
        } else {
            this.mainModel.setMinutes(this.roundMinutes(num));
        }

        // console.log(num, this.mainModel);

        this.updateTimeSection();
        this.updateInputFromMainModel();
        this.emitOnChange();

        // console.log(num);
        // console.log('input:', this.datetimeService.getMoment(this.mainModel).format('DD.MM.YYYY HH:mm:ss'));
    }

    public updateTimeSection () : void {
        const hours = this.mainModel ? this.mainModel.getHours() : null;
        const minutes = this.mainModel ? this.mainModel.getMinutes() : null;

        // time suffix
        this.timeSuffix = hours === null || hours < 12 ? 'am' : 'pm';

        // hours input
        if (this.activeTimeInput !== 'h') {
            this.hoursInputModel = hours === null ? '' : this.zeroPad(this.isTwelveHoursFormat ? (hours % 12 || 12) : hours);
        }

        // minutes input
        if (this.activeTimeInput !== 'm') {
            this.minutesInputModel = minutes === null ? '' : this.zeroPad(minutes);
        }

        // sliders
        if (this.activeTimeSliderType !== 'h') {
            this.hoursSliderValue = Math.round(100 / 23 * (hours || 0));
        }

        if (this.activeTimeSliderType !== 'm') {
            this.minutesSliderValue = Math.round(100 / 59 * (minutes || 0));
        }
    }

    public changeTimeSuffix (toTimeSuffix : 'am' | 'pm') : void {
        if (this.mainModel) {
            if (this.timeSuffix === toTimeSuffix) {
                return;
            }

            const hours = this.mainModel.getHours();

            if (this.timeSuffix === 'am' && hours > 11 || this.timeSuffix === 'pm' && hours < 12) {
                console.warn('Inconsistent timeSuffix and current hours:', this.timeSuffix, hours);
            }

            this.mainModel.setHours(hours + 12 * (toTimeSuffix === 'am' ? -1 : 1));
        } else {
            const hours = toTimeSuffix === 'am' ? 0 : 12;
            this.mainModel = this.getToday(hours);
            this.generateCalendarGrid(this.mainModel);
        }

        this.timeSuffix = toTimeSuffix;

        this.updateTimeSection();
        this.updateInputFromMainModel();
        this.emitOnChange();
    }

    public onSelectCurrentTime () : void {
        const date = new Date();

        if (this.mainModel) {
            this.mainModel.setHours(date.getHours(), this.roundMinutes(date.getMinutes()), 0, 0);
        } else {
            date.setMinutes(this.roundMinutes(date.getMinutes()));
            this.mainModel = date;
            this.generateCalendarGrid(date);
        }

        this.updateTimeSection();
        this.updateInputFromMainModel();
        this.emitOnChange();
    }
}
