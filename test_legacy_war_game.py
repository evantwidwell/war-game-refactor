import pytest
import random
from types import SimpleNamespace
from legacy_helper_functions import (
    get_shuffled_deck,
    split_deck,
    compare_cards,
    check_and_refill_hand,
    map_card_to_numeric,
)

# Mock args before importing legacy_war_game
import legacy_war_game

legacy_war_game.args = SimpleNamespace(auto=True, output=False, suit_up=False)


@pytest.fixture(autouse=True)
def set_random_seed():
    """Set a fixed seed for reproducible tests"""
    random.seed(42)


class TestLegacyHelperFunctions:
    """Test the legacy helper functions"""

    def test_get_shuffled_deck(self):
        """Test that get_shuffled_deck creates a complete 52-card deck"""
        deck = get_shuffled_deck()

        # Should have 52 cards
        assert len(deck) == 52

        # Should have unique cards
        assert len(set(deck)) == 52

        # Should have 13 cards of each suit
        for suit in ["c", "d", "h", "s"]:
            suit_cards = [card for card in deck if card.endswith(suit)]
            assert len(suit_cards) == 13

    def test_split_deck(self):
        """Test deck splitting between two players"""
        deck = list(range(52))  # Use numbers for predictable testing
        player1, player2 = split_deck(deck)

        # Both players should get cards
        assert len(player1) > 0
        assert len(player2) > 0

        # Total should equal original deck
        assert len(player1) + len(player2) == 52

        # Player 1 gets first half, Player 2 gets second half
        assert len(player1) == 26
        assert len(player2) == 26

    def test_map_card_to_numeric(self):
        """Test card string to numeric conversion"""
        # Test number cards
        assert map_card_to_numeric("5h") == 5
        assert map_card_to_numeric("10c") == 10

        # Test face cards
        assert map_card_to_numeric("Jd") == 11
        assert map_card_to_numeric("Qs") == 12
        assert map_card_to_numeric("Kh") == 13

        # Test Ace (should be high)
        assert map_card_to_numeric("1c") == 14

        # Test Joker
        assert map_card_to_numeric("Joker") is None

    def test_compare_cards_basic(self):
        """Test basic card comparison"""
        # Higher card wins
        assert compare_cards("Kh", "5c") == 1  # King beats 5
        assert compare_cards("5c", "Kh") == 2  # 5 loses to King

        # Equal cards
        assert compare_cards("5h", "5c") == 0  # Same value

        # Ace high
        assert compare_cards("1h", "Kc") == 1  # Ace beats King

    def test_compare_cards_suit_up(self):
        """Test suit up functionality"""
        # Same suit should trigger suit up
        result = compare_cards("5h", "10h", suit_up_active=True)
        assert result == 3

        # Different suits should use normal comparison
        result = compare_cards("5h", "10c", suit_up_active=True)
        assert result == 2  # 5 < 10

        # Equal values should still return 0 even with suit up
        result = compare_cards("5h", "5c", suit_up_active=True)
        assert result == 0

    def test_check_and_refill_hand(self):
        """Test hand refilling from discard pile"""
        # Test with cards in discard
        hand = []
        discard = ["Kh", "5c", "10d"]

        result = check_and_refill_hand(hand, discard)
        assert result is False  # Should not lose
        assert len(hand) > 0  # Hand should have cards
        assert len(discard) == 0  # Discard should be empty

        # Test with no cards anywhere
        empty_hand = []
        empty_discard = []

        result = check_and_refill_hand(empty_hand, empty_discard)
        assert result is True  # Should lose (return True)


class TestLegacyCardRepresentation:
    """Test legacy card representation and behavior"""

    def test_card_string_format(self):
        """Test that legacy cards are in expected string format"""
        # Check a few expected cards exist
        expected_cards = [
            "1h",
            "5c",
            "Jd",
            "Qs",
            "Kh",
        ]  # Ace, number, Jack, Queen, King

        for expected_card in expected_cards:
            # We can't guarantee these exact cards, but we can check format
            pass  # Legacy system doesn't have individual card creation

    @pytest.mark.parametrize(
        "card,expected_value",
        [
            ("2h", 2),
            ("3c", 3),
            ("4d", 4),
            ("5s", 5),
            ("6h", 6),
            ("7c", 7),
            ("8d", 8),
            ("9s", 9),
            ("10h", 10),
            ("Jc", 11),
            ("Qd", 12),
            ("Ks", 13),
            ("1h", 14),  # Ace high
        ],
    )
    def test_card_value_mapping(self, card, expected_value):
        """Test various card value mappings"""
        assert map_card_to_numeric(card) == expected_value


class TestLegacyGameMechanics:
    """Test core game mechanics in legacy implementation"""

    def test_deck_generation_consistency(self):
        """Test that legacy deck generation produces valid results"""
        # Set seed for reproducible results
        random.seed(42)
        deck = get_shuffled_deck()

        # Basic validation
        assert len(deck) == 52

        # Check all expected cards are present
        expected_suits = ["c", "d", "h", "s"]
        expected_values = [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "J",
            "Q",
            "K",
        ]

        for suit in expected_suits:
            for value in expected_values:
                card = value + suit
                assert card in deck, f"Card {card} missing from deck"

    def test_hand_operations(self):
        """Test hand and discard pile operations"""
        # Test basic hand operations that mirror Player class functionality
        hand = ["Kh", "5c", "10d"]
        discard = []

        # Test drawing from hand (equivalent to Player.draw_card)
        card = hand.pop(-1)  # Draw from top
        assert card == "10d"
        assert len(hand) == 2

        # Test adding to discard (equivalent to Player.add_cards_to_discard)
        discard.extend([card, "Ah"])
        assert len(discard) == 2

        # Test refill operation
        hand.clear()
        result = check_and_refill_hand(hand, discard)
        assert result is False  # Should not lose
        assert len(hand) > 0  # Should have cards from discard

    def test_game_over_detection(self):
        """Test game over conditions"""
        # Test when player has no cards (equivalent to GameState.check_game_over)
        empty_hand = []
        empty_discard = []

        result = check_and_refill_hand(empty_hand, empty_discard)
        assert result is True  # Player should lose

        # Test when player has cards in discard
        hand_with_discard = []
        discard_with_cards = ["Kh", "5c"]

        result = check_and_refill_hand(hand_with_discard, discard_with_cards)
        assert result is False  # Player should not lose


class TestLegacyGameIntegration:
    """Integration tests for legacy game system"""

    def test_complete_game_setup(self):
        """Test complete game setup and basic operations"""
        # Set seed for predictable testing
        random.seed(42)

        # Generate and split deck
        deck = get_shuffled_deck()
        player1_hand, player2_hand = split_deck(deck)

        # Initialize discard piles
        player1_discard = []
        player2_discard = []

        # Both players should have cards
        assert len(player1_hand) > 0
        assert len(player2_hand) > 0

        # Total cards should be 52
        total_cards = (
            len(player1_hand)
            + len(player2_hand)
            + len(player1_discard)
            + len(player2_discard)
        )
        assert total_cards == 52

        # Draw cards and compare (simulate one round)
        card1 = player1_hand.pop(-1)
        card2 = player2_hand.pop(-1)

        result = compare_cards(card1, card2)
        assert result in [0, 1, 2, 3]  # Valid comparison result

    def test_suit_up_integration(self):
        """Test suit up rule integration"""
        # Test that suit up works in context
        same_suit_cards = ["5h", "10h"]
        different_suit_cards = ["5h", "10c"]

        # Same suit with suit up should return 3
        result = compare_cards(
            same_suit_cards[0], same_suit_cards[1], suit_up_active=True
        )
        assert result == 3

        # Different suits should use normal comparison
        result = compare_cards(
            different_suit_cards[0], different_suit_cards[1], suit_up_active=True
        )
        assert result == 2  # 5 < 10


class TestLegacyGameLogic:
    """Test core game logic equivalent to GameState tests"""

    @pytest.mark.parametrize(
        "card1,card2,expected",
        [
            # Basic comparisons
            ("Kh", "5c", 1),  # King beats 5
            ("5c", "Kh", 2),  # 5 loses to King
            ("Qd", "Jh", 1),  # Queen beats Jack
            ("1s", "Kc", 1),  # Ace beats King
            ("5h", "5c", 0),  # Same values tie
            # Face card comparisons
            ("Jh", "10c", 1),  # Jack beats 10
            ("Qd", "Js", 1),  # Queen beats Jack
            ("Kc", "Qh", 1),  # King beats Queen
            ("1d", "Ks", 1),  # Ace beats King
        ],
    )
    def test_card_comparison_scenarios(self, card1, card2, expected):
        """Test various card comparison scenarios"""
        result = compare_cards(card1, card2)
        assert result == expected

    def test_edge_cases(self):
        """Test edge cases in legacy implementation"""
        # Test with minimum and maximum values
        assert compare_cards("1h", "2c") == 1  # Ace beats 2
        assert compare_cards("2c", "1h") == 2  # 2 loses to Ace

        # Test all face cards
        face_card_order = [("Jh", "Qc", 2), ("Qh", "Kc", 2), ("Kh", "1c", 2)]
        for card1, card2, expected in face_card_order:
            result = compare_cards(card1, card2)
            assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])
