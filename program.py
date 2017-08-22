import random


class ShoeMaker(object):
    faces_tuples = [('A', 11, 1), ('K', 10, 10), ('Q', 10, 10), ('J', 10, 10), ('T', 10, 10), ('9', 9, 9),
                    ('8', 8, 8), ('7', 7, 7), ('6', 6, 6), ('5', 5, 5), ('4', 4, 4), ('3', 3, 3), ('2', 2, 2)]
    suites = [("♠", 'spade'), ("♥", 'heart'), ("♦", 'diamond'), ("♣", 'club')]

    def __init__(self, cut_card_at):
        self.cut_card_at = cut_card_at

    def get_shoe(self, number_of_decks):
        decks = []
        for i in range(number_of_decks):
            cards = []
            for face_name, val, sec_val in self.faces_tuples:
                for symbol, suite_name in self.suites:
                    suite = Suite(name=suite_name, symbol=symbol)
                    face = Face(name=face_name, value=val, second_value=sec_val)
                    cards.append(Card(face=face, suite=suite))
            decks.append(Deck(cards=cards))
        return Shoe(decks=decks, cut_card_at=self.cut_card_at)


class Table(object):
    active_players = 0
    shoe_maker = None

    def __init__(self, table_rules, dealer):
        self.rules = table_rules
        self.dealer = dealer
        self.shoe_maker = ShoeMaker(self.rules.cut_card_at)
        self.shoe = self.shoe_maker.get_shoe(number_of_decks=self.rules.number_of_decks)
        self.seats = []
        for i in range(self.rules.max_players):
            self.seats.append(Seat(player=None))

    def play(self):
        while True:
            # Check if any players at table
            if self.active_players == 0:
                print('No active players at table!')
                break

            # Fill the shoe if the number of cards remaining are less than cut card marker
            if len(self.shoe) <= self.shoe.cut_card_at:
                self.shoe = self.shoe_maker.get_shoe(number_of_decks=self.rules.number_of_decks)

            self.place_your_bets(min_bet=self.rules.min_bet, max_bet=self.rules.max_bet)
            self.dealer.no_more_bets()
            self.dealer.deal(shoe=self.shoe, active_players=self.active_players)

    def place_your_bets(self, min_bet, max_bet):
        for seat in self.seats:
            if seat.player is not None:
                seat.set_bet(seat.player.place_bets(self.rules.min_bet, self.rules.max_bet))
            else:
                # Seat is empty
                pass

    def join(self, player):
        if player.bankroll < self.rules.min_bet:
            print('{name} was unable to join the table since bankroll is less than table minimum ${min_bet}'.format(
                name=player.name, min_bet=self.rules.min_bet))
            return
        for seat in self.seats:
            if seat.player is None:
                seat.player = player
                print('{name} joined table successfully with ${bankroll}'.format(name=player.name,
                                                                                 bankroll=player.bankroll))
                self.active_players += 1
                return
        print('{name} was unable to join the table since all seats are occupied.'.format(name=player.name))


class TableRules(object):
    def __init__(self, max_players, number_of_decks, dealer_hits_soft_17, dealer_peeks, min_bet, max_bet,
                 cut_card_percent=25.0):
        self.max_players = max_players
        self.number_of_decks = number_of_decks
        self.dealer_hits_soft_17 = dealer_hits_soft_17
        self.dealer_peeks = dealer_peeks
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.cut_card_at = int(((number_of_decks * 52.0) * cut_card_percent) / 100.0)


class Player(object):
    def __init__(self, name, bankroll):
        self.name = name
        self.bankroll = bankroll

    def place_bets(self, min_bet, max_bet):
        pass


class Human(Player):
    def __init__(self, name, bankroll):
        Player.__init__(self, name=name, bankroll=bankroll)

    def place_bets(self, min_bet, max_bet):
        bet = 0
        while True:
            try:
                bet = int(
                    input('Place your bet please.. (Min:{0}, Max:{1}) '.format(min_bet, max(self.bankroll, max_bet))))
                if bet < min_bet or bet > max(self.bankroll, max_bet):
                    raise Exception
                else:
                    break
            except:
                print('Invalid bet!')
        return bet


class Machine(Player):
    def __init__(self, name, bankroll):
        Player.__init__(self, name=name, bankroll=bankroll)

    def place_bets(self, min_bet, max_bet):
        return random.randint(min_bet, max(self.bankroll, max_bet))


class Deck(object):
    def __init__(self, cards):
        self.cards = cards

    def __len__(self):
        return sum([len(card) for card in self.cards])


class Card(object):
    def __init__(self, suite, face):
        self.suite = suite
        self.face = face

    def __len__(self):
        return 1


class Dealer(object):
    def __init__(self, name):
        self.name = name

    def no_more_bets(self):
        print('{name}: No more bets.'.format(name=self.name))

    def deal(self, shoe, active_players):
        print('{name}: Dealing cards...'.format(name=self.name))
        cards_to_draw = (active_players + 1) * 2
        for i in range(cards_to_draw):
            card_at_random = random.randint(0, len(shoe))
            # Card pop code here


class Shoe(object):
    number_of_decks = 0
    cut_card_at = 0

    def __init__(self, decks, cut_card_at):
        self.decks = decks
        self.number_of_decks = len(decks)
        self.cut_card_at = cut_card_at

    def __len__(self):
        return sum([len(deck) for deck in self.decks])


class Seat(object):
    bet = 0

    def __init__(self, player):
        self.player = player

    def set_bet(self, value):
        self.bet = value
        print('{name} bets ${bet}'.format(name=self.player.name, bet=self.bet))


class Suite(object):
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol


class Face(object):
    def __init__(self, name, value, second_value):
        self.name = name
        self.value = value
        self.second_value = second_value


rules = TableRules(max_players=2, number_of_decks=6, dealer_hits_soft_17=True, dealer_peeks=True, min_bet=10,
                   max_bet=100)
dealer = Dealer(name='Mike')
table = Table(table_rules=rules, dealer=dealer)
alice = Human(name='Alice', bankroll=10000)
micheal = Machine(name='Micheal', bankroll=5)
bob = Machine(name='Bob', bankroll=500)
eve = Machine(name='Eve', bankroll=100)
table.join(alice)
table.join(micheal)
table.join(bob)
table.join(eve)
table.play()
