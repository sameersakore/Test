x = [1, 2, 3, 4, 5]
a = []

if 1 in x:
    print("1")
    a = [1]
    print("a", a)
    if 2 in x:
        print("2")
        a = [1, 2]
        print("a", a)
    if 3 in x:
        print("3")
else:
    a = [1, 2, 3, 4, 5]
    print("final", a)

print("hello")
