# Parser combinators
#
# Things to notice:

# 1. A parser is a function: text -> Either error value
# 2. A parser combiator is a high order function that takes a parser as an input
#    and can return another parser as output.

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

    # 3. Notice how we define the __call__ magic method
    # so that Parser instances can be callable.
    def __call__(self, text, index):
        return self.fn(text, index)

    # parse_one | parse_two
    def __or__(self, other):
        # 4. Since Parser is a callable that takes a function as a constructor
        # argument, it can also be a decorator:
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

    # skip_parse_result >> select_parse_result
    def __rshift__(self, other):
        @Parser
        def _compose(text, idx):
            res = self(text, idx)
            if res.success:
                return other(text, idx + res.idx)
            else:
                return res

        return _compose

    # select_parse_result << skip_parse_result
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

# 5. A string parser:
#   Looks for a specific string
def string(s):
    @Parser
    def _string(text, index):
        if s == text[index : index + len(s)]:
            return Result(success=True, idx=index + len(s), value=s, expected=s)
        return Result(success=False, idx=index, value=None, expected=s)

    return _string

# 6. A parser that looks for a parser `p` which is separated by the text of some
# other parser `sep`:
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

# 7. I can define my parsers
py = string("Python")
hs = string("Haskell")
js = string("JS")

# 8. And compose them:
langs = py | hs | js

comma = string(",")
langs_by_comma = sepBy(langs, comma)

left_bracket = string("{")
right_bracket = string("}")

langs = left_bracket >> langs_by_comma << right_bracket

# 9. ^^ I need to learn how my EDSL for parser combinators work

print(langs.parse("{Python,Haskell,JS}"))
print(langs.parse("{Haskell}"))
print(langs.parse("{JS}"))

# Parse errors
# print(langs.parse("[Python]"))
# print(langs.parse("{Python]"))
# print(langs.parse("{HTML}"))
# print(langs.parse("{JS,}"))
# print(langs.parse("{JS,CSS}"))
