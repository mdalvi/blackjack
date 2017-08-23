import random


class Table(object):
    def __init__(self, table_rules, dealer):
        self.active_players = 0
        self.rules = table_rules
        self.dealer = dealer
        self.dealer.hits_soft_17 = self.rules.dealer_hits_soft_17
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
            self.dealer.deal(shoe=self.shoe, seats=self.seats)

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


class Dealer(object):
    def __init__(self, name):
        self.name = name
        self.cards = []
        self.actions = {'H': 'Hit!', 'S': 'Stand', 'DD': 'DoubleDown', 'SP': 'Split!'}
        self.hits_soft_17 = False

    def no_more_bets(self):
        print('{name}: No more bets.'.format(name=self.name))

    def deal(self, shoe, seats):
        print('{name}: Dealing cards...'.format(name=self.name))

        # First deal
        for seat in seats:
            if seat.player is not None:
                seat.set_cards(card1=shoe.get_card_at_random(), card2=shoe.get_card_at_random())
        # Dealer self-deals
        self.self_deal(card1=shoe.get_card_at_random(), card2=shoe.get_card_at_random())

        # Dealer serving every seat
        for seat in seats:
            if seat.player is not None:
                while True:
                    action = seat.player.decide(seat.bet)
                    print(
                        '{dealer}: {name} '.format(dealer=self.name, name=seat.player.name) + self.actions[action])
                    if action == 'S':
                        break
                    elif action == 'H':
                        seat.set_cards(card1=shoe.get_card_at_random())
                        hand_values = seat.get_hand_values()
                        if hand_values[0] > 21 and hand_values[1] > 21:
                            seat.discard_hand()
                            print('{dealer}: {name} busted!'.format(dealer=self.name, name=seat.player.name))
                            break
                    elif action == 'DD':
                        seat.set_bet(seat.bet)
                        seat.set_cards(card1=shoe.get_card_at_random())
                        hand_values = seat.get_hand_values()
                        if hand_values[0] > 21 and hand_values[1] > 21:
                            seat.discard_hand()
                            print('{dealer}: {name} busted!'.format(dealer=self.name, name=seat.player.name))
                            break
                    elif action == 'SP':
                        pass

        # Dealer plays
        is_dealer_busted = False
        print('Dealer has ' + self.get_hand_as_string(True))
        # Playing hard hand first
        while True:
            hand_values = self.get_hand_values()
            if hand_values[0] < 17:
                self.self_deal(card1=shoe.get_card_at_random(), card2=None, true_hand=True)
            elif hand_values[0] >= 17 and hand_values[0] <= 21:
                break
            elif hand_values[0] > 21:
                is_dealer_busted = True
                print('Dealer busted!')
                break
            print('Dealer has ' + self.get_hand_as_string(True))
        hand_values = self.get_hand_values()
        if hand_values[1] <= 17 and self.hits_soft_17:
            # Playing soft hand second
            while True:
                hand_values = self.get_hand_values()
                if hand_values[1] <= 17 and self.hits_soft_17:
                    self.self_deal(card1=shoe.get_card_at_random(), card2=None, true_hand=True)
                elif hand_values[1] >= 17 and hand_values[1] <= 21:
                    break
                elif hand_values[1] > 21:
                    is_dealer_busted = True
                    print('Dealer busted!')
                    break
                print('Dealer has ' + self.get_hand_as_string(True))
        # Reward distribution (if any)
        self.deal_rewards(seats=seats, is_dealer_busted=is_dealer_busted)

    def deal_rewards(self, seats, is_dealer_busted):
        for seat in seats:
            if is_dealer_busted:
                if seat.player is not None and seat.status == 'default':
                    seat.set_reward(seat.bet * 2)
            else:
                pass

    def self_deal(self, card1, card2=None, true_hand=False):
        if card2 is not None:
            self.cards.append(card1)
            self.cards.append(card2)
            print('Dealer is dealt Xx{c2_name}{c2_sym}'.format(c2_name=card2.face.name, c2_sym=card2.suite.symbol))
        else:
            self.cards.append(card1)
            print('Dealer is dealt {c1_name}{c1_sym}'.format(c1_name=card1.face.name, c1_sym=card1.suite.symbol))
        print('Dealer has ' + self.get_hand_as_string(true_hand))

    def get_hand_as_string(self, true_hand):
        hand_string = ''
        hand_first_value = 0
        hand_second_value = 0
        for card in self.cards:
            if not true_hand:
                hand_string += 'Xx|'
                true_hand = True
                continue
            hand_string += '{0}{1}|'.format(card.face.name, card.suite.symbol)
            hand_first_value += card.get_first_value()
            hand_second_value += card.get_second_value()
        hand_string += '{0}/{1}'.format(hand_first_value, hand_second_value)
        return hand_string

    def get_hand_values(self):
        hand_first_value = 0
        hand_second_value = 0
        for card in self.cards:
            hand_first_value += card.get_first_value()
            hand_second_value += card.get_second_value()
        return hand_first_value, hand_second_value


class Seat(object):
    def __init__(self, player):
        self.cards = []
        self.bet = 0
        self.player = player
        self.status = 'default'
        self.reward = 0

    def set_reward(self, value):
        self.reward = value
        self.player.bankroll += self.reward
        print('{name} is rewarded with ${reward}'.format(name=self.player.name, reward=self.reward))

    def set_bet(self, value):
        self.bet = value
        print('{name} bets ${bet}'.format(name=self.player.name, bet=self.bet))

    def set_cards(self, card1, card2=None):
        if card2 is not None:
            self.cards.append(card1)
            self.cards.append(card2)
            print('{name} is dealt {c1_name}{c1_sym}{c2_name}{c2_sym}'.format(name=self.player.name,
                                                                              c1_name=card1.face.name,
                                                                              c1_sym=card1.suite.symbol,
                                                                              c2_name=card2.face.name,
                                                                              c2_sym=card2.suite.symbol))
        else:
            self.cards.append(card1)
            print('{name} is dealt {c1_name}{c1_sym}'.format(name=self.player.name,
                                                             c1_name=card1.face.name,
                                                             c1_sym=card1.suite.symbol))
        print('{name} has '.format(name=self.player.name) + self.get_hand_as_string())

    def get_hand_as_string(self):
        hand_string = ''
        hand_first_value = 0
        hand_second_value = 0
        for card in self.cards:
            hand_string += '{0}{1}|'.format(card.face.name, card.suite.symbol)
            hand_first_value += card.get_first_value()
            hand_second_value += card.get_second_value()
        hand_string += '{0}/{1}'.format(hand_first_value, hand_second_value)
        return hand_string

    def get_hand_values(self):
        hand_first_value = 0
        hand_second_value = 0
        for card in self.cards:
            hand_first_value += card.get_first_value()
            hand_second_value += card.get_second_value()
        return hand_first_value, hand_second_value

    def discard_hand(self):
        self.bet = 0
        self.cards = []
        self.status = 'lost'


class Shoe(object):
    def __init__(self, decks, cut_card_at):
        self.decks = decks
        self.number_of_decks = len(decks)
        self.cut_card_at = cut_card_at

    def __len__(self):
        return sum([len(deck) for deck in self.decks])

    def get_card_at_random(self):
        # Random card index
        r_index = random.randint(0, self.__len__() - 1)
        # Card index with respect to shoe
        s_index = 0
        # Search shoe and return the requested card at random
        for deck in self.decks:
            for c_index in range(0, len(deck.cards)):
                if s_index == r_index:
                    return deck.cards.pop(c_index)
                else:
                    s_index += 1


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
        self.actions = ('S', 'H', 'DD', 'SP')

    def place_bets(self, min_bet, max_bet):
        pass

    def decide(self, bet):
        pass


class Human(Player):
    def __init__(self, name, bankroll):
        Player.__init__(self, name=name, bankroll=bankroll)

    def place_bets(self, min_bet, max_bet):
        bet = 0
        while True:
            try:
                bet = int(
                    input('{2} place your bet please.. (Min:{0}, Max:{1}) '.format(min_bet, max(self.bankroll, max_bet),
                                                                                   self.name)))
                if bet < min_bet or bet > max(self.bankroll, max_bet):
                    raise Exception
                else:
                    break
            except:
                print('Invalid bet!')
        self.bankroll -= bet
        return bet

    def decide(self, bet):
        while True:
            action = input('Choose your action (S|H|DD|SP) {name}: '.format(name=self.name)).upper()
            if action in self.actions:

                if action == 'DD':
                    self.bankroll -= bet
                return action
            else:
                print('Invalid action!')


class Machine(Player):
    def __init__(self, name, bankroll):
        Player.__init__(self, name=name, bankroll=bankroll)

    def place_bets(self, min_bet, max_bet):
        bet = random.randint(min_bet, min(self.bankroll, max_bet))
        self.bankroll -= bet
        return bet

    def decide(self, bet):
        action = self.actions[random.randint(0, len(self.actions) - 1)].upper()
        if action == 'DD':
            self.bankroll -= bet
        return action


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

    def get_first_value(self):
        return self.face.value

    def get_second_value(self):
        return self.face.second_value


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
