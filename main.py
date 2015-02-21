from abc import ABCMeta, abstractmethod
from collections import namedtuple
from collections import defaultdict
from collections import deque
from copy import deepcopy
import inspect
import math
import random
import itertools
import sys

__author__ = 'mejmo'

PLAYERS_COUNT = 2
CARDS_NUM_START = 5
SHUFFLE_COUNT = 0
SIMULATE_LEVELS = 2

def p(what):
    stack = inspect.stack()
    print("%-40s::%-15s - %s" % (stack[1][0].f_locals['self'].__class__, stack[1][0].f_code.co_name, what))

Card = namedtuple('Card', 'colour type')

class Player:
    def __init__(self, index, name):
        self.cards = Cards()
        self.name = name
        self.index = index
        self.possible_player_deck = {x+1: [] for x in range(0, PLAYERS_COUNT)}
        del self.possible_player_deck[index]
        p("Player %s created" % name)

    def take_card(self, game, count):
        self.cards.extend(game.get_cards_from_deck(count))
        p("%d cards added to player cards. Cards on hand: %s" % (count, self.get_formatted_cards()))

    def get_formatted_cards(self):
        return str(self.cards)

class Cards(list):
    def __str__(self):
        return str(["%s-%s" % (card.colour, card.type) for card in self])


class Universe(list):
    card_types = [
        '7', '8', '9', '10', 'DOL', 'HOR', 'KRAL', 'ESO'
    ]
    card_colours = [
        'ZELEN', 'GULA', 'CERVEN', 'ZALUD'
    ]
    def __init__(self, *args):
        list.__init__(self, *args)
        self.extend(map(lambda x: Card(x[0], x[1]), itertools.product(Universe.card_colours, Universe.card_types)))

class Deck(Cards):
    def __init__(self):
        p("Creating new deck from universe")
        list.__init__(self, Universe())
        L = [self.pop(8),
             self.pop(9),
             self.pop(2),
             self.pop(26),
             self.pop(7),
             self.pop(1),
             self.pop(23)
        ]
        for z in L:
            self.insert(0, z)
        for _ in itertools.repeat(None, SHUFFLE_COUNT): random.shuffle(self)
        p("New deck shuffled %d times" % SHUFFLE_COUNT)

class UsedDeck(Cards):
    def __init__(self):
        self.new = []

    def reset_new(self):
        self.new = []


class GameAction(object):
    __metaclass__ = ABCMeta
    _action_name = ""

    def not_imp(self):
        return NotImplemented("GameAction type must implement %s method" % inspect.stack()[1][0].f_code.co_name)

    @abstractmethod
    def play(self, game):
        raise self.not_imp()

    def __str__(self):
        return self._action_name

class SevenAction(GameAction):

    _action_name = "SevenAction"

    # def play(self, game):
    #     games = []
    #
    #     for card in game.get_current_player().cards:
    #
    #         if card.type == '7'
    #         _game = deepcopy(game)
    #
    #         if card.type == game.current_colour or game.state & GameStates.PLAYER_RETURNED_TO_GAME:
    #             _game.play_cards([card], self)
    #             _game.next_player()
    #             games.append(_game)
    #
    #
    #     if game.get_top_card().type == '7'
    #
    #     return games

class SameTypeAction(GameAction):

    _action_name = "SameTypeAction"

    def play(self, game):
        games = []

        _ = {
            lambda card: card.type == game.get_top_card().type or \
                         game.state & GameStates.PLAYER_RETURNED_TO_GAME:card \
                         for card in game.get_current_player().cards
        }
        cards = [v for k, v in _.items() if k is True]

        perms = [itertools.permutations(cards, i+1) for i in range(0, len(cards))]

        for perm in perms:
            for pos_turn in perm:
                _game = deepcopy(game)
                _game.play_cards(list(pos_turn), self)
                if list(pos_turn) < 4: _game.next_player()
                games.append(_game)

        return games

class SameColourAction(GameAction):

    _action_name = "SameColourAction"

    def play(self, game):

        games = []

        for card in game.get_current_player().cards:
            _game = deepcopy(game)

            if card.colour == game.current_colour or game.state & GameStates.PLAYER_RETURNED_TO_GAME:
                _game.play_cards([card], self)
                _game.next_player()
                games.append(_game)

        return games

class DrawAction(GameAction):

    _action_name = "DrawAction"

    def play(self, game):

        games = []
        all_possible_cards = list(set(Universe()).difference(set(game.get_current_player().cards)))

        if len(game.deck) > 0:
            for card in all_possible_cards:
                _game = deepcopy(game)
                _game.get_current_player().cards.append(card)
                _game.play_cards([], self)
                _game.next_player()
                games.append(_game)
        else:
            _game = deepcopy(game)
            _game.get_current_player().append(_game.used_deck.pop(0))
            _game.next_player()
            games = [_game]

        return games

class FaraonAction(GameAction):

    _action_name = "FaraonAction"

    def play(self, game):

        games = []
        if ('ZELEN', 'DOL') in game.get_current_player().cards:
            _game = deepcopy(game)
            _game.play_cards(('ZELEN', 'DOL'), self)
            _game.next_player()
            games.append(_game)

        return games

class ChangeColourAction(GameAction):

    _action_name = "ChangeColourAction"

    def play(self, game):

        games = []

        _ = [card for card in game.get_current_player().cards if card.type == "HOR"]
        perms = [itertools.permutations(_, i+1) for i in range(0, len(_))]

        for perm in perms:
            for pos_turn in perm:
                _game = deepcopy(game)
                _game.play_cards(list(pos_turn), self)
                _game.next_player()
                for colour in Universe.card_colours:
                    __game = deepcopy(_game)
                    __game.current_colour = colour
                    games.append(__game)

        return games


class BackToGameAction(GameAction):

    _action_name = "BackToGame"

    def play(self, game):

        games = []

        if ("CERVEN", "7") in game.get_current_player().cards and (game.state == GameStates.GAME_ENDED):

            _game = deepcopy(game)
            _game.play_cards([Card("CERVEN", "7")], self)
            _game.get_current_player().cards.extend(_game.get_cards_from_deck(3))
            _game.next_player()
            _game.state |= GameStates.PLAYER_RETURNED_TO_GAME
            games.append(_game)

        return games

class AceAction(GameAction):

    _action_name = "AceAction"

    def play(self, game):

        games = []

        _ = [card for card in game.get_current_player().cards if card.type == "ESO"]
        perms = [itertools.permutations(_, i+1) for i in range(0, len(_))]

        for perm in perms:
            for pos_turn in perm:
                _game = deepcopy(game)
                _game.play_cards(list(pos_turn), self)

                if not len(_game.get_current_player().cards):
                    _game.next_player()

                games.append(_game)

        return games

class Game:

    def __init__(self, players):
        self.deck = Deck()
        self.used_deck = UsedDeck()
        self.players = deque(players)
        self.played_cards = []
        self.last_action = None
        self.state = GameStates.GAME_PLAYING
        self.seven_played = 0

        for player in players: player.take_card(self, CARDS_NUM_START)

        self.used_deck.append(self.deck.pop(0))
        self.current_colour = self.get_top_card().colour

        p("Game created. On top of the used deck is: %s" % str(self.get_top_card()))

    def play_cards(self, iterable, action):
        self.used_deck.extend(iterable)
        self.played_cards = Cards(iterable)
        self.last_action = action

        for card in iterable: self.get_current_player().cards.remove(card)

        if (not len(self.get_current_player().cards)):
            self.state = GameStates.GAME_ENDED
        else:
            self.state = GameStates.GAME_PLAYING


    def get_current_player(self):
        return self.players[0]

    def next_player(self):
        self.players.rotate(-1)

    def get_cards_from_deck(self,  count):
        cards = []
        while (len(cards) != count):
            try:
                cards.append(self.deck.pop(0))
            except IndexError:
                cards.append(self.used_deck.pop(0))

        return cards

    def get_top_card(self):
        return self.used_deck[-1]

    def get_prob_in_player_deck(self, card):
        source_cards = self.get_current_player().cards

        cards_to_remove = list(source_cards)
        cards_to_remove.extend(self.used_deck)

        all_possible_cards = list(set(Universe()).difference(set(cards_to_remove)))

        return round(float(1)/len(all_possible_cards)*100, 3) if card in all_possible_cards else 0

    def get_game_state(self):
        return [attr for attr in dir(GameStates) if not callable(attr) and not attr.startswith("__") and getattr(GameStates, attr) & self.state]

    def print(self):
        p("----------- GAME OUTPUT -----------------")
        p("Played action: %s Played cards: %s" % (str(self.last_action), str(self.played_cards)))
        p("%s %s" % ("Used deck:", str(self.used_deck)))
        p("Card on top: %s" % (str(self.get_top_card())))
        p("Game state: %s" % " | ".join(self.get_game_state()))
        p("Current coulour: %s" % (str(self.current_colour)))
        for player in self.players:
            p("Player: %d Name: %-10s Cards: %s" % (player.index, player.name, str(player.get_formatted_cards())))


class GameStates:
    PLAYER_RETURNED_TO_GAME = 1
    GAME_PLAYING = 2
    GAME_ENDED = 4

class Simulator:
    actions = [
        # RedSevenAction,
        # SevenAction,
        # FaraonAction,
        # AceAction,
        # SameFourTypesAction,
        # SameColourAction,
        # SameTypeAction,
        # DrawAction,
        ChangeColourAction
    ]

    def __init__(self, game):
        self.game = game

    def make_tree(self, game, tree=None, level=0):

        if (tree is None):
            tree = game

        for action in Simulator.actions:
            obj = action()
            games = obj.play(game)

            if len(games):
                p("Action: "+str(obj)+" provides "+len(games).__str__()+" possible games")
                for zgame in games:
                    # zgame = games[0]
                    zgame.print()
                    p("")
                    p("Probabilty: "+str(zgame.get_prob_in_player_deck(('ZELEN', 'HOR'))))

class Tree:
    def __init__(self):
        def tree():
            return defaultdict(tree)
        self.game_tree = tree()

    def print(self, t):
        return {k: self.print(t[k]) for k in t}

players = [Player(1, "Pocitac1"), Player(2, "Mejmo")]
game = Game(players)

all = Universe()
for z in [Card("ZELEN", "ESO"), Card("ZELEN", "8"), Card("ZELEN", "10")]:
    print(z)
    all.remove(z)

game.players[1].cards = Cards([Card("ZELEN", "8"), Card("CERVEN", "7")])
game.players[0].cards = Cards([Card("ZELEN", "ESO")])
game.used_deck = Cards([Card("ZELEN", "10")])
game.current_colour = "ZELEN"
game.print()
action = AceAction()
games = action.play(game)

for z in games:
    z.print()

action = BackToGameAction()
games = action.play(games[0])

print("Games list:")
for z in games:
    z.print()



# sim = Simulator(game)
# sim.make_tree(game)

# actions = game.get_possible_turns()

# print(actions)

# for card in Universe():
#     print(card.colour+card.type+": "+game.get_prob_in_player_deck(card, 0, 1).__str__()+"%")





