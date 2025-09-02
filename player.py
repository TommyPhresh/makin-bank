"""
This file defines and initializes the player class
"""

class Player:
    """Name, net worth, statuses (effects), and court case flags """
    def __init__(self, name, num_players):
        self.name = name
        self.net_worth = 7 if num_players == 2 else 9
        self.statuses = set()
        self.is_bankrupt = False
        self.under_investigation = False 
