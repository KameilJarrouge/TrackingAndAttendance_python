def f(x=13, y=11):
    if (y <= 0):
        return 0
    else:
        if (y % 2 == 0):
            return f()
        else:
            return x + f(x+2, y-2)


print(f())
