WIDTH = 600
HEIGHT = 800
FPS = 60

CARDS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]
SUITS = ["clubs", "diamonds", "hearts", "spades"]
DECK = [(card, suit) for suit in SUITS for card in CARDS]
BJ_DECK = DECK*4
