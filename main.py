"""
Entry point to game. Time to make some bank
"""
from game import Game

if __name__ == "__main__":
    player_names = []
    while len(player_names) < 2 or len(player_names) > 4:
        player_names_input = input("Enter player names, separated by commas (2-4 players): ")
        player_names = [name.strip() for name in player_names_input.split(",")]
        if len(player_names) < 2 or len(player_names) > 4:
            print("Invalid number of players. Please enter between 2 and 4 names.")

    game = Game(player_names)
    game.play()
