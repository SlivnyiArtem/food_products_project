def make_sequence(n):
    res = []
    c_num, counter = 1, 0
    while counter < n:
        amount = min(c_num, n - counter)
        res.append(str(c_num) * amount)
        counter += amount
        c_num += 1
    return "".join(res)


def main():
    n = int(input("Введите n\n"))
    print(make_sequence(n))


if __name__ == '__main__':
    main()
