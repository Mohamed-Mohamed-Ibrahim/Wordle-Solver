def pattern_str_to_code(s: str) -> int:
    res = 0

    for i, c in enumerate(s):
        p = pow(3, i)
        if c == "g":
            res += p * 2
        elif c == "y":
            res += p

    return res


# def pattern_code_to_str(code: int) -> str:
#     res = []

#     for i in range():


if __name__ == "__main__":
    print(pattern_str_to_code("rrrrr"))
    # print(pattern_code_to_str(0))
    print(pattern_str_to_code("gggrg"))
    # print(pattern_code_to_str(188))
    print(pattern_str_to_code("grggg"))
    # print(pattern_code_to_str(236))
