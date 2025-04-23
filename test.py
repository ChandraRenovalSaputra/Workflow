def testing():
    try:
        a = "test"
        b = " lagi"
        return a + b
    except Exception:
        print("error")
    finally:
        print("finally")

print(testing())