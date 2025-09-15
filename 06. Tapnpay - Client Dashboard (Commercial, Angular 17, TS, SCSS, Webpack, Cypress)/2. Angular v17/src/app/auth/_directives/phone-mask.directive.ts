import {Directive, ElementRef, Input, OnInit, OnDestroy, Renderer2} from '@angular/core';
import {AbstractControl} from '@angular/forms';
import {Subscription} from "rxjs";


@Directive({
  selector: '[appPhoneMask]'
})
export class PhoneMaskDirective implements OnInit, OnDestroy {

  // @ts-ignore
  private _phoneControl: AbstractControl;
  // @ts-ignore
  private _startedControlValue: string = '';

  @Input()
  set phoneControl(control: AbstractControl) {
    this._phoneControl = control;
  }

  @Input()
  set startedControlValue(value: string) {
    this._startedControlValue = value;
  }

// @ts-ignore
  private sub$: Subscription;
  private phoneValueMaxLength = 10;

  constructor(private el: ElementRef, private renderer: Renderer2) {
  }

  ngOnInit() {
    this.phoneValidate();
  }

  ngOnDestroy() {
    this.sub$.unsubscribe();
  }

  private readonly phoneInputIdSelector = '#main_reg_tel';

  phoneValidate() {

    this.sub$ = this._phoneControl.valueChanges.subscribe((currentControlValue: string) => {
      if (currentControlValue) {
        let prevControlValue: string = this._startedControlValue || '';
        let lastChar: string = !!prevControlValue && prevControlValue.length > 0 ? prevControlValue.charAt(prevControlValue.length - 1) : '0';
        // remove all mask characters (keep only numeric)
        let newVal: string = '';
        newVal = currentControlValue.replace(/\D/g, '');

        //cut the string to the maximum length of phone number
        if (newVal && newVal.length > this.phoneValueMaxLength) {
          newVal = newVal.slice(0, this.phoneValueMaxLength);
        }

        let start = this.renderer.selectRootElement(this.phoneInputIdSelector).selectionStart;
        let end = this.renderer.selectRootElement(this.phoneInputIdSelector).selectionEnd;

        if (currentControlValue.length < prevControlValue.length) {
          if (prevControlValue.length < start) {
            if (lastChar == ')') {
              newVal = newVal.slice(0, newVal.length - 1);
            }
          }
          if (newVal.length == 0) {
            newVal = '';
          } else if (newVal.length <= 3) {
            newVal = this.replaceStringByRegex(newVal, /^(\d{0,3})/, '($1');
          } else if (newVal.length <= 6) {
            newVal = this.replaceStringByRegex(newVal, /^(\d{0,3})(\d{0,3})/, '($1) $2')
          } else {
            newVal = this.replaceStringByRegex(newVal, /^(\d{0,3})(\d{0,3})(.*)/, '($1) $2-$3');
          }

          this._phoneControl.setValue(newVal, {emitEvent: false});
          this.renderer.selectRootElement(this.phoneInputIdSelector).setSelectionRange(start, end);
        } else {
          var removedD = currentControlValue.charAt(start);
          if (newVal.length == 0) {
            newVal = '';
          } else if (newVal.length <= 3) {
            newVal = `(${newVal}`;
          } else if (newVal.length <= 6) {
            newVal = `(${newVal.slice(0, 3)}) ${newVal.slice(3)}`;
          } else {
            newVal = `(${newVal.slice(0, 3)}) ${newVal.slice(3, 6)}-${newVal.slice(6)}`;
          }


          if (prevControlValue.length >= start) {
            if (['(', ')', ' ', '-'].includes(removedD)) {
              const increment = removedD === ')' ? 2 : 1;
              start += increment;
              end += increment;
            }

            this.setControlValue(newVal);
            this.renderer.selectRootElement(this.phoneInputIdSelector).setSelectionRange(start, end);
          } else {
            this.setControlValue(newVal);
            this.renderer.selectRootElement(this.phoneInputIdSelector).setSelectionRange(start + 4, end + 4); // +2 because of wanting standard typing
          }
        }
      }
    });
  }

  private setControlValue(value: string) {
    this._phoneControl.setValue(value, {emitEvent: false});
  }

  private replaceStringByRegex(str: string, regex: RegExp, replaceValue: string) {
    return str.replace(regex, replaceValue);
  }
}
