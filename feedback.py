from collections import deque
from pathlib import Path
import json

data_dir = Path("data")



if __name__ == "__main__":
    # print(pattern_str_to_code("rrrrr"))
    print(pattern_code_to_str(0))
    # print(pattern_str_to_code("gggrg"))
    print(pattern_code_to_str(188))
    # print(pattern_str_to_code("grggg"))
    print(pattern_code_to_str(236))
