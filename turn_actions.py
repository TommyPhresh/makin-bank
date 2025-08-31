import random, time

rolls = {"Player":
         {1: "Bills due. -$0.1M",
          2: "Payday! +$0.2M",
          3: "Bad news. Double all losses until next turn.",
          4: "Good news. No bad news for anyone.",
          5: "Can bet against the central fund.",
          6: "Can bet against the central fund."
          },
         "Table":
         {1: "Central fund running out! -$1.0M",
          2: "Central fund gets a boost. +$0.2M",
          3: "Economy is HOT! Triple losses for the central fund.",
          4: "Economy is NORMAL. It's joever.",
          5: "Roller's choice: Central fund -$0.2M OR bet against central fund",
          6: "Can bet against the central fund."
          }
         }

def check_net_worth(player):
    if player.net_worth < 0:
        player.is_bankrupt = True
    elif player.net_worth > 20:
        player.investigation = True

def clear_statuses(game, i):
    player = game.players[i % len(game.players)]
    player.got_bad_news = False
    player.has_stock = False
    player.has_bond = False

def choose_odds(max_bet, bad_news):
    min_choices = 1
    if bad_news:
        if max_bet < 20:
            min_choices = 1
        if max_bet < 16:
            min_choices = 2
        if max_bet < 12:
            min_choices = 3
        if max_bet < 8:
            min_choices = 4
        if max_bet < 4:
            min_choices = 5
    else:
        if max_bet < 10:
            min_choices = 1
        if max_bet < 8:
            min_choices = 2
        if max_bet < 6:
            min_choices = 3
        if max_bet < 4:
            min_choices = 4
        if max_bet < 2:
            min_choices = 5
    winners = input(f"Enter a comma-separated list of your chosen digits (0-9).\n\
    You can cover {min_choices} or more digits.\n \
    The less numbers you choose, the more you'll be betting.")
    if len(winners.split()) < min_choices:
        print(f"Try again. You can only cover {min_choices} or more digits.")
        return choose_odds(max_bet, bad_news)
    else:
        return [int(i) for i in winners.split(',')]
    
def bet_player(game, i, j):
    player = game.players[i % len(game.players)]
    target = game.players[j]
    winners = choose_odds(player.net_worth, player.got_bad_news)
    result = random.randint(0, 9)
    if result in winners:
        print(f"{player.name} won!")
        if player.has_stock:
            player.net_worth += 4*(6 - len(winners))
        else:
            player.net_worth += 2*(6 - len(winners))
        if target.has_bond:
            target.net_worth -= 1*(6 - len(winners))
        elif target.got_bad_news:
            target.net_worth -= 4*(6 - len(winners))
        else:
            target.net_worth -= 2*(6 - len(winners))
    else:
        print(F"{player.name} lost.")
        if player.has_bond:
            player.net_worth -= 1*(6 - len(winners))
        elif player.got_bad_news:
            player.net_worth -= 4*(6 - len(winners))
        else:
            player.net_worth -= 2*(6 - len(winners))
        if target.has_stock:
            target.net_worth += 2*(6 - len(winners))
        else:
            target.net_worth += 1*(6 - len(winners))
    check_net_worth(player)
    check_net_worth(target)
    print(player)
    print(target)

def bet_table(game, i):
    table = game.table
    player = game.players[i % len(game.players)]
    winners = choose_odds(player.net_worth, player.got_bad_news)
    result = random.randint(0, 9)
    if result in winners:
        print(f"{player.name} won!")
        if player.has_stock:
            player.net_worth += 4*(6 - len(winners))
        else:
            player.net_worth += 2*(6 - len(winners))
        if table.economy_hot:
            table.points -= 6*(6 - len(winners))
        else:
            table.points -= 2*(6 - len(winners))
    else:
        print(f"{player.name} lost.")
        if player.has_bond:
            player.net_worth -= 1*(6 - len(winners))
        elif player.got_bad_news:
            player.net_worth -= 4*(6 - len(winners))
        else:
            player.net_worth -= 2*(6 - len(winners))
        table.points += 2*(6 - len(winners))
    check_net_worth(player)
    print(player)
    print(table)

# basic routing for betting phase
def make_bets(game, i, table_open):
    player = game.players[i % len(game.players)]
    if table_open:
        target = input("Enter 'fund' to bet against the central fund\n \
        or a player's name to bet against another player.")
        if target.lower() == 'fund':
            bet_table(game, i)
        elif target.lower() == player.name.lower():
            print("Try again. You cannot bet against yourself.")
            target = input("Enter a player's name to bet against that player.")
        else:
            for j in range(len(game.players)):
                if game.players[i].name == target:
                    print(f"Betting against {game.players[j].name}")
                    bet_player(game, i, j)
                    
    # no option to bet against central fund
    else:
        target = input("Enter a player's name to bet against that player.")
        if target.lower() == player.name.lower():
            print("Try again. You cannot bet against yourself.")
            target = input("Enter a player's name to bet against that player.")
        else:
            for j in range(len(game.players)):
                if game.players[i].name.lower() == target.lower():
                    print(f"Betting against {game.players[j].name}")
                    bet_player(game, i, j)
                    

# basic turn structure
def take_turn(game, i):
    clear_statuses(game, i)
    player = game.players[i % len(game.players)]
    player.my_turn = True
    print("HEADLINES")
    headlines = check_ticker()
    if headlines == -1:
        print(player)
        print("TURN OVER")
        player.my_turn = False
    elif headlines == 1:
        player.has_stock = True
        print(player)
        print("TURN OVER")
        player.my_turn = False
    elif headlines == 2:
        player.has_bond = True
        print(player)
        print("TURN OVER")
        player.my_turn = False
    else:
        print("HEADLINES")
        table_open = read_headlines(game, i, headlines)
        time.sleep(1)
        make_bets(game, i, table_open)
        print("TURN OVER")
        player.my_turn = False

def read_headlines(game, i, headlines):
    (player_die, table_die) = headlines
    table = game.table
    player = game.players[i % len(game.players)]
    print(rolls['Player'][player_die])
    print(rolls['Table'][table_die])
    table_open = False
    match player_die:
        case 1:
            player.net_worth -= 1
        case 2:
            player.net_worth += 2
        case 3:
            player.got_bad_news = True
        case 4:
            for p in game.players:
                p.got_bad_news = False
        case _:
            table_open = True
    match table_die:
        case 1:
            table.points -= 10
        case 2:
            table.points += 2
        case 3:
            table.economy_hot = True
        case 4:
            table.economy_hot = False
        case 5:
            rollers_choice = int(input("Enter '1' to bet the central fund, \
            or '2' to auto-deduct $0.2M and bet normally."))
            if rollers_choice == 1:
                table_open = True
            else:
                table.points -= 2
        case 6:
            table_open = True
    print(game)
    return table_open
    

# roll dice
def check_ticker(from_doubles=False):
    player_die = random.randint(1, 6)
    table_die = random.randint(1, 6)
    if player_die == table_die and from_doubles:
        print("DOUBLES! You lost your turn")
        return -1
    elif player_die == table_die:
        print("DOUBLES!")
        print("Current headlines")
        print(rolls['Player'][player_die])
        print(f"AND {rolls['Table'][table_die]}")
        choice = int(input("Enter '1' if you want to accept current headlines, \
            '2' if you want to try again. If you get doubles again, you lose this turn.\
            '3' if you want to take an investment."))
        if choice == 2:
            return check_ticker(from_doubles=True)
        elif choice == 3:
            invest = int(input("Enter '1' if you want a stock (Double winnings until next turn)\
            , enter '2' if you want a bond (Half losses until next turn)"))
            return invest
    return (player_die, table_die)
        
        
