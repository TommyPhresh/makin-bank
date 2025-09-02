"""
This file contains all the utility functions to roll each type of dice.

"""
import random

def roll_d6():
    return random.randint(1, 6)

def roll_d10():
    return random.randint(0, 9)

def roll_d4():
    return random.randint(1, 4)
