import {
    isArrayBufferResizeSupported,
    isSharedArrayBufferGrowSupported,
    isWasmMemorySupported,
} from '../../../src/main';


test('Test isWasmMemorySupported', () => {
    expect(isWasmMemorySupported === true).toBe(true);
});

test('Test isArrayBufferResizeSupported', () => {
    expect(isArrayBufferResizeSupported === false || isArrayBufferResizeSupported === true).toBe(true);
});

test('Test isSharedArrayBufferGrowSupported', () => {
    expect(isSharedArrayBufferGrowSupported === false || isSharedArrayBufferGrowSupported === true).toBe(true);
});
