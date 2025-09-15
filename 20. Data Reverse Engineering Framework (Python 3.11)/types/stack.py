import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bfw.utils import *



class Stack:
    def __init__ (self, items=None):
        if isinstance(items, list):
            self._stack = list(items)
        else:
            self._stack = []

    def push (self, value):
        self._stack.append(value)

    def pop (self):
        if self.isEmpty():
            raise Exception('Stack is empty')

        return self._stack.pop()

    def get (self):
        if self.isEmpty():
            raise Exception('Stack is empty')

        return self._stack[-1]

    def isEmpty (self):
        return not self._stack

    def __len__ (self):
        return len(self._stack)



def _test_ ():
    s = Stack([ 2, 4, 8 ])

    print(toJson(s), len(s), s.pop(), s.get(), s.get(), s.get(), s.pop(), s.pop())

    assert len(s) == 0



__all__ = [
    'Stack'
]



if __name__ == '__main__':
    _test_()