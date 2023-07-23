packs = {
    "rare": (80, 19.5, 0.5, 50000),
    "epic": (65, 33, 2, 70000),
    "legendary": (50, 47, 3, 120000)
}

packtypes = list(packs.keys())

for i in range(len(packtypes)):
    print(list(packs[packtypes[i]]))