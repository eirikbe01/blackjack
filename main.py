import pygame
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from const import *
import random
import sys
from pygame import mixer


# Pygame setup and variables
pygame.init()
pygame.display.set_caption("Blackjack!")
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
timer = pygame.time.Clock()
welcome_font = pygame.font.Font("freesansbold.ttf", 64)
font = pygame.font.Font("freesansbold.ttf", 44)
small_font = pygame.font.Font("freesansbold.ttf", 24)
mixer.music.load("father_gascoigne.wav")
mixer.music.play(-1)
# Game variables
start = False
initial_deal = True
scores = {"player": 0, "dealer": 0, "draws": 0}
player_hand = []
player_score = 0
dealer_hand = []
dealer_score = 0
dealer_reveal = False
hand_active = False
results = ["", "BUST xD", "WIN :D", "LOSS :(", "DRAW..."]
outcome = 0
add_score = False
records = [0, 0, 0]


# Draws DEAL, HIT and STAND buttons as well as some other game stuff
def draw_buttons(start, records, result) -> list:
    buttons = []
    # if we start a new game, then draw DEAL button
    if not start:
        # Draw WELCOME
        welcome_text = font.render("Welcome to Egge's Casino", True, "white")
        screen.blit(welcome_text, (15, 130))
        blackjack_text = font.render("BLACKJACK", True, "red")
        screen.blit(blackjack_text, (165, 200))
        press_text = small_font.render("Press DEAL to play", True, "white")
        screen.blit(press_text, (180, 320))
        # Draw DEAL button
        deal = pygame.draw.rect(screen, "white", [150, 350, 300, 100], 0, 5)
        pygame.draw.rect(screen, "green", [150, 350, 300, 100], 3, 5)
        deal_text = font.render("DEAL", True, "black")
        screen.blit(deal_text, (240, 380))
        buttons.append(deal)
    # Else game is active, hit or stand
    else:
        # Draw HIT button
        hit = pygame.draw.rect(screen, "white", [0, 700, 300, 100], 0, 5)
        pygame.draw.rect(screen, "green", [0, 700, 300, 100], 3, 5)
        hit_text = font.render("HIT", True, "black")
        screen.blit(hit_text, (100, 735))
        buttons.append(hit)
        
        # Draw STAND button
        stand = pygame.draw.rect(screen, "white", [300, 700, 300, 100], 0, 5)
        pygame.draw.rect(screen, "red", [300, 700, 300, 100], 3, 5)
        stand_text = font.render("STAND", True, "black")
        screen.blit(stand_text, (372, 735))
        buttons.append(stand)

        # Draw SCORE
        score_text = small_font.render(f"Wins: {records[0]}    Losses: {records[1]}    Draws: {records[2]}", True, "white")
        screen.blit(score_text, (120, 670))
    # if we have reached a result, draw the result and give option for new round
    if result != 0:
        screen.blit(small_font.render(results[result], True, "white"), (15, 25))
        new_hand = pygame.draw.rect(screen, "white", [150, 40, 300, 100], 0, 5)
        pygame.draw.rect(screen, "black", [150, 40, 300, 100], 3, 5)
        pygame.draw.rect(screen, "green", [150, 40, 300, 100], 3, 5)
        hand_text = font.render("NEW HAND", True, "black")
        screen.blit(hand_text, (175, 70))
        buttons.append(new_hand)
    return buttons

# Deals a new card from the deck to your current hand
def deal_card(current_hand, game_deck) -> list:
    current_hand.append(game_deck.pop())
    return current_hand


# Helper method for draw_cards()
def load_cards(hand) -> list:
    cards_image_url = []
    for card in hand:
        rank, suit = card[0], card[1]
        img_url = os.path.join(f"PNG-cards-1.3/{rank}_of_{suit}.png")
        cards_image_url.append(img_url)
    return cards_image_url

# Draws the cards on screen
def draw_cards(player, dealer, reveal) -> None:
    player_cards = load_cards(player)
    i = 1
    for url in player_cards:
        player_img = pygame.image.load(url)
        player_img = pygame.transform.scale(player_img, (120, 160))
        screen.blit(player_img, (50*i, 400))
        i += 1
    
    dealer_cards = load_cards(dealer)
    if reveal:
        j = 1
        for url in dealer_cards:
            dealer_img = pygame.image.load(url)
            dealer_img = pygame.transform.scale(dealer_img, (120, 160))
            screen.blit(dealer_img, (50*j, 150))
            j += 1
    else:
        for url in dealer_cards[:1]:
            dealer_img = pygame.image.load(url)
            dealer_img = pygame.transform.scale(dealer_img, (120, 160))
            screen.blit(dealer_img, (50, 150))
        back_img = os.path.join(f"PNG-cards-1.3/backside.png")
        dealer_img_2 = pygame.image.load(back_img)
        dealer_img_2 = pygame.transform.scale(dealer_img_2, (120, 160))
        screen.blit(dealer_img_2, (110, 150))



# Draws on screen amount of wins, losses and draws
def draw_score(player, dealer):
    screen.blit(small_font.render(f"Player Score: {player}", True, "white"), (60, 575))
    screen.blit(small_font.render(f"Dealer Score: {dealer}", True, "white"), (60, 320))


# Calculates current score of cards in hand
def calculate_score(hand):
    score = 0
    for card in hand:
        rank = card[0]
        if rank in ["king", "queen", "jack"]:
            rank = 10
        elif rank == "ace":
            if (score + 11) > 21:
                rank = 1
            else:
                rank = 11
        score += int(rank)
    return score


def check_endgame(hand_act, play_score, deal_score, result, totals, add) -> tuple:
    # Check endgame conditions
    # bust=1, win=2, loss=3, push=4
    # if you and dealer stand and you have over 21 = PLAYER BUST, DEALER WIN
    if not hand_act and deal_score >= 17:
        if play_score > 21:
            result = 1
            scores["dealer"] += 1
        # if dealer has less score than player or dealer gets over 21 = DEALER BUST, PLAYER WIN
        elif deal_score < play_score <= 21 or deal_score > 21:
            result = 2
            scores["player"] += 1
        # No one busts, but dealer has higher score than player = DEALER WIN, PLAYER LOSE
        elif play_score < deal_score <= 21:
            result = 3
            scores["dealer"] += 1
        # push, both scores are equal and not bust
        else:
            result = 4
            scores["draws"] += 1
        if add:
            if result == 1 or result == 3:
                totals[1] += 1
            elif result == 2:
                totals[0] += 1
            else:
                totals[2] += 1
            add = False
    return result, totals, add

# main game loop
if __name__ == "__main__":
    # Shuffles the deck
    random.shuffle(BJ_DECK)
    while True:
        # run game at framerate=60 and draw a black background
        timer.tick(FPS)
        screen.fill("black")
        if len(BJ_DECK) == 0:
            print("I'm empty! Time to reshuffle")
            BJ_DECK = 4*DECK
            random.shuffle(BJ_DECK)
        # If new game is started, then deal initial cards
        if initial_deal:
            for i in range(2):
                player_hand = deal_card(player_hand, BJ_DECK)
                dealer_hand = deal_card(dealer_hand, BJ_DECK)
            initial_deal = False
            print(f"Player: {player_hand} \nDealer: {dealer_hand}")
        
        # once inital deal is dealt, draw the cards, start the game
        if start:
            #draw_hand()
            draw_cards(player_hand, dealer_hand, dealer_reveal)
            player_score = calculate_score(player_hand)
            if dealer_reveal:
                dealer_score = calculate_score(dealer_hand)
                if dealer_score < 17:
                    dealer_hand = deal_card(dealer_hand, BJ_DECK)
            else:
                dealer_score = calculate_score(dealer_hand[:1])
            draw_score(player_score, dealer_score)
            

        buttons = draw_buttons(start, records, outcome)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                # if we haven't started a game
                if not start:
                    # if mouse click is inside DEAL rectangle
                    if buttons[0].collidepoint(event.pos):
                        mixer.Sound('click.wav').play()
                        # start new game
                        start = True
                        player_hand = []
                        dealer_hand = []
                        hand_active = True
                        initial_deal = True
                        dealer_reveal = False
                        outcome = 0
                        add_score = True
                else:
                    if buttons[0].collidepoint(event.pos) and player_score < 21 and hand_active:
                        mixer.Sound('click.wav').play()
                        player_hand = deal_card(player_hand, BJ_DECK)
                    elif buttons[1].collidepoint(event.pos) and not dealer_reveal:
                        mixer.Sound('click.wav').play()
                        dealer_reveal = True
                        hand_active = False
                    elif len(buttons) == 3:
                        if buttons[2].collidepoint(event.pos):
                            mixer.Sound('click.wav').play()
                            start = True
                            initial_deal = True
                            player_hand = []
                            dealer_hand = []
                            hand_active = True
                            dealer_reveal = False
                            outcome = 0
                            add_score = True
                            dealer_score = 0
                            player_score = 0
        
        if hand_active and player_score > 21:
            hand_active = False
            dealer_reveal = True
        outcome, records, add_score = check_endgame(hand_active, player_score, dealer_score,
                                                    outcome, records, add_score)
        pygame.display.update()


