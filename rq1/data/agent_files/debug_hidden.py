def check_hidden():
    with open('target_stabilizers_60.txt', 'rb') as f:
        content = f.read()
    print(content[:1000])

if __name__ == "__main__":
    check_hidden()
