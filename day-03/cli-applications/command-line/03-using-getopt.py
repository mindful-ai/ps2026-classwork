import sys, getopt

opts, args = getopt.getopt(sys.argv[1:], "n:a:c:", ["name=", "age=", "city="])

for opt, val in opts:
    if opt in ("-n", "--name"):
        name = val
    elif opt in ("-a", "--age"):
        age = val
    elif opt in ("-c", "--city"):
        city = val

print(f"Name: {name}, Age: {age}, City: {city}")
