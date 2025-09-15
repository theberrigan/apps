import { Injectable }         from '@angular/core';

@Injectable({
    providedIn: 'root'
})
export class ColorService {
    constructor () {}

    public isWhiteContrastingColor (color : string | number[]) : boolean {
        return (typeof(color) == 'string' ? this.hex2lum(color) : this.rgb2lum(color)) <= 130;
    }

    public getContrastingColor (color : string | number[]) : string {
        return this.isWhiteContrastingColor(color) ? '#fff' : '#000';
    }

    public hex2lum (hex : string) : number {
        return this.rgb2lum(this.hex2rgb(hex));
    }

    public rgb2lum (rgb : number[]) : number {
        return (0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]);
    }

    public rgb2hex (rgb : any) : string {
        return `00000${ (rgb[0] << 16 | rgb[1] << 8 | rgb[2]).toString(16) }`.slice(-6);
    }

    public hex2rgb (hex : string) : number[] {
        hex = hex.replace(/^(0x|#)/, '');
        hex.length == 3 && (hex += hex);
        const color : number = parseInt(`0x${ hex }`, 16);
        return [ color >> 16 & 0xff, color >> 8 & 0xff, color & 0xff ];
    }

    public rgb2hsv (rgb : number[]) : number[] {
        const
            r : number = rgb[0] / 255,
            g : number = rgb[1] / 255,
            b : number = rgb[2] / 255,
            min : number = Math.min(r, g, b),
            max : number = Math.max(r, g, b);

        if (min == max) {
            return [ 0, 0, min ];
        }

        const
            d : number = (r == min) ? (g - b) : ((b == min) ? (r - g) : (b - r)),
            h : number = (r == min) ? 3 : ((b == min) ? 1 : 5);

        return [
            60 * (h - d / (max - min)),
            (max - min) / max,
            max
        ];
    }

    public hex2hsv (hex : string) : number[] {
        return this.rgb2hsv(this.hex2rgb(hex));
    }
}
