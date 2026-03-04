from pathlib import Path
import math, json
import pandas as pd
from collections import Counter

N_ITERS = 6

h_w = math.log2(12970)
data_dir = Path("data")

pattern_matrix_file = data_dir / "pattern_matrix.csv"
guess_file_path = data_dir / "dictionary_5_letter.json"
target_file_path = data_dir / "targets_5_letter.json"


def pattern_code(guess, target):
    res = []

    for g, t in zip(guess, target):
        if g == t:
            res.append("g")
        else:
            res.append("r")

    ct = Counter(target)

    for i, c in enumerate(guess):
        if ct[c] != 0 and res[i] != "g":
            res[i] = "y"
            ct[c] = 0

    return "".join(res)


def precompute_pattern_matrix():
    # if pattern_matrix_file.exists():
    # pattern_matrix = 12
    # return

    with open(guess_file_path, "r") as file:
        guesses = json.load(file)

    with open(target_file_path, "r") as file:
        targets = json.load(file)

    data = {}
    guesses = guesses[:5]
    targets = targets[:5]
    for guess in guesses:
        data[guess] = []
        for target in targets:
            data[guess].append(pattern_code(guess, target))

    df = pd.DataFrame(data, index=targets)
    df.index.name = "targets"

    df.to_csv(pattern_matrix_file)

    print(
        f"CSV file '{pattern_matrix_file}' created successfully with string indices and columns."
    )
    print("\nDataFrame structure:")
    print(df)


def get_best_guess():
    pass


def print_iter(h_w, h_y, best_word):
    print(f"prior entropy H(W)={h_w:.3f}")
    print(f"best-guess expected feedback entropy H(Y)={h_y:.3f}")
    print(f"expected posterior entropy H(W|Y)={h_w - h_y:.3f}")
    print(f"information gain I(W;Y)={h_y:.3f}")

    print(f"BEST={best_word}")


def main():
    i = 0

    while i < N_ITERS:
        get_best_guess()
        print("", end=" ")
        i += 1


if __name__ == "__main__":
    # main()
    # precompute_pattern_matrix()
    print(pattern_code("ALLEY", "APPLE"))
