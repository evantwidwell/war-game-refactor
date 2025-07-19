import logging
import argparse
from helper_functions import GameState

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[],
)
logger = logging.getLogger()

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
parser.add_argument(
    "--battle-advantage",
    action="store_true",
    help='run game with "battle with advantage" house rule',
)
args = parser.parse_args()


def _handle_empty_hands(game_state, player_1_played_cards, player_2_played_cards):
    """Handle the case where both players are out of cards during war"""
    if not game_state.player1.has_cards() and not game_state.player2.has_cards():
        if player_1_played_cards and player_2_played_cards:
            return game_state.compare_cards(
                player_1_played_cards[-1],
                player_2_played_cards[-1],
                suit_up_active=False,
            )
        else:
            return 0  # Draw if no cards were played
    return None


def _draw_cards_for_round(
    game_state, player_1_played_cards, player_2_played_cards, deal, reversed
):
    """Draw the required number of cards for both players"""
    for _ in range(0, deal):
        # Check if both players are out of cards
        empty_hand_result = _handle_empty_hands(
            game_state, player_1_played_cards, player_2_played_cards
        )
        if empty_hand_result is not None:
            return empty_hand_result

        # Player 1 draws a card
        card1 = game_state.player1.draw_card(from_bottom=reversed)
        if card1 is None:
            return 2  # Player 2 wins
        player_1_played_cards.append(card1)

        # Player 2 draws a card
        card2 = game_state.player2.draw_card(from_bottom=reversed)
        if card2 is None:
            return 1  # Player 1 wins
        player_2_played_cards.append(card2)

    return None  # Continue with round


def _handle_battle_with_advantage(
    game_state, player_1_played_cards, player_2_played_cards
):
    """Handle battle with advantage when King vs Queen is played"""
    card1, card2 = player_1_played_cards[-1], player_2_played_cards[-1]

    if card1.value == 13:  # Player 1 has King
        winner, all_cards = game_state.battle_with_advantage(
            card2, card1, game_state.player2, game_state.player1
        )
        if winner == 1:  # Queen (Player 2) wins
            game_state.player2.add_cards_to_discard(
                player_2_played_cards + player_1_played_cards + all_cards[2:]
            )
        else:  # King (Player 1) wins
            game_state.player1.add_cards_to_discard(
                player_1_played_cards + player_2_played_cards + all_cards[2:]
            )
    else:  # Player 2 has King
        winner, all_cards = game_state.battle_with_advantage(
            card1, card2, game_state.player1, game_state.player2
        )
        if winner == 1:  # Queen (Player 1) wins
            game_state.player1.add_cards_to_discard(
                player_1_played_cards + player_2_played_cards + all_cards[2:]
            )
        else:  # King (Player 2) wins
            game_state.player2.add_cards_to_discard(
                player_2_played_cards + player_1_played_cards + all_cards[2:]
            )


def _log_round_results(
    game_state, player_1_played_cards, player_2_played_cards, comparison
):
    """Log the results of the current round"""
    logger.info(
        f"P1: H:{str(len(game_state.player1.hand)).ljust(2)} | D:{str(len(game_state.player1.discard)).ljust(2)} | {player_1_played_cards}{'*' if comparison == 1 else ' '}"
    )
    logger.info(
        f"P2: H:{str(len(game_state.player2.hand)).ljust(2)} | D:{str(len(game_state.player2.discard)).ljust(2)} | {player_2_played_cards}{'*' if comparison == 2 else ' '}"
    )


def play_round(
    game_state, player_1_played_cards, player_2_played_cards, deal=1, reversed=False
):
    """
    Single round of gameplay, wars are considered part of the same round, and are recursively called
    """
    if (not args.auto) and not (args.output):
        input("Press Enter to play")

    # Draw cards for this round
    early_result = _draw_cards_for_round(
        game_state, player_1_played_cards, player_2_played_cards, deal, reversed
    )
    if early_result is not None:
        return early_result

    # Compare the cards
    comparison = game_state.compare_cards(
        player_1_played_cards[-1],
        player_2_played_cards[-1],
        suit_up_active=(args.suit_up and deal != 4),
        battle_advantage_active=(args.battle_advantage and deal != 4),
    )

    # Log round results
    _log_round_results(
        game_state, player_1_played_cards, player_2_played_cards, comparison
    )

    # Handle the comparison result
    if comparison == 1:
        game_state.player1.add_cards_to_discard(
            player_1_played_cards + player_2_played_cards
        )
    elif comparison == 2:
        game_state.player2.add_cards_to_discard(
            player_2_played_cards + player_1_played_cards
        )
    elif comparison == 0:
        logger.info("War!")
        return play_round(
            game_state, player_1_played_cards, player_2_played_cards, deal=4
        )
    elif comparison == 3:
        logger.info("Suit Up!")
        return play_round(
            game_state,
            player_1_played_cards,
            player_2_played_cards,
            deal=2,
            reversed=True,
        )
    elif comparison == 4:
        logger.info("Battle with Advantage Triggered!")
        _handle_battle_with_advantage(
            game_state, player_1_played_cards, player_2_played_cards
        )

    return None  # no winner yet


def play_war():
    """
    Play game
    """

    # Setup game using GameState class
    game_state = GameState()
    game_state.setup_game(shuffle_deck=True)

    while True:
        # Game play loop
        assert (
            game_state.round_number < 10000
        ), "infinite loop suspected"  # if player's don't grab their own deck first when picking up cards, the game can enter infinite loops
        player_1_played_cards, player_2_played_cards = [], []
        logger.info(f"---- Round {game_state.round_number} ----")

        winner = play_round(
            game_state, player_1_played_cards, player_2_played_cards, deal=1
        )
        if winner:
            logger.info(f"Player {winner} Wins in {game_state.round_number} rounds!")
            break
        elif winner == 0:  # for rare case
            logger.info("Draw!")
            break

        # Check if game is over after round
        game_winner = game_state.check_game_over()
        if game_winner:
            logger.info(f"{game_winner} Wins in {game_state.round_number} rounds!")
            break

        game_state.increment_round()


if __name__ == "__main__":
    if args.output:
        logger.addHandler(
            logging.FileHandler(
                mode="w", filename=(args.output.replace(".log", "") + ".log")
            )
        )
    else:
        logger.addHandler(logging.StreamHandler())
    play_war()
