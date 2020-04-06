"""
This file is the entry point for the blackjack game
"""

## system-packages imports
import random
import time
from itertools import count

import customExceptions as Ex


class Card:
    def __init__(self, unique_id, kind, name, value):
        self.unique_id = unique_id
        self.kind = kind
        self.name = name
        self.value = value

    def __str__(self):        # Magic methods
        return '{}'.format(self.name)


class Player:
    def __init__(self, name):
        self.name = name
        self.balance = 0
        self.victories = 0
        self.hand = []
        self.aces = 0
        self.sum = 0
        self.current_bet = 0
        # self.in_game = False
        print('{} has entered the room'.format(self.name))

    def buy_chips(self, quantity):
        self.balance += quantity
        print('{} current balance is ${}.'.format(self.name, self.balance))

    def bet(self, quantity):
        if quantity > self.balance:
            raise Ex.NotEnoughBalance
        else:
            self.current_bet += quantity
            self.balance -= self.current_bet


def aces_check(player, card):
    if card.kind == 'Ace':
        player.aces += 1
        if player.aces == 2:  # Over 21. A+A = 22
            player.aces -= 1
            player.sum -= 10


class Dealer:
    def __init__(self, stop):
        self.stop = stop
        self.tip = 0
        self.hand = []
        self.sum = 0
        self.aces = 0

    @staticmethod
    def give_card(deck, player):
        card = deck.pop(0)
        if card.kind == 'Ace':
            player.aces += 1
        player.hand.append(card)
        player.sum += card.value
        while player.sum > 21:
            if player.aces > 0:
                player.aces -= 1
                player.sum -= 10
            else:       # lose case
                return False
        return True     # Otherwise, return ok

    @staticmethod
    def collect_bet(player):
        player.current_bet = 0

    @staticmethod
    def pay_bet(player):
        print('{}: won'.format(player.name))
        player.balance += player.current_bet*2
        player.current_bet = 0
        player.victories += 1

    def deal(self, deck, players):
        for _ in range(2):
            for player in players:
                card = deck.pop(0)
                aces_check(player, card)
                player.hand.append(card)
                player.sum += card.value
                if player.sum == 21:
                    print('Blackjack for {}!'.format(player.name))
                    self.pay_bet(player)
                    print_hand(player)
                    players.remove(player)      # bye winning player
            card = deck.pop(0)
            aces_check(self, card)
            self.hand.append(card)
            self.sum += card.value

    def get_card(self, deck):
        card = deck.pop(0)
        self.hand.append(card)
        self.sum += card.value
        if card.kind == 'Ace':
            self.aces += 1
        while self.sum > 21:
            if self.aces > 0:
                self.aces -= 1
                self.sum -= 10
            else:       # lose case
                return False
        return True     # Otherwise, return ok


def generate_deck(number_of_decks):
    deck = []
    figures = ['Hearts', 'Spades', 'Diamonds', 'Clubs']
    faces = ['Jack', 'Queen', 'King']
    uid = 0
    for i in range(number_of_decks):
        for figure in figures:    # Generating for each suit
            # Generate Ace
            c = Card(uid, 'Ace', 'Ace of {}'.format(figure), 11)
            deck.append(c)
            uid += 1

            # Generate Numbers
            for num in range(2, 11, 1):
                c = Card(uid, 'Number', '{} of {}'.format(str(num), figure), num)
                uid += 1
                deck.append(c)

            # Generate Persons
            for face in faces:
                c = Card(uid, 'Face', '{} of {}'.format(face, figure), 10)
                deck.append(c)
                uid += 1

    return deck


def print_hand(player):
    print("{} hand:".format(player.name))
    [print(card) for card in player.hand]
    print('Sum is {}'.format(player.sum))

class Game:
    _ids = count(0)

    def __init__(self, dealer, number_of_decks, min_bet):
        self.id = next(self._ids)
        self.players = []
        self.dealer = dealer
        self.deck = generate_deck(number_of_decks)
        self.min_bet = min_bet
        self.dealer.hand = []
        self.dealer.aces = 0
        self.dealer.sum = 0

    def validate_bet(self, player):
        in_bet = 0
        while True:
            try:
                in_bet = (input('{}, what is your bet? '.format(player.name)))
                in_bet = int(in_bet)
                if in_bet < 1:
                    raise ValueError
                elif in_bet < self.min_bet:
                    raise Ex.BelowMinBet
                player.bet(in_bet)
                break
            except ValueError:
                print('Your input "{}" is invalid, try again'.format(in_bet))
                continue
            except Ex.NotEnoughBalance:
                print("You don't have enough money. Current Balance: {}. Try again".format(player.balance))
                continue
            except Ex.BelowMinBet:
                print("Your bet is lower than the table's minimum bet. Min bet: {}. Try again".format(self.min_bet))
                continue

    def add_player(self, player):
        if player.balance >= self.min_bet:
            print('{} current balance is ${}.'.format(player.name, player.balance))
            # player.in_game = True
            player.sum = 0
            player.aces = 0
            player.hand = []
            self.players.append(player)
        else:
            print('{} does not have enough funds to play, buy more'.format(player.name))

    def shuffle_carts(self):
        random.shuffle(self.deck)

    def print_deck(self):
        for card in self.deck:
            print(card)

    def show_hands(self, open_dealer):
        for player in self.players:
            print_hand(player)
            if player.sum > 21:
                print('{} losses'.format(player.name))
            print('____________')

        print("Dealer hand:")
        if not open_dealer:
            print("Covered Cart")
            [print(card) for card in self.dealer.hand[1:]]       # Not showing first
        else:
            [print(card) for card in self.dealer.hand]

    def start_game(self):
        self.shuffle_carts()
        for player in self.players:
            self.validate_bet(player)
        self.dealer.deal(self.deck, self.players)
        self.show_hands(open_dealer=False)

        for player in self.players:
            while True:
                action = input("\n\r{}, hit or stop? type: 'h' or 's'".format(player.name))
                if (action != 'h') and (action != 's'):
                    print('Invalid input, try again')
                elif action == 'h':
                    ok = Dealer.give_card(self.deck, player)
                    print('\n\r')
                    self.show_hands(open_dealer=False)
                    if not ok:    # lose
                        Dealer.collect_bet(player)
                        self.players.remove(player)       # bye losing player
                        break     # next player
                elif action == 's':
                    break         # next player

        ok = True

        if len(self.players):
            self.show_hands(open_dealer=True)
            while self.dealer.sum < self.dealer.stop and ok:
                ok = self.dealer.get_card(self.deck)
                print('\n\r')
                self.show_hands(open_dealer=True)
                time.sleep(2)

            if not ok:
                for player in self.players:
                    Dealer.pay_bet(player)
            else:
                for player in self.players:
                    if player.sum == self.dealer.sum:       # bet
                        player.balance += player.current_bet
                        player.current_bet = 0
                        print('{}: Push'.format(player.name))
                    elif player.sum > self.dealer.sum:      # player won
                        player.balance += player.current_bet*2
                        player.current_bet = 0
                        print('{}: won'.format(player.name))
                    else:                                   # lost
                        Dealer.collect_bet(player)
                        print('{}: lost'.format(player.name))
        print("Game over")

    def __str__(self):
        return 'Game ID: {}\n\rPlayers: {}'.format(self.id, len(self.players))


if __name__ == '__main__':
    NUMBER_OF_DECKS = 2

    dealer_1 = Dealer(stop=17)
    user_1 = Player('Miguel')

    while True:
        game_1 = Game(dealer=dealer_1, number_of_decks=NUMBER_OF_DECKS, min_bet=2)
        if user_1.balance < 10:
            if input("{}, your balance is {}, want to buy chips? y/n".format(user_1.name, user_1.balance)) == 'y':
                user_1.buy_chips(100)

        game_1.add_player(user_1)

        if len(game_1.players) > 0:
            print(game_1)
            game_1.start_game()
        else:
            print("Not enough players for the game!")
        if input("Play again? y/n") == 'n':
            break
