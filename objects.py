# Player in the game
class Player:
    def __init__(self, i, num_players):
        self.name = input(f'Player {i}, type your name: ')
        self.net_worth = 7 if num_players == 2 else 9
        self.has_stock = False
        self.has_bond = False
        self.investigation = False
        self.is_bankrupt = False
        self.got_bad_news = False
        self.my_turn = False

    def __str__(self):
        if self.is_bankrupt:
            return f"{self.name} is BANKRUPT."
        else:
            return f"""{self.name} 
            {'UNDER INVESTIGATION' if self.investigation else ''} 
            {'BAD NEWS' if self.got_bad_news else ''} 
            Net Worth: ${self.net_worth/10}M. 
            Portfolio: {self.get_portfolio()} \n"""

    def get_portfolio(self):
        return f"{'Stock' if self.has_stock else 'Bond' if self.has_bond else 'N/A'}"

# Central fund players interact with. When it runs out, game over.
class Table:
    def __init__(self, num_players):
        self.points = 40
        self.max_points = 60 if num_players == 2 else 80
        self.economy_hot = False

    # prints table details
    def __str__(self):
        return f"Central fund holds ${self.points/10}M currently. \
        \n ${self.max_points/10}M max fund. \
        \n Economy is {'hot' if self.economy_hot else 'normal'}.\n"
        

# List of entity objects
class GameState:
    def __init__(self, num_players):
        self.num_players = num_players
        self.table = Table(num_players)
        self.players = []
        for i in range(num_players):
            self.players.append(Player(i, num_players))

    # prints num_players, table, and each player
    def __str__(self):
        return f"""{self.num_players}-player game. 
        {print(self.table)}
        ({[print(player) for player in self.players]}"""   
