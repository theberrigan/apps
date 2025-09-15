const { TextDecoder, TextEncoder } = require('node:util');
const { TestEnvironment } = require('jest-environment-jsdom');


class CustomJSDOMEnvironment extends TestEnvironment {
    async setup() {
        await super.setup();

        this.global.TextDecoder = TextDecoder
        this.global.TextEncoder = TextEncoder
        this.global.Uint8Array = Uint8Array;
        this.global.ArrayBuffer = ArrayBuffer;
        this.global.SharedArrayBuffer = SharedArrayBuffer;
        this.global.fetch = fetch;

        /*
         this.customExportConditions = args.customExportConditions || ['']

         this.global.TextDecoder = TextDecoder
         this.global.TextEncoder = TextEncoder
         this.global.TextDecoderStream = TextDecoderStream
         this.global.TextEncoderStream = TextEncoderStream
         this.global.ReadableStream = ReadableStream

         this.global.Blob = Blob
         this.global.Headers = Headers
         this.global.FormData = FormData
         this.global.Request = Request
         this.global.Response = Response
         this.global.fetch = fetch
         this.global.structuredClone = structuredClone
         this.global.URL = URL
         this.global.URLSearchParams = URLSearchParams

         this.global.BroadcastChannel = BroadcastChannel
         this.global.TransformStream = TransformStream
         */
    }
}

module.exports = CustomJSDOMEnvironment;
