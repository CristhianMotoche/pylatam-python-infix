# Infix notation
#
# Haskell:
#
# div :: Int -> Int -> Int
#
# div 8 2 == 4
# 8 `div` 2 == 4



class Infix:
    def __init__(self, function):
        self.function = function

    def __ror__(self, other):
        return Infix(lambda x: self.function(other, x))

    def __or__(self, other):
        return self.function(other)


multiple_of = Infix(lambda x, y: x % y == 0)
where = Infix(lambda it, f: filter(f, it))

larger_than_five = range(1,20) |where| (lambda x: x > 5)

for item in larger_than_five:
    if item |multiple_of| 2:
        print(item, "is even")
    else:
        print(item, "is odd")
