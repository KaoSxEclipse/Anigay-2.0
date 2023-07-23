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
