from pathlib import Path
import math, json
import pandas as pd
from collections import Counter
import numpy as np
import re

from feedback import pattern_str_to_code

N_ITERS = 6

pattern_matrix = None

data_dir = Path("data")
pattern_matrix_file = data_dir / "pattern_matrix.csv"
guess_file_path = data_dir / "dictionary_5_letter.json"
target_file_path = data_dir / "targets_5_letter.json"


def get_user_guess(guesses):
    valid_guess_regex = r"^[a-z]{5}$"

    user_guess = input().strip()

    while user_guess not in guesses or not re.match(valid_guess_regex, user_guess):
        print(
            "Please. Ensure that the input is following the right requirements\n"
            + "1. length of 5\n"
            + "2. the word is in the dictionary\n"
            + "3. only lower case english characters is supported\n"
        )
        print("Guess Word: ", end="")
        user_guess = input().strip()

    return user_guess


def get_user_feedback():
    valid_feedback_regex = r"^(r|g|y){5}$"

    user_feedback = input().strip()

    while not re.match(valid_feedback_regex, user_feedback):
        print(
            "Please. Ensure that the input is following the right requirements\n"
            + "1. length of 5\n"
            + "2. g or y or r are the only supported characters\n"
        )
        print("Feedback (g for green, y for yellow, r for grey): ", end="")
        user_feedback = input().strip()

    return user_feedback


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
    # guesses = guesses[:10]
    # targets = targets[:10]
    for guess in guesses:
        data[guess] = []
        for target in targets:
            data[guess].append(pattern_code(guess, target))

    df = pd.DataFrame(data, index=targets)
    df.index.name = "targets"

    df.to_csv(pattern_matrix_file)
    # print(df)

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
    print(f"Targets length: {len(targets)}")
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
    return best_guess, best_information_gain, targets


def print_iter(h_w, h_y, best_word):
    print(f"prior entropy H(W)={h_w:.3f}")
    print(f"best-guess expected feedback entropy H(Y)={h_y:.3f}")
    print(f"expected posterior entropy H(W|Y)={h_w - h_y:.3f}")
    print(f"information gain I(W;Y)={h_y:.3f}")

    print(f"BEST={best_word}\n")
    print("=" * 100, "\n")


def get_entropy(pattern_matrix, guess, feedback, targets):
    patterns = []
    for target in targets:
        patterns.append(pattern_matrix.at[target, guess])
    codes = [pattern_str_to_code(pattern) for pattern in patterns]
    cnts = Counter(codes)
    print(cnts[feedback])
    prob = cnts[feedback] / len(codes)
    entropy = -1 * prob * math.log2(prob) if prob != 0 else 0
    print(entropy)
    return entropy


def main():
    print("=" * 100, "\n")

    i = 0
    h_w = math.log2(3242)
    pattern_matrix = precompute_pattern_matrix()
    guesses = pattern_matrix.columns.to_list()
    user_guess, user_feedback = "", ""

    while i < N_ITERS:
        best_guess, best_information_gain, targets = get_best_guess(
            pattern_matrix, user_guess, user_feedback
        )
        print_iter(h_w, best_information_gain, best_guess)

        print("Guess Word: ", end="")
        # user_guess = get_user_guess(set(guesses))
        user_guess = best_guess

        print("Feedback (g for green, y for yellow, r for grey): ", end="")
        user_feedback = get_user_feedback()

        gained_entropy = get_entropy(pattern_matrix, user_guess, user_feedback, targets)
        print(f"Entropy gained from guess: {gained_entropy}")
        h_w -= gained_entropy

        print()

        if user_feedback == "ggggg":
            print("Well Done")
            return

        i += 1
    print("Game Over ... Better Luck next time ...")


if __name__ == "__main__":
    main()

    # print(get_best_guess(pattern_matrix))
    # print(pattern_code("ALLEY", "APPLE"))
