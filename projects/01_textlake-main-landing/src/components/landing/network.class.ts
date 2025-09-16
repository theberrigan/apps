import {bindMethods} from '../../js/utils';

export class Network {
    constructor () {
        bindMethods(this);
    }

    public init () : void {

    }

    // readystatechange - это самое старое событие срабатывает при смене состояния и является альтернативой остальным
    // loadstart
    // progress
    // abort
    // error
    // load - срабатывает, когда ресурс успешно загружен
    // timeout
    // loadend - срабатывает в любом случае, самым последним: success/error/abort

    // abort: readystatechange loadstart readystatechange progress abort loadend
    // error:
    // timeout:
    public get (url : string, responseType : string = 'json') : Promise<any> {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.responseType = 'text';  // always load as text and then parse manually, coz IE doesn't support 'json'

            xhr.addEventListener('readystatechange', () => {  // use oldest hook instead load/error/...
                if (xhr.readyState !== 4) {
                    return;
                }

                if (xhr.status >= 200 && xhr.status <= 399) {
                    const response = xhr.response || xhr.responseText;

                    if (responseType === 'json') {
                        resolve(JSON.parse(response));
                        return;
                    }

                    resolve(response);
                    return;
                }

                reject(xhr.status + ' ' + xhr.statusText);
            });

            xhr.open('GET', url, true);
            xhr.send();
        });
    }
}