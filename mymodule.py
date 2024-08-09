import random

def genBuyKey():
    ALPHABET = "abcdefghijklmnopqrstuvwxyz"
    NUMBERS = "012456789"
    SPELLS = NUMBERS + ALPHABET
    length = 16
    return "".join(random.choices(SPELLS, k=length))
