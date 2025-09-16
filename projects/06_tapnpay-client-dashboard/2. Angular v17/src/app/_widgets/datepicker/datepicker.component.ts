import {
    AfterViewInit,
    Component,
    ElementRef,
    forwardRef,
    HostListener,
    Input,
    OnChanges,
    OnDestroy,
    OnInit,
    Renderer2,
    SimpleChanges,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {
    AbstractControl,
    ControlValueAccessor,
    NG_VALIDATORS,
    NG_VALUE_ACCESSOR,
    ValidationErrors,
    Validator
} from '@angular/forms';
import {TranslateService} from '@ngx-translate/core';
import {findIndex, forEach, forIn, includes, maxBy, padStart, range} from 'lodash';
import {Subscription} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../services/device.service';
import {DomService} from '../../services/dom.service';
import {DatetimeService} from '../../services/datetime.service';
import {cloneDate, int, isEmpty} from '../../lib/utils';
import {Moment} from "moment";

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
// 4. Поля ввода времени
// 5. Слайдеры времени
// 6. emitOnChange()
// 7. onTouch()
// ----------------------
// Поле ввода минут/часов:
// 1. если основной модели ещё не существует (главный инпут пуст),
//    создать new Date() и заполнить время нулями. Сохранить
//    этот объект в главную модель.
// 2. Из главной модели (она теперь по-любому есть) сделать резервную копию.
// 3. При вводе часов/минут, если состояние этого поля становится невалидным,
//    то брать резервную копию, подставлять в главную модель и обновлять ВСЁ!
//    (слайдер, соседнее поле часов/мин, календарь, основное поле ввода и главную модель)
// 4. При блюре в главной модели по-любому находится валидное значение, и весь UI
//    находится в правильном состоянии. Нужно лишь обновить из модели
//    только что заблюренное поле. И удалить резервную копию даты.
// ------------------------
// Слайдер:
// 1. рассчитывать значение ползунка; вычислять часы и минуты;
//    конвертировать 12 -> 24, если нужно; обновить интерфейс.
// ------------------------
// object, date, moment, iso, timestamp
// ------------------------
// Календарь нужно обновлять после обновления времени только в том случае, если mainModel создана с нуля

// при кейапе проверять время, если валидно, то писать в модель и обновлять главный инпут
// при блюре проверять валидность


// - Поменялся язык -> обновить поле, обновить пикер
// - value поменялось через writeValue -> распарсить, обновить поле, обновить пикер
//   если распаршенное значение инвалидно -> сбросить в null, обновить поле, обновить пикер, уведомить через onChange
// - Пользователь изменил ввод в UI -> вычислить value, обновить поле, уведомить через onChange
// - Пользователь ввёл неверное значение в поле
// ------------------------
// required будет проверяться FormBuilder'ом
// валидность даты будет проверяться валидатором, который напишу позже

// console.log('after conversion:', this.datetimeService.getMoment(this.mainModel).format('DD.MM.YYYY HH:mm:ss'));


const BUBBLE_WIDTH = 462;
const BUBBLE_HEIGHT = 334;
const POPUP_ITEM_HEIGHT = 44;

interface PopupDisplayItemData {
    value: string | number;
    index: number;
    isActive: boolean;
}

interface PopupDisplayData {
    offset: number;
    items: PopupDisplayItemData[];
}

interface mobilePickerState {
    touchedItemType: TouchItemType,
    prevY: null | number,
    mobilePickerRenderedItems: {
        date: PopupDisplayData,
        month: PopupDisplayData,
        year: PopupDisplayData,
        hours: PopupDisplayData,
        minutes: PopupDisplayData,
        timeSuffix: PopupDisplayData
    }
}

type TouchItemType = 'date' | 'month' | 'year' | 'hours' | 'minutes' | 'timeSuffix';

@Component({
    selector: 'datepicker',
    exportAs: 'datepicker',
    templateUrl: './datepicker.component.html',
    styleUrls: ['./datepicker.component.scss'],
    encapsulation: ViewEncapsulation.None,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => DatepickerComponent),
            multi: true
        },

        {
            provide: NG_VALIDATORS,
            useExisting: forwardRef(() => DatepickerComponent),
            multi: true,
        },
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
        '[class.datepicker_active]': 'activePicker',
    }
})
export class DatepickerComponent implements OnInit, OnDestroy, OnChanges, AfterViewInit, ControlValueAccessor, Validator {
    @ViewChild('inputEl')
    public inputEl: ElementRef;

    @ViewChild('datePickerBtn', {read: ElementRef})
    public datePickerBtn: ElementRef<HTMLElement>;

    public subs: Subscription[] = [];

    // ---------------------

    public viewportBreakpoint: ViewportBreakpoint = null;

    public moment: any = null;

    public inputModel: string = '';

    //
    // ------------------------

    public onTouched: any = () => {
    };

    public onChange: any = (_: any) => {
    };

    public onChanged: any = () => {
    };

    public onValidationChange: any = () => {
    };

    // Options
    // ------------------------

    private _isDisabled: boolean = false;

    @Input()
    public set isDisabled(value: boolean) {
        if ((this._isDisabled = value)) {
            this.destroyPickerRendering();
        }
    }

    public get isDisabled(): boolean {
        return this._isDisabled;
    }

    public _firstDayOfWeek: 'mon' | 'sun' | 'auto';

    @Input()
    public firstDayOfWeek: 'mon' | 'sun' | 'auto' = 'auto';

    public _format: string;

    @Input()
    public format: string = 'YYYY-MM-DD'; // TODO: set default format

    public _type: 'timestamp' | 'iso' | 'date' | 'moment' | 'object' = 'timestamp';

    @Input()
    public type: 'timestamp' | 'iso' | 'date' | 'moment' | 'object';

    public _boundingEl: ElementRef;

    @Input()
    public boundingEl: ElementRef;

    @Input()
    public placeholder: string = '';

    public hasTimePicker: boolean;

    public isTwelveHoursFormat: boolean;

    @Input()
    public isShowDatePicker: boolean = true;

    // defaultValue: null, // well be set by client component
    // isRequired: true  // checked by formBuilder

    // -----------------------------

    public activePicker: 'bubble' | 'popup' = null;
    public isTouch: boolean = false;
    public isInputFocus: boolean = false;

    public activeDateSelectLayout: 'calendar' | 'years' | 'months' = null;
    public calendarYear: number;
    public calendarMonth: number;
    public calendarMonthName: string;
    public calendarFullDate: Date;

    public renderedYearsSelectGrid: number[];
    public renderedMonthsSelectGrid: any[];
    public renderedDaysSelectGrid: any[];
    public renderedShotWeekDayNamesList: string[];

    public nowDateForSelect: any;


    // -------------------------------------

    @ViewChild('hoursSlider')
    public set hoursSlider(el: ElementRef) {
        this.setupSlider(el, 'h');
    }

    @ViewChild('minutesSlider')
    public set minutesSlider(el: ElementRef) {
        this.setupSlider(el, 'm');
    }

    public slidersUnlistens: any = {};
    public activeTimeSlider: HTMLDivElement;
    public activeTimeSliderType: 'h' | 'm';
    public hoursSliderValue: number = 0;
    public minutesSliderValue: number = 0;
    public mainModel: Date;
    public mainModelBackup: Date;
    public timeFormatSuffix: 'am' | 'pm' = 'am';
    public activeTimeInput: 'h' | 'm';
    public hoursInputModel: string = '';
    public minutesInputModel: string = '';

    public isLastClickOnPickerPanelZone: boolean = false;
    public bubblePosition: number;

    // --------------------------------------

    @ViewChild('popup', {read: ElementRef})
    public popupEl: ElementRef;

    public listeners: any[] = [];

    @Input() public minDate: Date | string | Moment | null = null;
    @Input() public maxDate: Date | string | null = null;
    @Input() public isBlockToSelectDayBeforeToday: boolean = false;

    constructor(
        public el: ElementRef,
        public renderer: Renderer2,
        public deviceService: DeviceService,
        public domService: DomService,
        public datetimeService: DatetimeService,
        public translateService: TranslateService
    ) {
        this.isTouch = this.deviceService.device.touch;
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;

        this.addSub(
            this.deviceService.onResize.subscribe((message) => {
                if (message.breakpointChange) {
                    this.viewportBreakpoint = this.deviceService.viewportBreakpoint;

                    if (this.activePicker === 'bubble') {
                        this.activePicker = null;
                    }

                }
            })
        );

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

    public ngOnInit(): void {
        const rootElement = document.documentElement;
        this.listeners = [
            ...this.listeners,
            this.renderer.listen(rootElement, 'click', (e) => this.onDocumentClick(e)),
            this.renderer.listen(rootElement, 'mousedown', (e) => this.onDocumentMouseDown(e)),
            this.renderer.listen(rootElement, 'mouseup', (_e) => this.onDocumentMouseUp()),
        ];
    }

    public ngAfterViewInit(): void {
        this.setupPopupPicker();
    }

    public ngOnDestroy(): void {
        this.listeners.forEach(unlisten => unlisten());

        if (this.popupListeners) {
            this.popupListeners.forEach(unlisten => unlisten());
            this.popupListeners = null;
        }

        if (this.bubbleListeners) {
            this.bubbleListeners.forEach(unlisten => unlisten());
            this.bubbleListeners = null;
        }

        this.destroyPopupPicker();
        this.subs.forEach(sub => sub.unsubscribe());
    }

    public ngOnChanges(changes: SimpleChanges): void {
        this.parseOptions();  // TODO: parse only if options changed
    }

    public parseOptions(): void {
        this._firstDayOfWeek = this.firstDayOfWeek === 'auto' ? this.datetimeService.getFirstDayOfWeek() : this.firstDayOfWeek;
        this._format = this.datetimeService.getFormatByAlias((this.format || '').trim() || 'YYYY-MM-DD');
        this._type = includes(['timestamp', 'iso', 'date', 'moment', 'object'], this.type) ? this.type : 'timestamp';
        this._boundingEl = this.boundingEl;
        this.hasTimePicker = this.datetimeService.hasFormatTime(this._format);
        this.isTwelveHoursFormat = this.hasTimePicker && this.datetimeService.isTwelveHoursFormat(this._format);
    }

    public addSub(sub: Subscription): void {
        this.subs = [...this.subs, sub];
    }


    // ControlValueAccessor impl.
    // ---------------------------

    set(value: any) {
        this.mainModel = value;


        this.registerOnChange(this.mainModel);
        this.onValidationChange();
    }

    // source - object, date, moment, iso, timestamp
    public writeValue(source: Object | string | number | Date | any): void {
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

    public registerOnChange(fn: any): void {
        this.onChange = fn;
    }

    public registerOnTouched(fn: any): void {
        this.onTouched = fn;
    }

    public setDisabledState(isDisabled: boolean): void {
        this._isDisabled = isDisabled;
    }

    public registerOnValidatorChange?(fn: () => void): void {
        this.onValidationChange = fn;
    }


    // MAIN INPUT & MODEL
    // ---------------------------

    public updateInputFromMainModel(): void {
        this.inputModel = this.mainModel && this.datetimeService.getMoment(this.mainModel).format(this._format) || '';
        // console.warn('moment -> input', this.inputModel);
    }

    public updateMainModelFromInput(): void {
        const moment = this.datetimeService.parse((this.inputModel || '').trim(), this._format);
        this.mainModel = moment && moment.toDate();
        // console.warn('input -> moment', this.mainModel);
    }

    public onInputFocus(): void {
        this.isInputFocus = true;
    }

    public onInputBlur(): void {
        this.isInputFocus = false;

        this.updateMainModelFromInput();
        this.updateInputFromMainModel();

        this.emitOnChange();
        this.onTouched();
    }

    public onInputType(): void {
        this.updateMainModelFromInput();
        this.emitOnChange();
    }

    public emitOnChange(): void {
        let value: any = null;

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


    public clickOnPickerInputBtn(event: MouseEvent): void {
        this.domService.markEvent(event, `clickOnPickerInputButton`);
        if (!this.activePicker) {
            this.initPickerRendering();
            return;
        } else {
            this.destroyPickerRendering();
        }
    }

    // @HostListener('document:click', [ '$event' ])
    public onDocumentClick(event: MouseEvent): void {

        const isClickOnPickerInputBtn = this.domService.isHasEventMark(event, 'clickOnPickerInputButton');
        const isClickOnPickerZone = this.domService.isHasEventMark(event, 'clickOnPickerPanelZone');

        if (isClickOnPickerInputBtn) {
            this.closeOpenedPickers(event);
        }

        if (!isClickOnPickerZone && !isClickOnPickerInputBtn) {
            if (this.activePicker) {
                this.destroyPickerRendering();
            }
        }
    }


    private closeOpenedPickers(event: MouseEvent) {
        const eventTargetElement = event.target as HTMLElement;
        const pickerToggleBtn = this.datePickerBtn.nativeElement as HTMLElement;
        const childrenPickerToggleBtnElements = Array.from(pickerToggleBtn.children);
        const isClickedBtnNotPickerBtn = pickerToggleBtn !== eventTargetElement;
        const isClickedBtnNotPickerBtnChildren = childrenPickerToggleBtnElements.indexOf(eventTargetElement) === -1;
        const isActiveDesktopPicker = this.activePicker && this.activePicker === 'bubble';

        if (isClickedBtnNotPickerBtn && isClickedBtnNotPickerBtnChildren) {
            if (isActiveDesktopPicker) {
                this.setDesktopPickerState(false);
            }
        }
    }

    public initPickerRendering(): void {
        if (this.activePicker === (this.isTouch ? 'popup' : 'bubble')) {
            return;
        }

        if (this.isTouch) {
            this.setMobilePickerState(true);
        } else {
            this.setDesktopPickerState(true);
        }
    }

    public destroyPickerRendering(): void {
        if (this.activePicker === 'bubble') {
            this.setDesktopPickerState(false);
        } else if (this.activePicker === 'popup') {
            this.setMobilePickerState(false);
        }

        this.onTouched();
    }


    // POPUP
    // ---------------------------

    // @ViewChild('popupItemsDate')
    // public popupItemsDate : ElementRef;
    //
    // @ViewChild('popupItemsMonth')
    // public popupItemsMonth : ElementRef;
    //
    // @ViewChild('popupItemsYear')
    // public popupItemsYear : ElementRef;
    //
    // @ViewChild('popupItemsHours')
    // public popupItemsHours : ElementRef;
    //
    // @ViewChild('popupItemsMinutes')
    // public popupItemsMinutes : ElementRef;
    //
    // @ViewChild('popupItemsSuffix')
    // public popupItemsSuffix : ElementRef;

    public popupModel: Date;

    public popupListeners: any[];

    public bubbleListeners: any[];

    public mobilePickerState: mobilePickerState = {
        touchedItemType: null,
        prevY: 0,
        mobilePickerRenderedItems: {
            date: {
                offset: 0,
                items: []
            },
            month: {
                offset: 0,
                items: []
            },
            year: {
                offset: 0,
                items: []
            },
            hours: {
                offset: 0,
                items: []
            },
            minutes: {
                offset: 0,
                items: []
            },
            timeSuffix: {
                offset: 0,
                items: []
            }
        }
    };

    isPopupVisible: boolean = false;

    public setupPopupPicker(): void {
        if (this.isTouch && this.popupEl) {
            this.renderer.appendChild(document.body, this.popupEl.nativeElement);
        }

        // defer(() => this.activate());
    }

    public destroyPopupPicker(): void {
        if (this.isTouch && this.popupEl && this.popupEl.nativeElement.parentElement === document.body) {
            this.renderer.removeChild(document.body, this.popupEl.nativeElement);
        }
    }

    public setMobilePickerState(isActive: boolean): void {
        if (isActive) {
            this.popupModel = this.getmobilePickerInitialDate();
            this.generatePopupData();
            this.popupListeners = [
                this.renderer.listen('document', 'touchmove', e => this.onPopupTouchMove(e)),
                this.renderer.listen('document', 'touchend', e => this.onPopupTouchEnd(e)),
                this.renderer.listen('document', 'touchcancel', e => this.onPopupTouchEnd(e)),
            ];
            this.renderer.addClass(document.body, 'datepicker-no-scroll');
            this.isPopupVisible = true;
            this.activePicker = 'popup';
        } else {
            this.activePicker = null;
            this.isPopupVisible = false;
            this.renderer.removeClass(document.body, 'datepicker-no-scroll');
            this.popupModel = null;
            this.mobilePickerState.touchedItemType = null;
            this.mobilePickerState.prevY = 0;
            forIn(this.mobilePickerState.mobilePickerRenderedItems, display => {
                display.items = [];
                display.offset = 0;
            });
            if (this.popupListeners) {
                this.popupListeners.forEach(unlisten => unlisten());
                this.popupListeners = null;
            }
        }
    }

    public getmobilePickerInitialDate(): Date {
        const date = this.mainModel ? cloneDate(this.mainModel) : this.getToday(0, 0, 0, 0);
        const minutes = Math.round(date.getMinutes() / 5) * 5;
        date.setMinutes(minutes >= 60 ? 0 : minutes);
        return date;
    }

    public generatePopupData(): void {
        const model = this.popupModel;

        // ---------------------

        const modelDate = this.popupModel.getDate();

        this.mobilePickerState.mobilePickerRenderedItems.date.items = range(1, this.getDaysInMonth(model) + 1).map((value, index) => {
            if (value === modelDate) {
                this.mobilePickerState.mobilePickerRenderedItems.date.offset = -1 * POPUP_ITEM_HEIGHT * index;
            }

            return {
                value,
                index,
                isActive: value === modelDate
            };
        });

        // ---------------------

        const modelMonth = this.popupModel.getMonth();

        this.mobilePickerState.mobilePickerRenderedItems.month.items = this.datetimeService.getShortMonths().map((value, index) => {
            if (index === modelMonth) {
                this.mobilePickerState.mobilePickerRenderedItems.month.offset = -1 * POPUP_ITEM_HEIGHT * index;
            }

            return {
                value,
                index,
                isActive: index === modelMonth
            };
        });

        // ---------------------

        const modelYear = this.popupModel.getFullYear();

        this.mobilePickerState.mobilePickerRenderedItems.year.items = range(modelYear - 10, modelYear + 10).map((value, index) => {
            if (value === modelYear) {
                this.mobilePickerState.mobilePickerRenderedItems.year.offset = -1 * POPUP_ITEM_HEIGHT * index;
            }

            return {
                value,
                index,
                isActive: value === modelYear
            };
        });

        // ---------------------

        if (this.hasTimePicker) {
            let modelHours = this.popupModel.getHours();
            let modelSuffix = null;
            let startHour = 0;
            let endHour = 24;

            if (this.isTwelveHoursFormat) {
                modelSuffix = modelHours < 12 ? 'AM' : 'PM';
                modelHours = modelHours % 12 || 12;
                startHour = 1;
                endHour = 13;
            }

            this.mobilePickerState.mobilePickerRenderedItems.timeSuffix.items = ['AM', 'PM'].map((value, index) => {
                if (value === modelSuffix) {
                    this.mobilePickerState.mobilePickerRenderedItems.timeSuffix.offset = -1 * POPUP_ITEM_HEIGHT * index;
                }

                return {
                    value: value,
                    index,
                    isActive: value === modelSuffix
                };
            });

            // -----------------------

            this.mobilePickerState.mobilePickerRenderedItems.hours.items = range(startHour, endHour).map((value, index) => {
                if (value === modelHours) {
                    this.mobilePickerState.mobilePickerRenderedItems.hours.offset = -1 * POPUP_ITEM_HEIGHT * index;
                }

                return {
                    value,
                    index,
                    isActive: value === modelHours
                };
            });

            // ---------------------

            const modelMinutes = this.popupModel.getMinutes();

            this.mobilePickerState.mobilePickerRenderedItems.minutes.items = range(0, 60, 5).map((value, index) => {
                if (value === modelMinutes) {
                    this.mobilePickerState.mobilePickerRenderedItems.minutes.offset = -1 * POPUP_ITEM_HEIGHT * index;
                }

                return {
                    value: this.zeroPad(value),
                    index,
                    isActive: value === modelMinutes
                };
            });
        }

        // ---------------------

        forIn(this.mobilePickerState.mobilePickerRenderedItems, (_, key) => {
            this.updatePopupItems(key);
        });
    }

    // когда прокрутка, пересчитать isActive
    // когда отпускает, нужно пересчитать число и установить новую дату

    public updatePopupItems(type: string): void {
        const offsetCount = Math.round(this.mobilePickerState.mobilePickerRenderedItems[type].offset / POPUP_ITEM_HEIGHT);
        const items = this.mobilePickerState.mobilePickerRenderedItems[type].items;
        const itemsCount = items.length;
        let replaceCount = Math.floor(itemsCount / 2);

        if (type === 'timeSuffix') {

        } else if (offsetCount >= -1 || (offsetCount + itemsCount) <= 1) {
            if (type === 'year') {
                let yearsRange;

                if (offsetCount >= -1) {
                    const firstYear = items[0].value;
                    yearsRange = range(firstYear - 10, firstYear);
                } else {
                    const lastYear = items[itemsCount - 1].value;
                    yearsRange = range(lastYear + 1, lastYear + 11);
                }

                const newItems = yearsRange.map((value, index) => {
                    return {
                        value,
                        index,
                        isActive: false
                    };
                });

                if (offsetCount >= -1) {
                    this.mobilePickerState.mobilePickerRenderedItems.year.items = [...newItems, ...items.slice(0, -10)];
                    this.mobilePickerState.mobilePickerRenderedItems.year.offset -= POPUP_ITEM_HEIGHT * 10;
                } else {
                    this.mobilePickerState.mobilePickerRenderedItems.year.items = [...items.slice(10), ...newItems];
                    this.mobilePickerState.mobilePickerRenderedItems.year.offset += POPUP_ITEM_HEIGHT * 10;
                }
            } else {
                if (offsetCount >= -1) {
                    replaceCount *= -1;
                }

                this.mobilePickerState.mobilePickerRenderedItems[type].items = [...items.slice(replaceCount), ...items.slice(0, replaceCount)];
                this.mobilePickerState.mobilePickerRenderedItems[type].offset += replaceCount * POPUP_ITEM_HEIGHT;
            }
        }
    }

    public onPopupTouchStart(event: TouchEvent, touchItemType: TouchItemType): void {
        // console.log('start');
        this.mobilePickerState.touchedItemType = touchItemType;
        this.mobilePickerState.prevY = event.touches[0].clientY;
    }

    public onPopupTouchMove(e: any): void {
        if (!this.mobilePickerState.touchedItemType) {
            return;
        }

        const {touchedItemType, prevY} = this.mobilePickerState;
        const currentY = e.touches[0].clientY;
        const deltaY = prevY - currentY;
        let newOffset = this.mobilePickerState.mobilePickerRenderedItems[touchedItemType].offset - deltaY;
        newOffset = touchedItemType === 'timeSuffix' ? Math.max(-1 * POPUP_ITEM_HEIGHT, Math.min(0, newOffset)) : newOffset;

        const itemIndex = Math.abs(Math.round(newOffset / POPUP_ITEM_HEIGHT));
        const items = this.mobilePickerState.mobilePickerRenderedItems[touchedItemType].items;
        const targetItem = items[itemIndex];

        if (!targetItem.isActive) {
            items.forEach(item => item.isActive = item === targetItem);
        }

        this.mobilePickerState.prevY = currentY;
        this.mobilePickerState.mobilePickerRenderedItems[touchedItemType].offset = newOffset;

        this.updatePopupItems(touchedItemType);
    }

    public onPopupTouchEnd(_e: any): void {
        // console.log(e.type);
        const {touchedItemType} = this.mobilePickerState;

        if (touchedItemType) {
            this.mobilePickerState.touchedItemType = null;
            this.mobilePickerState.mobilePickerRenderedItems[touchedItemType].offset = Math.round(this.mobilePickerState.mobilePickerRenderedItems[touchedItemType].offset / POPUP_ITEM_HEIGHT) * POPUP_ITEM_HEIGHT;

            // -----------------
            const displays = this.mobilePickerState.mobilePickerRenderedItems;

            let date = displays.date.items.find(d => d.isActive).value;
            const month = displays.month.items.find(m => m.isActive).index;
            const year = <number>displays.year.items.find(y => y.isActive).value;
            let hours: number = 0;
            let minutes: number = 0;

            if (this.hasTimePicker) {
                hours = <number>displays.hours.items.find(hour => hour.isActive).value;
                minutes = <number>displays.minutes.items.find(minute => minute.isActive).value;

                if (this.isTwelveHoursFormat) {
                    const timeSuffix = displays.timeSuffix.items.find(ts => ts.isActive).value;
                    hours = timeSuffix === 'AM' ? (hours % 12) : (hours === 12 ? 12 : (hours + 12));
                }
            }

            if (touchedItemType === 'year' && month === 1 || touchedItemType === 'month') {
                const daysInMonth = this.getDaysInMonth(new Date(year, month, 1));
                let dateItems = displays.date.items;
                const currentDaysCount = dateItems.length;
                // const daysOffset = Math.round(displays.date.offset / POPUP_ITEM_HEIGHT);

                // console.log(year, month, daysInMonth, currentDaysCount);

                if (currentDaysCount < daysInMonth) {
                    const maxItemIndex = dateItems.indexOf(maxBy(dateItems, (item: any) => item.value));

                    const daysToAdd = range(currentDaysCount + 1, daysInMonth + 1).map(value => {
                        return {
                            value,
                            isActive: false
                        };
                    });

                    dateItems.splice(maxItemIndex + 1, 0, ...(<any>daysToAdd));

                    displays.date.offset = -1 * findIndex(dateItems, (item: any) => item.isActive) * POPUP_ITEM_HEIGHT;
                } else if (currentDaysCount > daysInMonth) {
                    displays.date.items = dateItems = dateItems.filter(item => <number>item.value <= daysInMonth);

                    if (<number>date > daysInMonth) {
                        const maxDate = maxBy(dateItems, (item: any) => item.value);
                        maxDate.isActive = true;
                        date = maxDate.value;
                    }

                    const activeItem = dateItems.find(item => item.isActive);
                    const activeItemIndex = dateItems.indexOf(activeItem);

                    if (activeItemIndex < 2) {
                        displays.date.items = [...dateItems.slice(-3), ...dateItems.slice(0, -3)];
                    } else if ((dateItems.length - activeItemIndex - 1) < 2) {
                        displays.date.items = [...dateItems.slice(3), ...dateItems.slice(0, 3)];
                    }

                    displays.date.offset = -1 * dateItems.indexOf(activeItem) * POPUP_ITEM_HEIGHT;
                }
            }

            // --------------

            this.popupModel = new Date(year, month, <number>date, hours, minutes, 0, 0);

            // console.log(this.datetimeService.getMoment(this.popupModel).format('DD.MM.YYYY HH:mm:ss'));

            // console.log(`${date}.${month + 1}.${year} ${hours}:${minutes}`);
        }
    }

    public onPopupClose(confirm: boolean): void {
        if (confirm) {
            this.mainModel = cloneDate(this.popupModel);
            this.updateInputFromMainModel();
            this.emitOnChange();
        }

        this.onTouched();
        this.setMobilePickerState(false);
    }


    // BUBBLE
    // ---------------------------

    public onBubbleClick(e: any): void {
        this.domService.markEvent(e, 'clickOnPickerPanelZone');
    }

    public onBubbleMouseDown(e: any): void {
        this.domService.markEvent(e, 'dtPickerBubbleMouseDown');
    }

    public runNowUpdater(): void {
        this.stopNowUpdater();

        const update = () => {
            const date = this.datetimeService.getMoment();

            let timeSuffix: string;
            let hours: number = date.hours();

            if (this.isTwelveHoursFormat) {
                timeSuffix = hours < 12 ? 'AM' : 'PM';
                hours = hours % 12 || 12;
            }

            this.nowDateForSelect = {
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

    public stopNowUpdater(): void {
        if (this.nowDateForSelect) {
            clearTimeout(this.nowDateForSelect.timeout);
            this.nowDateForSelect = null;
        }
    }

    public setDesktopPickerState(isActive: boolean): void {
        if (isActive) {
            this.generateCalendarGrid(this.mainModel || this.getToday());
            this.generateMonthsGrid();
            this.generateWeekdays();
            this.updateTimeSection();
            this.activeDateSelectLayout = 'calendar';
            this.runNowUpdater();
            this.calcBubblePosition();
            if (this.hasTimePicker) {
                this.bubbleListeners = [
                    this.renderer.listen(document.documentElement, 'mousemove', e => this.calcSlider(e)),
                ];
            }
            this.activePicker = 'bubble';
        } else {
            this.activePicker = null;

            if (this.bubbleListeners) {
                this.bubbleListeners.forEach(unlisten => unlisten());
                this.bubbleListeners = null;
            }

            this.renderedDaysSelectGrid = null;
            this.calendarYear = null;
            this.calendarMonth = null;
            this.calendarMonthName = null;
            this.calendarFullDate = null;

            this.renderedYearsSelectGrid = null;
            this.renderedMonthsSelectGrid = null;
            this.renderedShotWeekDayNamesList = null;
            this.activeDateSelectLayout = null;
            this.stopNowUpdater();
        }
    }

    @HostListener('click', ['$event'])
    markDatepickerClick(e) {
        this.domService.markEvent(e, 'datepickerClick');
    }

    public calcBubblePosition(): void {
        const boundEl = this.boundingEl?.nativeElement || this.getParentBounding() || document.body;
        const boundRect: ClientRect = boundEl.getBoundingClientRect();
        const rootRect = this.el.nativeElement.getBoundingClientRect();
        const viewportSize = this.deviceService.viewportClientSize;

        interface PositionData {
            posY: string;
            posX: string;
            oppositePosX: string;
            posId: number;
        }

        const positions: PositionData[] = [
            {posY: 'bottom', posX: 'right', oppositePosX: 'left', posId: 1},
            {posY: 'bottom', posX: 'left', oppositePosX: 'right', posId: 2},
            {posY: 'top', posX: 'right', oppositePosX: 'left', posId: 3},
            {posY: 'top', posX: 'left', oppositePosX: 'right', posId: 4}
        ];

        let bestPositionId = positions[0].posId;
        let maxFreeSquare = 0;

        for (const position of positions) {
            const bound = {
                top: Math.max(0, boundRect.top),
                bottom: Math.min(viewportSize.y, boundRect.bottom)
            };

            const freeX = Math.abs(rootRect[position.posX] - boundRect[position.oppositePosX]);
            const freeY = Math.abs(bound[position.posY] - rootRect[position.posY]);
            const freeSquare = Math.min(BUBBLE_WIDTH, freeX) * Math.min(BUBBLE_HEIGHT, freeY);

            if (maxFreeSquare < freeSquare) {
                maxFreeSquare = freeSquare;
                bestPositionId = position.posId;
            }

            if (BUBBLE_WIDTH * BUBBLE_HEIGHT <= freeSquare) break;
        }

        this.bubblePosition = bestPositionId;
    }


    public getParentBounding(): any {
        const widgetEl = this.el.nativeElement;
        let parent = widgetEl.parentElement || widgetEl.parentNode;

        while (parent && (!parent.dataset || !parent.dataset.bounding)) {
            parent = parent.parentElement || parent.parentNode;
        }

        return parent;
    }

    public onSelectCurrentDate(): void {
        const today = new Date();

        this.activateDate({
            year: today.getFullYear(),
            month: today.getMonth(),
            date: today.getDate()
        });
    }

    public onGridSlide(direction: number): void {
        switch (this.activeDateSelectLayout) {
            case 'calendar':
                this.generateCalendarGrid(
                    direction === 1 ?
                        this.getNextMonth(this.calendarFullDate) :
                        this.getPrevMonth(this.calendarFullDate)
                );
                break;
            case 'years':
                const startYear = this.renderedYearsSelectGrid[0] + (12 * direction);
                this.renderedYearsSelectGrid = range(startYear, startYear + 12);
                break;
        }
    }

    public switchToMonths(): void {
        this.activeDateSelectLayout = 'months';
    }

    public switchToYears(): void {
        const currentYear = this.calendarYear;

        if (!this.renderedYearsSelectGrid || !includes(this.renderedYearsSelectGrid, currentYear)) {
            this.renderedYearsSelectGrid = range(currentYear - 4, currentYear + 8);
        }

        this.activeDateSelectLayout = 'years';
    }

    public switchToCalendar(): void {
        this.activeDateSelectLayout = 'calendar';
    }

    public activateYear(year: number) {
        const date = new Date(year, this.calendarMonth, 1);
        this.generateCalendarGrid(date);
        this.switchToMonths();
    }

    public activateMonth(month: number): void {
        const date = new Date(this.calendarYear, month, 1);
        this.generateCalendarGrid(date);
        this.switchToCalendar();
    }

    public activateDate(source: any): void {
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
            this.destroyPickerRendering();
        }
    }

    public isLeapYear(year: number): boolean {
        return (year % 4 === 0) && (year % 100 !== 0) || (year % 400 === 0);
    }

    public getDaysInMonth(date: Date): number {
        const february = 28 + Number(this.isLeapYear(date.getFullYear()));
        return [31, february, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][date.getMonth()];
    }

    public getFirstDayOfMonth(date: Date): number { // 0-6 (0 - sun)
        return (new Date(date.getFullYear(), date.getMonth(), 1)).getDay();
    }

    public getPrevMonth(date: Date): Date {
        const month = date.getMonth();
        return new Date(date.getFullYear() - Number(month === 0), (month || 12) - 1, 1);
    }

    public getNextMonth(date: Date): Date {
        const month = date.getMonth();
        return new Date(date.getFullYear() + Number(month === 11), (month + 1) % 12, 1);
    }

    public getToday(hours: number = 0, minutes: number = 0, seconds: number = 0, ms: number = 0): Date {
        const date = new Date();
        date.setHours(hours, minutes, seconds, ms);
        return date;
    }

    public zeroPad(value: number | string): string {
        return padStart(String(value), 2, '0');
    }

    public roundMinutes(minutes: number): number {
        return Math.min(59, Math.round(minutes / 5) * 5);
    }

    // --------------------------------------

    public generateWeekdays(): void {
        this.renderedShotWeekDayNamesList = this.datetimeService.getShortWeekdays(<'mon' | 'sun'>this.firstDayOfWeek);
    }

    public generateMonthsGrid(): void {
        this.renderedMonthsSelectGrid = this.datetimeService.getShortMonths().map((name, month) => ({name, month}));
    }

    public generateCalendarGrid(date: Date): void {
        const now = new Date();
        const nowYear = now.getFullYear();
        const nowMonth = now.getMonth();
        const nowDay = now.getDate();

        const activeYear = this.mainModel ? this.mainModel.getFullYear() : null;
        const activeMonth = this.mainModel ? this.mainModel.getMonth() : null;
        const activeDay = this.mainModel ? this.mainModel.getDate() : null;

        const daysCount = this.getDaysInMonth(date);
        const firstDayOfMonth = this.getFirstDayOfMonth(date); // 0 (sun) - 6 (mon)

        const year = date.getFullYear();
        const month = date.getMonth();
        const monthName = this.datetimeService.getMonthName(month);
        const daySelectCalendarGrid = [];

        const prevMonthTailInDays = (this.firstDayOfWeek === 'mon' ? ((firstDayOfMonth || 7) - 1) : firstDayOfMonth) || 7;
        const head = (7 * 6) - prevMonthTailInDays - daysCount;

        const prevMonth = this.getPrevMonth(date);
        const prevMonthDaysCount = this.getDaysInMonth(prevMonth);
        const prevMonthYear = prevMonth.getFullYear();
        const prevMonthMonth = prevMonth.getMonth();

        const nextMonth = this.getNextMonth(date);
        const nextMonthYear = nextMonth.getFullYear();
        const nextMonthMonth = nextMonth.getMonth();

        for (let date: number = (prevMonthDaysCount - prevMonthTailInDays + 1); date <= prevMonthDaysCount; date++) {
            addItemTodaySelectCalendarGrid({
                isTail: true,
                isHead: false,
                isActive: false,
                year: prevMonthYear,
                month: prevMonthMonth,
                date
            })
        }

        for (let date: number = 1; date <= daysCount; date++) {
            addItemTodaySelectCalendarGrid({
                isTail: false,
                isHead: false,
                isActive: false,
                year,
                month,
                date
            })
        }

        for (let date: number = 1; date <= head; date++) {
            addItemTodaySelectCalendarGrid({
                isTail: false,
                isHead: true,
                isActive: false,
                year: nextMonthYear,
                month: nextMonthMonth,
                date,
            })
        }

        function addItemTodaySelectCalendarGrid(value) {
            daySelectCalendarGrid.push(value);
        }

        daySelectCalendarGrid.forEach((day: any, i: number) => {
            day.isHoliday = false;
            day.isWeekend = includes((this.firstDayOfWeek == 'mon' ? [5, 6] : [0, 6]), i % 7);
            day.isToday = day.year === nowYear && day.month === nowMonth && day.date === nowDay;
            day.isActive = day.year === activeYear && day.month === activeMonth && day.date === activeDay;
            day.isDisabled = this.isDayBlockedToSelectByPeriod(day);
        });

        this.renderedDaysSelectGrid = daySelectCalendarGrid;
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

    private isDayBlockedToSelectByPeriod(day: any) {
        const currentDate = this.datetimeService.getMoment(day);
        if (this.isBlockToSelectDayBeforeToday) {
            this.minDate = this.datetimeService.getMoment();
        }
        if (this.minDate && this.maxDate) {
            return currentDate.isBefore(this.minDate, 'day') || currentDate.isAfter(this.maxDate, 'day');
        }
        if (this.minDate && !this.maxDate) {
            return currentDate.isBefore(this.minDate, 'day');
        }
        if (!this.minDate && this.maxDate) {
            return currentDate.isAfter(this.maxDate, 'day');
        }
        return false;
    }

    public setupSlider(el: ElementRef, type: 'h' | 'm'): void {
        if (el) {
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

    public onTimeSliderMouseDown(e: any): void {
        // e.stopPropagation();
        // e.preventDefault();
        this.domService.toggleDragging(true);
        this.calcSlider(e);
    }

    // @HostListener('document:mousedown', [ '$event' ])
    public onDocumentMouseDown(e: any): void {
        this.isLastClickOnPickerPanelZone = this.domService.isHasEventMark(e, 'dtPickerBubbleMouseDown');
    }

    // @HostListener('document:mouseup')
    public onDocumentMouseUp(): void {
        if (this.activeTimeSliderType || this.activeTimeSlider) {
            this.domService.toggleDragging(false);
            this.activeTimeSliderType = null;
            this.activeTimeSlider = null;
        }
    }

    // @HostListener('document:mousemove', [ '$event' ])
    public calcSlider(e: any): void {
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

    public onTimeInputFocus(type: 'h' | 'm'): void {
        this.activeTimeInput = type;
        this.mainModelBackup = cloneDate(this.mainModel);
    }

    public onTimeInputBlur(): void {
        this.activeTimeInput = null;
        this.mainModelBackup = null;
        this.updateTimeSection();
        this.updateInputFromMainModel();
        this.emitOnChange();
        // console.log('blur:', this.datetimeService.getMoment(this.mainModel).format('DD.MM.YYYY HH:mm:ss'));
    }

    public onTimeInputChange(value: any, isHours: boolean): void {
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

    public updateTimeSection(): void {
        const hours = this.mainModel ? this.mainModel.getHours() : null;
        const minutes = this.mainModel ? this.mainModel.getMinutes() : null;

        // time suffix
        this.timeFormatSuffix = hours === null || hours < 12 ? 'am' : 'pm';

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

    public setTimeFormatSuffix(toTimeSuffix: 'am' | 'pm'): void {
        // Check if the suffix is already set
        if (this.timeFormatSuffix === toTimeSuffix) return;

        // Adjust model based on the new time suffix
        if (this.mainModel) {
            const mainModelHours = this.mainModel.getHours();

            const isMorning = toTimeSuffix === 'am';
            const shouldSwitchToMorning = mainModelHours >= 12 && isMorning;
            const shouldSwitchToAfternoon = mainModelHours < 12 && !isMorning;

            if (shouldSwitchToMorning || shouldSwitchToAfternoon) {
                this.mainModel.setHours(mainModelHours + 12 * (isMorning ? -1 : 1));
            }
        } else {
            // If no model is present, set a default time based on the suffix
            const defaultHours = toTimeSuffix === 'am' ? 0 : 12;
            this.mainModel = this.getToday(defaultHours);
            this.generateCalendarGrid(this.mainModel);
        }

        // Set the new suffix and update related properties
        this.timeFormatSuffix = toTimeSuffix;
        this.updateTimeSection();
        this.updateInputFromMainModel();
        this.emitOnChange();
    }


    public onSelectCurrentTime(): void {
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

    validate(control: AbstractControl): ValidationErrors | null {
        return undefined;
    }
}
