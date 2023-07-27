import random

async def fullname(shortform):
    shortform = shortform.lower()
    if shortform == "c":
        full_name = "Common"
    elif shortform == "uc":
        full_name = "Uncommon"
    elif shortform == "r":
        full_name = "Rare"
    elif shortform == "sr":
        full_name = "Super Rare"
    elif shortform == "ur":
        full_name = "Ultra Rare"

    return full_name


async def packrng(rng):
    factor = random.choices([2, 1, 0], [45, 30, 25], k=1)[0]

    if factor == 2:
        pass
    elif factor == 1:
        rng[0] *= 1.01
    elif factor == 0:
        rng[0] *= 0.99

    factor2 = random.choices([2, 1, 0], [45, 30, 25], k=1)[0]

    if factor2 == 2:
        pass
    elif factor2 == 1:
        rng[1] *= 1.05
    elif factor2 == 0:
        rng[1] *= 0.95

    factor3 = random.choices([1, 0], [75, 25], k=1)[0]

    if factor3 == 1:
        pass
    elif factor3 == 0:
        rng[2] *= 0.9
