#
# What are we looking for?
#
# value
#   | fun1
#   | fun2(x, y)
#   | fun3

class Pipe:
    def __init__(self, fn):
        self.fn = fn

    # arg | pipe == pipe.__ror__(arg)
    def __ror__(self, arg):
        return self.fn(arg)

    def __call__(self, *args, **kwargs):
        return Pipe(lambda x: self.fn(x, *args, **kwargs))

value = [1,2,3]
iddy = Pipe(lambda x: x)
select = Pipe(lambda iterable, fn: map(fn, iterable))
where = Pipe(lambda iterable, fn: filter(fn, iterable))
to_list = Pipe(list)

print("*"*30)
print(
  value
  | iddy
  | select(lambda x: x + 2)
  | select(lambda x: x ** 5)
  | select(lambda x: x - 3)
  | where(lambda x: x % 2 == 0)
  | to_list
)
