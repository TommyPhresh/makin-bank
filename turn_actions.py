"""
This file defines and initializes the Game class.
It also contains the core actions of the game, as the Game class handles most of that.
"""
from player import Player
from dice import *
import time

def get_wager_amount(numbers_chosen):
        """Helper fn mapping numbers chosen to amount wagered"""
        wager = {1: 10, 2: 8, 3: 6, 4: 4, 5: 2}
        return wager[numbers_chosen] 

class Game:
    def __init__(self, player_names):
        self.num_players = len(player_names)
        self.players = [Player(name, self.num_players) for name in player_names]
        self.central_fund = 40
        self.central_fund_cap = 60 if self.num_players == 2 else 80
        self.central_fund_status = 'NORMAL' # either NORMAL or HOT
        self.current_player_index = 0
        self.game_over = False
        self.free_turns_counter = 0

    def check_gameover(self):
        """Checks if central fund is 0 or over its cap """
        if self.central_fund <= 0:
            # central fund empty - a player has won
            # Players sorting criteria:
                # 1. Net worth
                # 2. Equity (Assets - liabilities)
                # 3. Bankruptcy status
            print("\nThe central fund has reached $0! Game over.")
            sorted_players = sorted(
                    self.players,
                    key=lambda p: (
                            -p.net_worth,
                            -(len(p.statuses.intersection({"STOCK", "BOND"})) - len(p.statuses.intersection({"BAD NEWS"}))),
                              p.is_bankrupt
                            )
                    )
            print("Final Results:")
            for i, player in enumerate(sorted_players):
                    print(f"    {i+1}. {player.name}: ${player.net_worth / 10}M")
            self.game_over = True
            return True
        elif self.central_fund >= self.central_fund_cap:
            # central fund over cap - all players lose
            # really emphasizes the fact that ALL players FAILED
            print("\nThe central fund has reached its cap! All players lose.")
            print(f"Final Central Fund value: ${self.central_fund / 10}M")
            print("Final Results:")
            for player in self.players:
                    print(f"    -. {player.name}: FAIL - BANKRUPT")
            self.game_over = True
            return True
        return False

    def display_game_state(self):
        """Prints current game state (all players and central fund)"""
        print("-" * 30)
        print(f"CENTRAL FUND: ${self.central_fund/10}M (cap is ${self.central_fund_cap/10}M)")
        print(f"Economy is {self.central_fund_status}")
        print("\nPLAYERS:")
        for player in self.players:
            statuses = ", ".join(player.statuses) if player.statuses else ""
            investigation = " (UNDER INVESTIGATION)" if player.under_investigation else ""
            bankrupt = " (BANKRUPT)" if player.is_bankrupt else ""
            print(f"    {player.name}:${player.net_worth/10}M | {statuses}{investigation}{bankrupt}")
        print("-" * 30)

    def handle_bankruptcy(self, player):
        """When a player's net worth < 1, they are BANKRUPT"""
        print(f"\n{player.name} has gone bankrupt!")
        player.statuses.clear()
        player.under_investigation = False
        player.is_bankrupt = True
        player.net_worth = 0

        if self.num_players == 2:
            print("Since this is a 2-player game, the other player gets 2 free turns to wear down the Central Fund.")
            self.free_turns_counter = 2
            self.current_player_index = (self.current_player_index + 1) % self.num_players

    def handle_bankruptcy_court(self, player):
        """Manages the d4 roll for the player to get back in the game"""
        print("-" * 30)
        print(f"{player.name} is going to bankruptcy court...")
        time.sleep(3)
        d4_roll = roll_d4()
        if self.num_players == 2:
            player.net_worth = d4_roll + 5
            print(f"Welcome back, {player.name}! You now have ${player.net_worth/10}M.")
            player.is_bankrupt = False
        else:
            if d4_roll % 2 == 0:
                player.net_worth += d4_roll
                print(f"{player.name} is back in with ${player.net_worth/10}M.")
                player.is_bankrupt = False
            else:
                player.net_worth += d4_roll
                print(f"{player.name} is still bankrupt. Try again next turn.")
                return 1

    def handle_d6_roll(self, player):
        """Manages the first phase of a player's turn: rolling the two d6s"""

        # Clear statuses
        player.statuses.discard("STOCK")
        player.statuses.discard("BOND")
        player.statuses.discard("BAD NEWS")

        player_die = roll_d6()
        fund_die = roll_d6()

        time.sleep(3)
        print("")
        print(f"{player.name} rolls Player {player_die}, Fund {fund_die}")
        if player_die == fund_die:
            print("\nDOUBLES! You have three options:")
            print("  1. Play the dice as rolled.")
            print("  2. Re-roll ONE time. If it's doubles again, your turn is FORFEIT.")
            print("  3. Invest in a Stock or Bond.")
            choice = input("Enter your choice (1, 2, or 3): ")

            # Player wants to re-roll
            if choice == '2':
                player_die = roll_d6()
                fund_die = roll_d6()
                print(f"Re-roll. Player {player_die}, Fund {fund_die}")
                if player_die == fund_die:
                    print("More doubles! Your turn ends without anything happening.")
                    return -2
            # Player wants to invest
            elif choice == '3':
                investment = input("Do you want a Stock or a Bond? Stocks double your winnings until your next turn, Bonds halve your losses until your next turn. Enter 'stock' or 'bond': ")
                if investment.lower() == 'stock':
                    print(f"{player.name} has invested in a Stock. Double winnings until next turn.")
                    player.statuses.add('STOCK')
                elif investment.lower() == 'bond':
                    print(f"{player.name} has invested in a Bond. Half losses until next turn.")
                    player.statuses.add("BOND")
                else:
                    print("Invalid choice. You missed your window. No investment made.")
                return -2
            elif choice != '1':
                print("Invalid choice. Your dice will be played as rolled.")

        # Player Die outcomes
        can_bet_fund = False
        match player_die:
            case 1:
                print("Bills Due! You lose $0.1M")
                player.net_worth -= 1
                print(f"{player.name} has ${player.net_worth/10}M.")
            case 2:
                print("Payday! You gain $0.2M")
                player.net_worth += 2
                print(f"{player.name} has ${player.net_worth/10}M.")
            case 3:
                print("Bad News. A dark cloud hangs over you. All bets carry DOUBLE losses until next turn.")
                player.statuses.add("BAD NEWS")
            case 4:
                print("Good News! The market is in your favor. All players' BAD NEWS are cleared.")
                for p in self.players:
                    p.statuses.discard("BAD NEWS")
            case _:
                print("A door has opened ... you are given the option to bet against the Central Fund.")
                can_bet_fund = True

        # Central Fund Die outcomes
        match fund_die:
            case 1:
                print("The market takes a nosedive! The Central Fund loses $1.0M")
                self.central_fund -= 10
            case 2:
                print("Inflation. The Central Fund gains $0.2M")
                self.central_fund += 2
            case 3:
                print("The economy is HOT! Central Fund's losses are TRIPLED.")
                self.central_fund_status = "HOT"
            case 4:
                print("The frenzy is over. Central Fund's losses are NORMAL.")
                self.central_fund_status = "NORMAL"
            case 5:
                print("Roller's Choice! Either deduct $0.2M from the Central Fund or bet against it.")
                choice = input("Deduct $0.2M from Central Fun? (y/n): ")
                if choice.lower() == "y":
                    self.central_fund -= 2
                    print(f"Central Fund now at ${self.central_fund/10}M.")
                else:
                    can_bet_fund = True
            case _:
                print("A door has opened ... you are given the option to bet against the Central Fund.")
                can_bet_fund = True
        return can_bet_fund
   

    def handle_betting(self, player, can_bet_fund):
        """Manages the second phase of a player's turn: betting"""
        print("-" * 30)
        # Status reminder
        if "BAD NEWS" in player.statuses:
            print(f"\n[!] A word to the wise: Due to BAD NEWS, your losses will be DOUBLED.")
        if "STOCK" in player.statuses:
            print(f"\n[!] Market update: Thanks to your Stock, winnings are DOUBLED!")
        if "BOND" in player.statuses:
            print(f"\n[!] Slow and steady wins the race: Thanks to your Bond, your losses are HALVED.")

        if can_bet_fund == "BANKRUPTCY":
            bet_type = 'fund'

        elif can_bet_fund:
            bet_type = input("Do you want to bet against the Central Fund or another player? (fund/player): ").lower()
            if bet_type not in ['fund', 'player']:
                print("Indecisive? The door is closed! Bet against a player")
                bet_type = 'player'
            elif bet_type == 'fund':
                print(f"{player.name} will bet against the Central Fund.")
        else:
            bet_type = 'player'

        if bet_type == 'player':
            opponent = None
            while not opponent:
                opponent_name = input("Type the name of the person you want to bet against. ")
                for p in self.players:
                    if p.name.lower() == opponent_name.lower() and p.name.lower() != player.name.lower() and not p.is_bankrupt:
                        opponent = p
                        break
                if not opponent:
                    print("Invalid opponent name. Please choose a different player.")

        # Player chooses wager
        while True:
            try:
                numbers_chosen = int(input("Choose how many numbers to bet. The less you pick, the more you wager. (1, 2, 3, 4, or 5): "))
                if not 1 <= numbers_chosen <= 5:
                    print("Invalid choice. Please pick a number from 1 to 5.")
                    continue
                wager_amount = get_wager_amount(numbers_chosen)

                # Check if they can afford it
                affordability_scalar = 2 if "BAD NEWS" in player.statuses else 1
                max_wager = wager_amount * affordability_scalar
                min_wager = 2 * affordability_scalar
                if player.net_worth < min_wager:
                    return -2
                if player.net_worth < max_wager:
                    print(f"{player.name}, you can't cover this wager. You can't wager ${max_wager/10}M with only ${player.net_worth/10}M.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a number 1 through 5.")

        # Player chooses winning set
        chosen_winners = set()
        print(f"You are betting ${wager_amount/10}M. Choose {numbers_chosen} numbers 0 through 9.")
        while len(chosen_winners) < numbers_chosen:
            try:
                num = int(input(f"Enter. This is #{len(chosen_winners) + 1} of {numbers_chosen} numbers."))
                if not 0 <= num <= 9:
                    print("Please choose a number between 0 and 9.")
                elif num in chosen_winners:
                    print("You've already chosen this number. Try again.")
                else:
                    chosen_winners.add(num)
            except ValueError:
                print("Invalid input. Please enter a number between 0 and 9.")


        # Conduct the bet (roll d10 and check who won)
        d10_roll = roll_d10()
        time.sleep(3)
        print("-" * 30)
        print(f"The customer has spoken! Result: {d10_roll}")
        bet_won = d10_roll in chosen_winners

        # Check if under investigation
        if player.under_investigation and bet_won:
            print(f"{player.name} is Under Investigation. They cannot win this bet, but they are cleared of wrongdoing.")
            player.under_investigation = False
            return

        # Apply gains/losses
        if bet_won:
            # Apply gains
            final_winnings = wager_amount
            if "STOCK" in player.statuses:
                final_winnings *= 2
                print(f"Great investment! {player.name}'s Stock DOUBLES their winnings!")

            print(f"{player.name} wins! You gain ${final_winnings/10}M.")
            player.net_worth += final_winnings
            self.check_antitrust(player)
            
            # Apply losses
            if bet_type == 'fund':
                loss_amount = wager_amount
                if self.central_fund_status == "HOT":
                    loss_amount *= 3
                    print("The HOT economy makes the Central Fund lose TRIPLE")
                self.central_fund -= loss_amount
                print(f"The Central Fund loses ${loss_amount/10}M.")
            elif bet_type == "player":
                # need to implement choosing player to bet against
                loss_amount = wager_amount
                if "BAD NEWS" in opponent.statuses:
                    loss_amount *= 2
                    print(f"BAD NEWS! {opponent.name}'s losses are DOUBLED.")
                elif "BOND" in opponent.statuses:
                    loss_amount /= 2
                    print(f"{opponent.name}'s Bond was a good call! Their losses are HALVED.")
                opponent.net_worth -= loss_amount
                print(f"{opponent.name} lost ${loss_amount/10}M.")
                if opponent.net_worth <= 0:
                    self.handle_bankruptcy(opponent)

        else:
            # Apply losses
            final_loss = wager_amount
            if "BAD NEWS" in player.statuses:
                final_loss *= 2
                print(f"BAD NEWS! {player.name}'s losses are DOUBLED.")
            if "BOND" in player.statuses:
                final_loss /= 2
                print(f"{player.name}'s Bond was a good call! Their losses are HALVED.")
            player.net_worth -= final_loss
            print(f"{player.name} lost ${final_loss/10}M.")

            # Apply gains
            if bet_type == "fund":
                self.central_fund += wager_amount
                print(f"The Central Fund gains ${wager_amount/10}M.")
            else:
                # need to implement choosing player to bet against
                winnings_amount = wager_amount / 2
                if opponent.under_investigation:
                    print(f"{opponent.name} is Under Investigation. They cannot win this bet, but they are cleared of wrongdoing.")
                    opponent.under_investigation = False
                elif "STOCK" in opponent.statuses:
                    winnings_amount *= 2
                    print(f"Great investment! {opponent.name}'s Stock DOUBLES their winnings!")
                opponent.net_worth += winnings_amount
                print(f"{opponent.name} won ${winnings_amount/10}M.")
                self.check_antitrust(opponent)
                       

    def check_antitrust(self, player):
        """Handles antitrust case (score over 20)"""
        print("-" * 30)
        if player.net_worth > 20:
            print(f"\n{player.name}'s net worth of ${player.net_worth/10}M has raised some eyebrows.")
            player.net_worth = 20
            fines = roll_d4()
            print(f"{player.name} must pay ${fines/10}M in fines.")
            player.net_worth -= fines
            print(f"{player.name}'s new net worth is ${player.net_worth/10}M")
            player.under_investigation = True
            print(f"{player.name} is now Under Investigation. They cannot win their next bet.")

    def play(self):
        """While loop controlling the game"""
        while not self.game_over:
            print("\n\n\n\n\n\n")
            current_player = self.players[self.current_player_index]
            current_player.statuses = set()
            time.sleep(3)            
            print(f"\nIt's {current_player.name}'s turn.")
            print("Rolling...")
            time.sleep(3)

            # 2-player free turns
            if self.num_players == 2 and self.free_turns_counter > 0:
                print(f"Your opponent is bankrupt. {current_player.name} gets 2 free turns to whittle down the Central Fund.")
                self.display_game_state()
                can_bet_fund = self.handle_d6_roll(current_player)
                self.display_game_state()
                # induced state check after rolling
                if current_player.net_worth < 1:
                    self.handle_bankruptcy(current_player)
                self.check_antitrust(current_player)
                # bet
                code = self.handle_betting(current_player, can_bet_fund="BANKRUPT")
                if code is not None:
                    print("You are too broke to bet. Turn over.")
                # induced states check after betting
                if current_player.net_worth < 1:
                    self.handle_bankruptcy(current_player)
                self.check_antitrust(current_player)

                if self.check_gameover():
                    break

                self.free_turns_counter -= 1
                if self.free_turns_counter <= 0:
                    print("Free turns complete. Game will resume normally.")
                    self.current_player_index = (self.current_player_index + 1) % self.num_players
                continue

            # bankrupt player's turn
            elif current_player.is_bankrupt:
                self.display_game_state()
                code = self.handle_bankruptcy_court(current_player)
                if code is not None:
                    self.current_player_index = (self.current_player_index + 1) % self.num_players
                    continue

            # normal turn
            else:
                current_player.statuses.clear()
                self.display_game_state()
                can_bet_fund = self.handle_d6_roll(current_player)
                self.display_game_state()
                # induced state check after rolling
                if current_player.net_worth < 1:
                    self.handle_bankruptcy(current_player)
                    self.current_player_index = (self.current_player_index + 1) % self.num_players
                    continue
                self.check_antitrust(current_player)

                code = self.handle_betting(current_player, can_bet_fund)
                if code is not None:
                    print("You are too broke to bet. Turn over.")

                # indeuced state check after betting
                if current_player.net_worth < 1:
                    self.handle_bankruptcy(current_player)
                    self.current_player_index = (self.current_player_index + 1) % self.num_players
                    continue
                
                if self.check_gameover():
                    break

            self.current_player_index = (self.current_player_index + 1) % self.num_players
            
            
            
