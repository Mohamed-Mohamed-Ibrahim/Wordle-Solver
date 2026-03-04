from pathlib import Path
import math, json
import pandas as pd
from collections import Counter
import numpy as np

from feedback import pattern_str_to_code

N_ITERS = 6

h_w = math.log2(12970)
h_w = math.log2(3242)
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
        return pd.read_csv(pattern_matrix_file, index_col=0)

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


def get_best_guess(pattern_matrix, user_guess="", user_feedback=""):
    best_guess = ""
    best_information_gain = 0
    ref_targets = pattern_matrix.index.to_list()
    targets = set()
    if user_guess != "":
        for target in ref_targets:
            valid_target = True
            for i, (c, f) in enumerate(zip(user_guess, user_feedback)):
                if c != target[i] and f == "g":
                    valid_target = False
                if c not in target and f == "y":
                    valid_target = False
                if c in target and f == "r":
                    valid_target = False
            if valid_target:
                targets.add(target)

        targets = list(targets)
    else:
        targets = ref_targets
    print(targets)
    for guess in pattern_matrix.columns:
        patterns = []
        for target in targets:
            patterns.append(pattern_matrix.at[target, guess])
        codes = [pattern_str_to_code(pattern) for pattern in patterns]
        cnts = Counter(codes)
        distribution = []
        for code, cnt in cnts.items():
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

    print(f"BEST={best_word}\n")
    print("=" * 100, "\n")


def main():
    print("=" * 100, "\n")
    i = 0
    pattern_matrix = precompute_pattern_matrix()
    # guesses = pattern_matrix.columns.to_list()
    user_guess, user_feedback = "", ""

    while i < N_ITERS:
        best_guess, best_information_gain = get_best_guess(
            pattern_matrix, user_guess, user_feedback
        )
        print_iter(h_w, best_information_gain, best_guess)
        print("Guess Word: ", end="")
        user_guess = input()
        print("Feedback: ", end="")
        user_feedback = input()

        if user_feedback == "ggggg":
            break

        i += 1


if __name__ == "__main__":
    main()

    # print(get_best_guess(pattern_matrix))
    # print(pattern_code("ALLEY", "APPLE"))
