import random
import logging
from dataclasses import dataclass
from enum import Enum
from collections import deque
from typing import List, Optional

logger = logging.getLogger()


class Suit(Enum):
    CLUBS = "c"
    DIAMONDS = "d"
    HEARTS = "h"
    SPADES = "s"


@dataclass
class Card:
    value: int  # 2-14, where 14 = Ace (high)
    suit: Suit

    def __str__(self):
        """String representation for display/logging compatibility"""
        if self.value == 11:
            value_str = "J"
        elif self.value == 12:
            value_str = "Q"
        elif self.value == 13:
            value_str = "K"
        elif self.value == 14:
            value_str = "A"  # Ace represented as A in original format
        else:
            value_str = str(self.value)
        return f"{value_str}{self.suit.value}"

    def __repr__(self):
        """Use string representation for lists/debugging to maintain clean output"""
        return self.__str__()

    def __lt__(self, other):
        """Enable direct comparison between cards"""
        return self.value < other.value

    def __eq__(self, other):
        """Cards are equal if they have the same value (suit doesn't matter for War)"""
        return self.value == other.value


class Player:
    """Represents a player in the War game"""

    def __init__(self, name: str, cards: Optional[List[Card]] = None):
        self.name = name
        self.hand = deque(
            cards or []
        )  # Use deque for efficient operations at both ends
        self.discard = deque()

    def has_cards(self) -> bool:
        """Check if player has any cards available"""
        return len(self.hand) > 0 or len(self.discard) > 0

    def hand_size(self) -> int:
        """Get current hand size"""
        return len(self.hand)

    def discard_size(self) -> int:
        """Get current discard pile size"""
        return len(self.discard)

    def total_cards(self) -> int:
        """Get total cards owned by player"""
        return len(self.hand) + len(self.discard)

    def draw_card(self, from_bottom: bool = False) -> Optional[Card]:
        """
        Draw a card from hand. If hand is empty, refill from discard pile.
        Returns None if player has no cards left (loses).
        """
        # Refill hand if empty
        if not self.hand:
            if not self.discard:
                return None  # Player loses - no cards left
            self._refill_hand_from_discard()

        # Draw from appropriate end
        if from_bottom:
            return self.hand.popleft()  # Bottom of hand
        else:
            return self.hand.pop()  # Top of hand (default)

    def add_cards_to_discard(self, cards: List[Card]):
        """Add cards to discard pile"""
        self.discard.extend(cards)

    def _refill_hand_from_discard(self):
        """Move all cards from discard pile to hand, reversing order"""
        # Reverse the discard pile and move to hand
        while self.discard:
            self.hand.append(self.discard.pop())


class GameState:
    """Manages the overall state of the War game"""

    def __init__(self, player1_name: str = "Player 1", player2_name: str = "Player 2"):
        self.player1 = Player(player1_name)
        self.player2 = Player(player2_name)
        self.round_number = 1
        self.suit_up_active = False

    def setup_game(self, shuffle_deck: bool = True):
        """Initialize the game with a shuffled deck"""
        deck = (
            self._get_shuffled_deck() if shuffle_deck else self._create_ordered_deck()
        )
        player1_cards, player2_cards = self._split_deck(deck)

        self.player1.hand.extend(player1_cards)
        self.player2.hand.extend(player2_cards)

    def _get_shuffled_deck(self) -> List[Card]:
        """Generate and shuffle a standard 52 card deck"""
        deck = []
        for suit in Suit:
            for value in range(2, 15):  # 2-14, where 14 = Ace
                deck.append(Card(value, suit))
        random.shuffle(deck)
        return deck

    def _split_deck(self, deck: List[Card]):
        """Deal cards the way you would in an actual card game"""
        player_1_hand = []
        player_2_hand = []

        # Alternate dealing cards to each player
        for i, card in enumerate(deck):
            if i % 2 == 0:
                player_1_hand.append(card)
            else:
                player_2_hand.append(card)

        return player_1_hand, player_2_hand

    def _create_ordered_deck(self) -> List[Card]:
        """Create an ordered deck for testing purposes"""
        deck = []
        for suit in Suit:
            for value in range(2, 15):
                deck.append(Card(value, suit))
        return deck

    def check_game_over(self) -> Optional[str]:
        """Check if game is over and return winner name, or None if game continues"""
        if not self.player1.has_cards():
            return self.player2.name
        elif not self.player2.has_cards():
            return self.player1.name
        return None

    def get_game_status(self) -> dict:
        """Get current game status for logging/display"""
        return {
            "round": self.round_number,
            "player1_hand": self.player1.hand_size(),
            "player1_discard": self.player1.discard_size(),
            "player2_hand": self.player2.hand_size(),
            "player2_discard": self.player2.discard_size(),
        }

    def increment_round(self):
        """Increment the round counter"""
        self.round_number += 1

    def compare_cards(
        self,
        card_1: Card,
        card_2: Card,
        suit_up_active: bool = False,
        battle_advantage_active: bool = False,
    ) -> int:
        """
        Compare two cards and return:
            0 if they're the same value
            1 if card_1 is greater than card_2
            2 if card_1 is less than card_2
            3 if cards are the same suit, and playing 'suit_up'
            4 if King vs Queen battle with advantage is triggered
        """
        if card_1.value == card_2.value:
            return 0
        elif battle_advantage_active and self._is_king_vs_queen(card_1, card_2):
            return 4
        elif suit_up_active and (card_1.suit == card_2.suit):
            return 3
        elif card_1.value > card_2.value:
            return 1
        elif card_1.value < card_2.value:
            return 2

        raise Exception(
            f"Comparison detected something unexpected: {card_1} vs. {card_2}"
        )

    def _is_king_vs_queen(self, card_1: Card, card_2: Card) -> bool:
        """Check if one card is King and the other is Queen"""
        values = {card_1.value, card_2.value}
        return values == {13, 12}  # King=13, Queen=12

    def battle_with_advantage(
        self,
        queen_card: Card,
        king_card: Card,
        queen_player: Player,
        king_player: Player,
    ) -> tuple:
        """
        Handle battle with advantage when King vs Queen is played.
        Returns (winner_number, all_cards_played)
        winner_number: 1 if queen_player wins, 2 if king_player wins
        """
        all_cards = [queen_card, king_card]

        logger.info("Battle with Advantage!")

        # Queen plays one card
        queen_second = queen_player.draw_card()
        if queen_second is None:
            # Queen has no cards left, King wins by default
            return (2, all_cards)
        all_cards.append(queen_second)

        # King plays one card
        king_second = king_player.draw_card()
        if king_second is None:
            # King has no cards left, Queen wins by default
            return (1, all_cards)
        all_cards.append(king_second)

        logger.info(
            f"Queen's second card: {queen_second}, King's second card: {king_second}"
        )

        # Compare second cards
        if king_second.value > queen_second.value:
            # King wins all 4 cards
            logger.info("King's card is higher - King wins all 4 cards!")
            return (2, all_cards)
        else:
            # King's card is lower, King plays a third card
            king_third = king_player.draw_card()
            if king_third is None:
                # King has no cards left, Queen wins
                return (1, all_cards)
            all_cards.append(king_third)

            logger.info(f"King's third card: {king_third}")

            if king_third.value > queen_second.value:
                # King wins all 5 cards
                logger.info("King's third card is higher - King wins all 5 cards!")
                return (2, all_cards)
            else:
                # Queen wins all 5 cards
                logger.info(
                    "King's third card is still lower - Queen wins all 5 cards!"
                )
                return (1, all_cards)

    def check_and_refill_hand(self, hand: List[Card], discard: List[Card]) -> bool:
        """
        If hand is empty, move discard pile to hand
        return True if the player loses
        """
        if not any(hand):  # need to refill hand or see if the game ends
            if not any(
                discard
            ):  # out of cards, we know player 2 has cards so player 1 loses
                return True
            else:  # pick up discard pile
                discard.reverse()
                while any(discard):
                    hand.append(discard.pop())
        return False
