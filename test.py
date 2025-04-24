test = {
    "1": ("desain", "24-04-2025 08:00", "24-04-2025 17:00"),
    "2": ("dummy", "26-04-2025 08:00", "26-04-2025 17:00"),
    "3": ("acc desain", "25-04-2025 08:00", "25-04-2025 17:00")
}

# print(test.items())
test = sorted(test.items(), key=lambda x: x[1][1])
print(test)

converted = {keys: value for keys, value in test}
print(converted)
