import {DomSanitizer} from '@angular/platform-browser';
import {Injectable, Pipe, PipeTransform} from '@angular/core';

@Injectable()
@Pipe({
    name: 'safeStyle'
})
export class SafeStylePipe implements PipeTransform {
    constructor(private sanitizer: DomSanitizer) {

    }

    transform (value) {
        return this.sanitizer.bypassSecurityTrustStyle(value);
    }
}
