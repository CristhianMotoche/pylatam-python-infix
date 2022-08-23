# Infix notation
#
# Haskell:
#
# div :: Int -> Int -> Int
#
# div 8 2 == 4
# 8 `div` 2 == 4



class Infix(object):
    def __init__(self, function):
        self.function = function

    def __ror__(self, other):
        return Infix(lambda x: self.function(other, x))

    def __or__(self, other):
        return self.function(other)


prod = Infix(lambda x, y: x * y)
where = Infix(lambda it, f: filter(f, it))

larger_than_five = range(1,20) |where| (lambda x: x > 5)

for item in larger_than_five:
    print(item |prod| 3)
