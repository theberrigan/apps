import {AbstractControl, ValidationErrors, ValidatorFn} from "@angular/forms";

export function minDateTodayValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
        if (control.value) {
            const today = new Date();
            const controlDate = new Date(control.value);
            const minDateToday = new Date(today.getFullYear(), today.getMonth(), today.getDate());
            return controlDate < minDateToday ? {'minDateToday': {value: control.value}} : null;
        } else {
            return null;
        }
    };
}

export function minDateValidator(endDate: Date | string): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
        if (control.value) {
            const controlDate = new Date(control.value);
            if (typeof endDate === 'string') {
                const minDate = new Date(endDate);
                return controlDate < minDate ? {'minDateForExtend': {value: control.value}} : null;
            } else {
                return controlDate < endDate ? {'minDateForExtend': {value: control.value}} : null;
            }
        } else {
            return null;
        }
    };
}

export function minTimeValidator(endTime: Date | string): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
        if (control.value) {
            const controlTime = new Date(control.value);
            if (typeof endTime === 'string') {
                const minTime = new Date(endTime);
                return controlTime < minTime ? {'minTimeForExtend': {value: control.value}} : null;
            } else {
                return controlTime < endTime ? {'minTimeForExtend': {value: control.value}} : null;
            }
        } else {
            return null;
        }
    };
}


export function maxDateValidator(maxDate: Date): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
        const {endDate, endTime} = control.value;
        const controlEndDate = endDate ? new Date(endDate) : null;
        const controlEndTime = endTime ? new Date(endTime) : null;
        let joinedDate = null;

        if (endDate && endTime) {
            joinedDate = new Date(
                controlEndDate.getFullYear(),
                controlEndDate.getMonth(),
                controlEndDate.getDate(),
                controlEndTime.getHours()
            );
        }
        if (endDate && !endTime) {
            joinedDate = new Date(
                controlEndDate.getFullYear(),
                controlEndDate.getMonth(),
                controlEndDate.getDate()
            );
        }

        if (joinedDate) {
            const maxDateDate = new Date(maxDate);
            const isJoinedDateAfterMaxDate = joinedDate > maxDateDate;

            return isJoinedDateAfterMaxDate ? {'maxDate': {value: control.value}} : null;
        }
        return null;
    };
}


export function minOneHourDurationValidator(): ValidatorFn {
    return (control: AbstractControl): { [key: string]: any } | null => {
        const endDateControlValue = control?.parent?.get('endDate')?.value;
        const endTimeControlValue = control?.value;
        if (endTimeControlValue && endDateControlValue) {
            const endDate = new Date(endDateControlValue);
            const endTime = new Date(endTimeControlValue);
            const nowDate = new Date();
            const endTimeHours = endTime.getHours();
            const endTimeMinutes = endTime.getMinutes();
            const nowDateHours = nowDate.getHours();
            const nowDateMinutes = nowDate.getMinutes();

            const endTimeMoment = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate(), endTimeHours, endTimeMinutes);
            const nowDatePlusOneHour = new Date(nowDate.getFullYear(), nowDate.getMonth(), nowDate.getDate(), nowDateHours + 1, nowDateMinutes);

            const isMinDurationOneHour = endTimeMoment < nowDatePlusOneHour;

            const isDateEqual = endDate.getFullYear() === nowDate.getFullYear() && endDate.getMonth() === nowDate.getMonth() && endDate.getDate() === nowDate.getDate();
            return isDateEqual && isMinDurationOneHour ? {'dateTodayAndMinDurationOneHour': {value: endTimeControlValue}} : null;
        } else {
            return null;
        }
    }
}

export function minOneHourExtendDurationValidator(oldRentalEndDate: Date, oldRentalEndTime: Date): ValidatorFn {
    return (control: AbstractControl): { [key: string]: any } | null => {
        const newExtendDate = control?.parent?.get('end_date')?.value;
        const newExtendTime = control?.value;

        if (newExtendTime && newExtendDate && oldRentalEndDate && oldRentalEndTime) {
            const newExtendEndDate = new Date(newExtendDate);
            const newExtendEndTime = new Date(newExtendTime);

            const newDateHours = newExtendEndTime.getHours();
            const newDateMinutes = newExtendEndTime.getMinutes();

            const oldDateHours = oldRentalEndTime.getHours();
            const oldDateMinutes = oldRentalEndTime.getMinutes();

            const newEndTimeMoment = new Date(newExtendEndDate.getFullYear(), newExtendEndDate.getMonth(), newExtendEndDate.getDate(), newDateHours, newDateMinutes);
            const oldEndDatePlusOneHour = new Date(oldRentalEndDate.getFullYear(), oldRentalEndDate.getMonth(), oldRentalEndDate.getDate(), oldDateHours + 1, oldDateMinutes);

            const isMinDurationOneHour = newEndTimeMoment < oldEndDatePlusOneHour;

            let isYearEqual = newExtendEndDate.getFullYear() === oldRentalEndDate.getFullYear();
            let isMonthEqual = newExtendEndDate.getMonth() === oldRentalEndDate.getMonth();
            let isDayNumberEqual = newExtendEndDate.getDate() === oldRentalEndDate.getDate();
            let isDateEqual = isYearEqual && isMonthEqual && isDayNumberEqual;

            return isDateEqual && isMinDurationOneHour ? {'minExtendOneHour': {value: newExtendTime}} : null;
        } else {
            return null;
        }
    }
}


export function timeFormatValidator(): ValidatorFn {
    return (control: AbstractControl): { [key: string]: boolean } | null => {
        const pattern = /^(0[1-9]|1[0-2]):([0-5][0-9]) (AM|PM)$/;
        const isValid = pattern.test(control.value);
        return isValid ? null : {'invalidTimeFormat': true};
    };
}


