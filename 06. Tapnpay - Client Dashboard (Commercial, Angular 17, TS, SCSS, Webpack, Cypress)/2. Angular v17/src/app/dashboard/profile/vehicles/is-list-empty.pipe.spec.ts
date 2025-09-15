import { IsListEmptyPipe } from './is-list-empty.pipe';

describe('IsListEmptyPipe', () => {
  it('create an instance', () => {
    const pipe = new IsListEmptyPipe();
    expect(pipe).toBeTruthy();
  });
});
