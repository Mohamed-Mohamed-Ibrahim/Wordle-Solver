from pathlib import Path
import math, json
import pandas as pd
from collections import Counter
import numpy as np

from feedback import pattern_str_to_code

N_ITERS = 6

h_w = math.log2(12970)
pattern_matrix = None

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
    if pattern_matrix_file.exists():
        return pd.read_csv(pattern_matrix_file)

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

    print(df)

    return df


def get_best_guess(pattern_matrix):
    print(pattern_matrix)
    print()
    best_guess = ""
    best_information_gain = float()

    for guess in pattern_matrix.columns:
        patterns = pattern_matrix.loc[:, guess]
        codes = [pattern_str_to_code(pattern) for pattern in patterns]
        cnts = Counter(codes)

        distribution = []
        for cnt in cnts.values():
            distribution.append(cnt / len(codes))
        information_gain = 0
        for prob in distribution:
            information_gain += prob * math.log2(prob)
        information_gain *= -1
        if information_gain > best_information_gain:
            best_guess = guess
            best_information_gain = information_gain
    return best_guess, best_information_gain


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
    pattern_matrix = precompute_pattern_matrix()
    print(get_best_guess(pattern_matrix))
    # print(pattern_code("ALLEY", "APPLE"))
