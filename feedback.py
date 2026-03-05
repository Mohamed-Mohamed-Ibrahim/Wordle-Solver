from collections import deque
from pathlib import Path
import json

data_dir = Path("data")
pattern_codes_file_path = data_dir / "codes.json"


def pattern_str_to_code(s: str) -> int:
    res = 0

    for i, c in enumerate(s):
        p = pow(3, i)
        if c == "g":
            res += p * 2
        elif c == "y":
            res += p

    return res


def pattern_code_to_str(code: int) -> str:
    code = str(code)
    if pattern_codes_file_path.exists():
        with open(pattern_codes_file_path, "r") as file:
            m = json.load(file)
    else:
        m = {}
        i = 0

        strs = deque()
        strs.append("")
        for i in range(5):
            for _ in range(len(strs)):
                s = strs.popleft()
                strs.append(s + "r")
                strs.append(s + "y")
                strs.append(s + "g")

        for s in strs:
            c = pattern_str_to_code(s)
            m[c] = s
        with open(pattern_codes_file_path, "w") as file:
            json.dump(m, file)
    return m[f"{code}"]


if __name__ == "__main__":
    # print(pattern_str_to_code("rrrrr"))
    print(pattern_code_to_str(0))
    # print(pattern_str_to_code("gggrg"))
    print(pattern_code_to_str(188))
    # print(pattern_str_to_code("grggg"))
    print(pattern_code_to_str(236))
