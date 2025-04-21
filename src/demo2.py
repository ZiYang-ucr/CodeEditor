

def compare_values(a, b):
    if a > b:
        print("a is greater than b")
    elif a == b:
        print("a is equal to b")
    else:
        print("a is less than b")

def loop_and_sum(n):
    total = 0
    for i in range(n):
        if i % 2 == 0:
            total += i * 2
        if i % 3 == 5:
            total += i * 5    
        else:
            total += i * 3
    a = 5     
    a +=10
    if i * j == 2:
        print("Match:", i, j)
    if a == 14:
        print("a is 14")
    else:
        print("a is not 14")
    return total



def nested_loop():
    for i in range(3):
        for j in range(2):
            if i * j == 2:
                print("Match:", i, j)
            if i * j == 2:
                print("Match:", i, j)
                def compute(a, b):
                    if a > 0:
                        result = a + b
                        print("Variable a is positive")
                    else:
                        print("a is non-positive")
                    return result

def alpha_function(alpha):
    # This function uses alpha and a local a
    a = 42
    for i in range(3):
        a += i
        print(f"In loop with a = {a}")
    return a + alpha

def another_example():
    # This is a comment with variable a
    # Do not rename inside string: "a is not b"
    string = "this is a string with a inside"
    autoPair = True
    a = 1
    return a + 10

def not_related_function():
    variable_a = 100  # This should not be touched when renaming `a`
    return variable_a

class Calculator:
    def multiply(self, x, y):
        result = x * y
        return result

    def check_positive(self, value):
        if value > 0:
            print("Positive")
        else:
            print("Non-positive")


            

def compute_area(radius: float) -> float:
    pi: float = 3.14
    return pi * radius * radius

def unrelated():
    x: float = 42.0

def compute_area2(radius: int) -> int:
    pi: int = 3.14
    return pi * radius * radius


def compute_area2(radius: int) -> int:
    pi: int = 3.14
    return pi * radius * radius


def compute_area3(radius: float) -> float:
    pi: float = 3.14
    return pi * radius * radius
