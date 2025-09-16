export class BTError extends Error {}

export class BTAssertError extends BTError {
    override name = 'AssertError';
}
