import logging
import argparse
from helper_functions import (
    check_and_refill_hand,
    compare_cards,
    get_shuffled_deck,
    split_deck,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[],
)
logger = logging.getLogger()

parser = argparse.ArgumentParser()
parser.add_argument('--auto', action='store_true', help='prevent request for user action to move game along.')
parser.add_argument('--output', nargs='?', const='gameplay.log', default=False, help='file to output logs to, game will auto play.')
args = parser.parse_args()

def play_round(player_1_hand, player_2_hand, player_1_played_cards, player_2_played_cards, player_1_discard, player_2_discard, deal=1):
    '''
    Single round of gameplay, wars are considered part of the same round, and are recursively called
    '''
    if (not args.auto) and not(args.output): input('Press Enter to play')
    for _ in range(0, deal):
        if not any([any(player_1_hand), any(player_1_discard), any(player_2_hand), any(player_2_discard)]):
            # Players have played all cards in one long series of wars, just compare on the last card or draw
            return compare_cards(player_1_played_cards[-1], player_2_played_cards[-1])

        player_2_win = check_and_refill_hand(player_1_hand, player_1_discard)
        if player_2_win: return 2
        player_1_played_cards.append(player_1_hand.pop())

        player_1_win = check_and_refill_hand(player_2_hand, player_2_discard)
        if player_1_win: return 1
        player_2_played_cards.append(player_2_hand.pop())

    comparison = compare_cards(player_1_played_cards[-1], player_2_played_cards[-1])

    logger.info(f"P1: H:{str(len(player_1_hand)).ljust(2)} | D:{str(len(player_1_discard)).ljust(2)} | {player_1_played_cards}{'*' if comparison == 1 else ' '}")#\nHand: {player_1_hand}\nDiscard: {player_1_discard}")
    logger.info(f"P2: H:{str(len(player_2_hand)).ljust(2)} | D:{str(len(player_2_discard)).ljust(2)} | {player_2_played_cards}{'*' if comparison == 2 else ' '}")#\nHand: {player_2_hand}\nDiscard: {player_2_discard}")

    if comparison == 1:
        player_1_discard += player_1_played_cards + player_2_played_cards
    elif comparison == 2:
        player_2_discard += player_2_played_cards + player_1_played_cards
    else:
        logger.info("War!")
        return play_round(player_1_hand, player_2_hand, player_1_played_cards, player_2_played_cards, player_1_discard, player_2_discard, deal=4)

    return None  # no winner yet

def play_war():
    '''
    Play game
    '''

    #setup deck and player data objects
    deck = get_shuffled_deck()
    player_1_hand, player_2_hand = split_deck(deck)
    player_1_discard, player_2_discard = [], []
    round = 1

    while(True):
        #game play loop
        assert round < 10000, "infinite loop suspected"  # if player's don't grab their own deck first when picking up cards, the game can enter infinite loops
        player_1_played_cards, player_2_played_cards = [], []
        logger.info(f'---- Round {round} ----')
        winner = play_round(player_1_hand, player_2_hand, player_1_played_cards, player_2_played_cards, player_1_discard, player_2_discard, deal=1)
        if winner:
            logger.info(f'Player {winner} Wins in {round} rounds!')
            break
        elif winner == 0:  # for rare case
            logger.info("Draw!")
            break

        # move cards from discard to hand if hand is empty
        player_2_wins = check_and_refill_hand(player_1_hand, player_1_discard)
        if player_2_wins:
            logger.info(f'Player 2 Wins in {round} rounds!')
            break

        player_1_wins = check_and_refill_hand(player_2_hand, player_2_discard)
        if player_1_wins:
            logger.info(f'Player 1 Wins in {round} rounds!')
            break

        round += 1

if __name__ == '__main__':
    print('handlers:', logger.handlers)
    if args.output:
        logger.addHandler(logging.FileHandler(mode='w', filename=(args.output.replace('.log', '')+'.log')))
    else:
        logger.addHandler(logging.StreamHandler())
    print(args)
    play_war()
