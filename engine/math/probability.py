import random


def weighted_choice(options):
    values = list(options.keys())
    probabilities = [options[key]["chance"] for key in values]
    return random.choices(values, weights=probabilities, k=1)[0]
