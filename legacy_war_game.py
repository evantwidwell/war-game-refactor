import logging
import argparse
from legacy_helper_functions import (
    check_and_refill_hand,
    compare_cards,
    get_shuffled_deck,
    split_deck,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[],
)
logger = logging.getLogger()

# Initialize args as None - will be set when running as main. This is for pytest imports
args = None


def play_round(
    player_1_hand,
    player_2_hand,
    player_1_played_cards,
    player_2_played_cards,
    player_1_discard,
    player_2_discard,
    deal=1,
    reversed=False,
):
    """
    Single round of gameplay, wars are considered part of the same round, and are recursively called
    """
    if (not args.auto) and not (args.output):
        input("Press Enter to play")

    for _ in range(0, deal):
        if not any(
            [
                any(player_1_hand),
                any(player_1_discard),
                any(player_2_hand),
                any(player_2_discard),
            ]
        ):
            # Players have played all cards in one long series of wars, just compare on the last card or draw
            # assume suit_up can't activate on this last hand
            return compare_cards(
                player_1_played_cards[-1],
                player_2_played_cards[-1],
                suit_up_active=False,
            )

        player_2_win = check_and_refill_hand(player_1_hand, player_1_discard)
        if player_2_win:
            return 2
        player_1_played_cards.append(player_1_hand.pop(0 if reversed else -1))

        player_1_win = check_and_refill_hand(player_2_hand, player_2_discard)
        if player_1_win:
            return 1
        player_2_played_cards.append(player_2_hand.pop(0 if reversed else -1))

    comparison = compare_cards(
        player_1_played_cards[-1],
        player_2_played_cards[-1],
        suit_up_active=(args.suit_up and deal != 4),
    )  # check if deal is 4, if it is it's a regular war and you can't enter suit-up

    logger.info(
        f"P1: H:{str(len(player_1_hand)).ljust(2)} | D:{str(len(player_1_discard)).ljust(2)} | {player_1_played_cards}{'*' if comparison == 1 else ' '}"
    )
    logger.info(
        f"P2: H:{str(len(player_2_hand)).ljust(2)} | D:{str(len(player_2_discard)).ljust(2)} | {player_2_played_cards}{'*' if comparison == 2 else ' '}"
    )

    if comparison == 1:
        player_1_discard += player_1_played_cards + player_2_played_cards
    elif comparison == 2:
        player_2_discard += player_2_played_cards + player_1_played_cards
    elif comparison == 0:
        logger.info("War!")
        return play_round(
            player_1_hand,
            player_2_hand,
            player_1_played_cards,
            player_2_played_cards,
            player_1_discard,
            player_2_discard,
            deal=4,
        )
    elif comparison == 3:
        logger.info("Suit Up!")
        return play_round(
            player_1_hand,
            player_2_hand,
            player_1_played_cards,
            player_2_played_cards,
            player_1_discard,
            player_2_discard,
            deal=2,
            reversed=True,
        )

    return None  # no winner yet


def play_war():
    """
    Play game
    """

    # setup deck and player data objects
    deck = get_shuffled_deck()
    player_1_hand, player_2_hand = split_deck(deck)
    player_1_discard, player_2_discard = [], []
    round = 1

    while True:
        # game play loop
        assert (
            round < 10000
        ), "infinite loop suspected"  # if player's don't grab their own deck first when picking up cards, the game can enter infinite loops
        player_1_played_cards, player_2_played_cards = [], []
        logger.info(f"---- Round {round} ----")
        winner = play_round(
            player_1_hand,
            player_2_hand,
            player_1_played_cards,
            player_2_played_cards,
            player_1_discard,
            player_2_discard,
            deal=1,
        )
        if winner:
            logger.info(f"Player {winner} Wins in {round} rounds!")
            break
        elif winner == 0:  # for rare case
            logger.info("Draw!")
            break

        # move cards from discard to hand if hand is empty
        player_2_wins = check_and_refill_hand(player_1_hand, player_1_discard)
        if player_2_wins:
            logger.info(f"Player 2 Wins in {round} rounds!")
            break

        player_1_wins = check_and_refill_hand(player_2_hand, player_2_discard)
        if player_1_wins:
            logger.info(f"Player 1 Wins in {round} rounds!")
            break

        round += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Prevent request for user action, move game along automatically",
    )
    parser.add_argument(
        "--output",
        nargs="?",
        const="gameplay.log",
        default=False,
        help="Auto play game and output the game results to a log file",
    )
    parser.add_argument(
        "--suit-up", action="store_true", help='run game with "suit up" house rule'
    )
    args = parser.parse_args()

    if args.output:
        logger.addHandler(
            logging.FileHandler(
                mode="w", filename=(args.output.replace(".log", "") + ".log")
            )
        )
    else:
        logger.addHandler(logging.StreamHandler())
    play_war()
