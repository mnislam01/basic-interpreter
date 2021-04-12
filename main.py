import basic
print("Ready")
while True:
    text = input(">> ")
    results, error = basic.run('<stdin>', text)

    if error:
        print(error.as_string())
    else:
        print(results)
