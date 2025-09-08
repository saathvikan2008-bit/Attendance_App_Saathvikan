while True:
    x = int(input("Outer"))
    if x == 1:
        while True:
            y = int(input("Inner"))
            if y == 1:
                print("Hello World")
            elif y == 2:
                break
    elif x == 2:
        break
print("Finit")