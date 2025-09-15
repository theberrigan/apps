import { isFn, isNone } from '../common/type-checks';
import { SharedArrayBufferCtor } from '../common/types';


const G = globalThis;

export const isWasmMemorySupported : boolean = !isNone(G.WebAssembly) && isFn(WebAssembly.Memory);

export const isArrayBufferResizeSupported : boolean = Boolean(
    !isNone(G.ArrayBuffer) &&
    isFn(ArrayBuffer.prototype?.resize) &&
    'maxByteLength' in ArrayBuffer.prototype &&
    'resizable' in ArrayBuffer.prototype
);

export const isSharedArrayBufferGrowSupported : boolean = Boolean(
    !isNone(SharedArrayBufferCtor) &&
    isFn(SharedArrayBufferCtor.prototype?.grow) &&
    'maxByteLength' in SharedArrayBufferCtor.prototype &&
    'growable' in SharedArrayBufferCtor.prototype
);
