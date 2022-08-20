# Parser combinators
#
# text -> Either error s

from typing import Any, NamedTuple


class ParseError(Exception):
    pass


class Result(NamedTuple):
    success: bool
    value: Any
    idx: int


class Parser:
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, text, index):
        return self.fn(text, index)

    def __or__(self, other):
        @Parser
        def _choice(text, idx):
            res = self(text, idx)
            if res.success:
                return res
            else:
                return other(text, idx)
        return _choice

    def parse(self, text):
        res = self.fn(text, 0)
        if res.success:
            return res
        else:
            raise ParseError(f"Unexpected value: {text}")



def string(s):
    @Parser
    def _string(text, index):
        if s == text[index:index + len(s)]:
            return Result(success=True, idx=index + len(s), value=s)
        return Result(success=False, idx=index, value=None)
    return _string


py = string("Python")
hs = string("Haskell")
lang = py | hs

print(lang.parse("Haskell"))
