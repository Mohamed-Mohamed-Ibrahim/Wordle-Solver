# region imports
from pathlib import Path
import math, json
import pandas as pd
from collections import Counter, deque
import numpy as np
import re
# endregion


# region Global Variables
N_ITERS = 6

pattern_matrix = None
mapping = None

data_dir = Path("data")
pattern_matrix_file = data_dir / "pattern_matrix.csv"
guess_file_path = data_dir / "dictionary_5_letter.json"
target_file_path = data_dir / "targets_5_letter.json"
pattern_codes_file_path = data_dir / "codes.json"
# endregion


# region conversion
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
    global mapping
    code = str(code)
    if mapping != None:
        return mapping[f"{code}"]
    elif pattern_codes_file_path.exists():
        with open(pattern_codes_file_path, "r") as file:
            mapping = json.load(file)
    else:
        mapping = {}
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
            mapping[c] = s
        with open(pattern_codes_file_path, "w") as file:
            json.dump(mapping, file)
    return mapping[f"{code}"]


# endregion


# region input validation
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


# endregion


# region pattern matrix
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


# endregion


# region VIP fns
def pattern_code(guess, target):
    res = ["r"] * 5
    cnt = Counter(target)

    for i, (g, t) in enumerate(zip(guess, target)):
        if g == t:
            res[i] = "g"
            cnt[g] -= 1

    for i, (g, t) in enumerate(zip(guess, target)):
        if res[i] != "g" and cnt[g] > 0:
            res[i] = "y"
            cnt[g] -= 1

    return "".join(res)


def get_best_guess(pattern_matrix, user_guess="", user_feedback="", targets=[]):
    best_guess = ""
    best_information_gain = 0
    best_guesses = set()

    if targets == []:
        targets = pattern_matrix.index.to_list()

    if user_guess != "" and user_feedback != "":
        targets = [
            target
            for target in targets
            if pattern_code(user_guess, target) == user_feedback
        ]

    # print(f"Remaining possible targets: {len(targets)}")

    if len(targets) == 1:
        return targets[0], 0.0, targets

    for guess in pattern_matrix.columns:
        patterns = []
        for target in targets:
            patterns.append(pattern_matrix.at[target, guess])

        codes = [pattern_str_to_code(pattern) for pattern in patterns]
        cnts = Counter(codes)

        information_gain = 0
        num_targets = len(targets)
        for cnt in cnts.values():
            prob = cnt / num_targets
            information_gain += prob * math.log2(prob)

        information_gain *= -1

        if information_gain > best_information_gain:
            best_guess = guess
            best_information_gain = information_gain
            best_guesses.clear()
            best_guesses.add(guess)
        elif abs(information_gain - best_information_gain) < 1e-9:
            best_guesses.add(guess)

    for guess in list(best_guesses):
        if guess in targets:
            best_guess = guess
            break

    return best_guess, best_information_gain, targets


# endregion


# region utils fns
def print_iter(h_w, h_y, best_word):
    print(f"prior entropy H(W)={h_w:.3f}")
    print(f"best-guess expected feedback entropy H(Y)={h_y:.3f}")
    print(f"expected posterior entropy H(W|Y)={h_w - h_y:.3f}")
    print(f"information gain I(W;Y)={h_y:.3f}")

    print(f"BEST={best_word}\n")
    print("=" * 100, "\n")


# endregion


# region main fn
def main():
    print("=" * 100, "\n")

    i = 0
    pattern_matrix = precompute_pattern_matrix()
    guesses = pattern_matrix.columns.to_list()
    targets = pattern_matrix.index.to_list()
    user_guess, user_feedback = "", ""
    h_w = math.log2(len(targets))

    while i < N_ITERS:
        best_guess, best_information_gain, targets = get_best_guess(
            pattern_matrix, user_guess, user_feedback, targets
        )

        if i != 0:
            gained_entropy = h_w - math.log2(len(targets))
            print(f"Entropy gained from guess: {gained_entropy}")

        print_iter(h_w, best_information_gain, best_guess)

        print("Guess Word: ", end="")
        user_guess = get_user_guess(set(guesses))

        print("Feedback (g for green, y for yellow, r for grey): ", end="")
        user_feedback = get_user_feedback()

        h_w = math.log2(len(targets))

        print()

        if user_feedback == "ggggg":
            print("Well Done")
            return

        if len(targets) == 0:
            print("No such a target in targets.json")
            break

        i += 1
    print("Game Over ... Better Luck next time ...")


# endregion

if __name__ == "__main__":
    main()
