import sys

if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        data = f.read()

    print(data.split("\n\n"))
