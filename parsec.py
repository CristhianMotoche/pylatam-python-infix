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
    expected: str


class Parser:
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, text, index):
        return self.fn(text, index)

    # parse_one | parse_two
    def __or__(self, other):
        @Parser
        def _choice(text, idx):
            res = self(text, idx)
            if res.success:
                return res
            else:
                res_other = other(text, idx)
                if res_other.success:
                    return res_other
                else:
                    return Result(
                        success=False,
                        idx=res_other.idx,
                        value=None,
                        expected=f"{res.expected} or {res_other.expected}",
                    )

        return _choice

    # skip_parse >> selected_parse
    def __rshift__(self, other):
        @Parser
        def _compose(text, idx):
            res = self(text, idx)
            if res.success:
                return other(text, idx + res.idx)
            else:
                return res

        return _compose

    # selected_parse << skip_parse
    def __lshift__(self, other):
        @Parser
        def _skip(text, idx):
            res = self(text, idx)
            if not res.success:
                return res

            res_other = other(text, idx + res.idx)

            if res_other.success:
                return Result(
                    success=True,
                    idx=res_other.idx,
                    value=res.value,
                    expected=res.expected,
                )
            return Result(
                success=False,
                idx=res_other.idx,
                value=None,
                expected=res_other.expected,
            )

        return _skip

    def parse(self, text):
        res = self.fn(text, 0)
        if res.success:
            return res
        else:
            raise ParseError(
                f"Unexpected value: '{text}'. "
                f"Expected: '{res.expected}' "
                f"at: {res.idx}"
            )


# Things to notice:
def string(s):

    # 1. Parser can be used as a decorator:
    @Parser
    def _string(text, index):
        if s == text[index : index + len(s)]:
            return Result(success=True, idx=index + len(s), value=s, expected=s)
        return Result(success=False, idx=index, value=None, expected=s)

    return _string

def sepBy(p, sep):
    @Parser
    def _sepBy(text, idx):
        acc = []
        idx_acc = idx
        res = Result(success=True, idx=idx_acc, value=acc, expected=None)

        while res.success:
            res = p(text, idx_acc)
            if not res.success:
                return res

            acc.append(res.value)
            idx_acc = res.idx

            res_sep = sep(text, idx_acc)

            if res_sep.success:
                idx_acc = res_sep.idx
            else:
                return Result(success=True, idx=idx_acc, value=acc, expected=res.expected)

    return _sepBy

# 2. I can define my parsers and compose them
py = string("Python")
hs = string("Haskell")
js = string("JS")
langs = py | hs | js

comma = string(",")
langs_by_comma = sepBy(langs, comma)

left_bracket = string("{")
right_bracket = string("}")

langs = left_bracket >> langs_by_comma << right_bracket

# 3. ^^ I need to learn how my EDSL for parser combinators work

print(langs.parse("{Python,Haskell,JS}"))
print(langs.parse("{Haskell}"))
print(langs.parse("{JS}"))

# Parse errors
# print(langs.parse("[JS]"))
# print(langs.parse("{JS]"))
# print(langs.parse("{HTML}"))
# print(langs.parse("{JS,}"))
# print(langs.parse("{JS,CSS}"))
