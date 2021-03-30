import basic

while True:
    text = input("In: ")
    results, error = basic.run('<stdin>', text)

    if error:
        print(error.as_string())
    else:
        print(results)
