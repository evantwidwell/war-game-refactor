#!/usr/bin/env python3
"""
Comprehensive tests for the War card game implementation.
Tests both the core classes and the game functionality.
"""

import unittest
from helper_functions import Card, Suit, Player, GameState


class TestCard(unittest.TestCase):
    """Test the Card class"""

    def test_card_creation(self):
        """Test creating cards with different values and suits"""
        card = Card(5, Suit.HEARTS)
        self.assertEqual(card.value, 5)
        self.assertEqual(card.suit, Suit.HEARTS)

    def test_card_string_representation(self):
        """Test card string formatting matches expected format"""
        self.assertEqual(str(Card(5, Suit.HEARTS)), "5h")
        self.assertEqual(str(Card(11, Suit.CLUBS)), "Jc")
        self.assertEqual(str(Card(12, Suit.DIAMONDS)), "Qd")
        self.assertEqual(str(Card(13, Suit.SPADES)), "Ks")
        self.assertEqual(str(Card(14, Suit.DIAMONDS)), "Ad")

    def test_card_comparison(self):
        """Test card comparison operations"""
        ace = Card(14, Suit.HEARTS)
        king = Card(13, Suit.SPADES)
        five = Card(5, Suit.CLUBS)

        # Test less than
        self.assertTrue(king < ace)
        self.assertTrue(five < king)

        # Test equality (value only, suit doesn't matter)
        self.assertEqual(ace, Card(14, Suit.CLUBS))
        self.assertNotEqual(ace, king)


class TestPlayer(unittest.TestCase):
    """Test the Player class"""

    def test_player_creation(self):
        """Test creating a player with and without initial cards"""
        # Empty player
        player = Player("Test Player")
        self.assertEqual(player.name, "Test Player")
        self.assertEqual(player.hand_size(), 0)
        self.assertEqual(player.discard_size(), 0)
        self.assertFalse(player.has_cards())

        # Player with initial cards
        cards = [Card(5, Suit.HEARTS), Card(10, Suit.CLUBS)]
        player_with_cards = Player("Player 2", cards)
        self.assertEqual(player_with_cards.hand_size(), 2)
        self.assertTrue(player_with_cards.has_cards())

    def test_draw_card(self):
        """Test drawing cards from hand"""
        cards = [Card(5, Suit.HEARTS), Card(10, Suit.CLUBS)]
        player = Player("Test", cards)

        # Draw from top (default)
        top_card = player.draw_card()
        self.assertEqual(str(top_card), "10c")  # Last card added
        self.assertEqual(player.hand_size(), 1)

        # Draw from bottom
        bottom_card = player.draw_card(from_bottom=True)
        self.assertEqual(str(bottom_card), "5h")  # First card added
        self.assertEqual(player.hand_size(), 0)

    def test_draw_card_with_refill(self):
        """Test drawing card when hand is empty but discard has cards"""
        player = Player("Test")

        # Add cards to discard pile
        discard_cards = [Card(5, Suit.HEARTS), Card(10, Suit.CLUBS)]
        player.add_cards_to_discard(discard_cards)

        # Draw should trigger refill
        card = player.draw_card()
        self.assertIsNotNone(card)
        self.assertEqual(player.discard_size(), 0)  # Discard should be empty
        self.assertGreater(player.hand_size(), 0)  # Hand should have cards

    def test_draw_card_no_cards_left(self):
        """Test drawing card when player has no cards left"""
        player = Player("Test")
        card = player.draw_card()
        self.assertIsNone(card)


class TestGameState(unittest.TestCase):
    """Test the GameState class"""

    def test_game_state_creation(self):
        """Test creating a game state"""
        game = GameState()
        self.assertEqual(game.player1.name, "Player 1")
        self.assertEqual(game.player2.name, "Player 2")
        self.assertEqual(game.round_number, 1)

        # Test with custom names
        custom_game = GameState("Alice", "Bob")
        self.assertEqual(custom_game.player1.name, "Alice")
        self.assertEqual(custom_game.player2.name, "Bob")

    def test_setup_game(self):
        """Test setting up the game with deck distribution"""
        game = GameState()
        game.setup_game(shuffle_deck=False)  # Use ordered deck for predictable testing

        # Both players should have 26 cards
        self.assertEqual(game.player1.total_cards(), 26)
        self.assertEqual(game.player2.total_cards(), 26)

        # Game should not be over initially
        self.assertIsNone(game.check_game_over())

    def test_compare_cards(self):
        """Test card comparison with various scenarios"""
        game = GameState()

        ace = Card(14, Suit.HEARTS)
        king = Card(13, Suit.SPADES)
        queen = Card(12, Suit.HEARTS)
        five_hearts = Card(5, Suit.HEARTS)
        ten_hearts = Card(10, Suit.HEARTS)

        # Basic comparisons
        self.assertEqual(game.compare_cards(ace, king), 1)  # Ace beats King
        self.assertEqual(game.compare_cards(king, ace), 2)  # King loses to Ace
        self.assertEqual(
            game.compare_cards(ace, Card(14, Suit.CLUBS)), 0
        )  # Equal values

        # Suit-up functionality
        result = game.compare_cards(five_hearts, ten_hearts, suit_up_active=True)
        self.assertEqual(result, 3)  # Same suit triggers suit-up

        result = game.compare_cards(five_hearts, king, suit_up_active=True)
        self.assertEqual(result, 2)  # Different suits, normal comparison

        # Battle with advantage functionality
        result = game.compare_cards(king, queen, battle_advantage_active=True)
        self.assertEqual(result, 4)  # King vs Queen triggers battle with advantage

        result = game.compare_cards(queen, king, battle_advantage_active=True)
        self.assertEqual(result, 4)  # Queen vs King also triggers battle with advantage

        # Battle with advantage should not trigger for other combinations
        result = game.compare_cards(king, ace, battle_advantage_active=True)
        self.assertEqual(result, 2)  # King < Ace, normal comparison

    def test_check_game_over(self):
        """Test game over detection"""
        game = GameState()

        # Initially no one should win (both have no cards)
        winner = game.check_game_over()
        self.assertEqual(winner, "Player 2")  # Player 1 checked first, has no cards

        # Give Player 1 some cards
        cards = [Card(5, Suit.HEARTS)]
        game.player1.hand.extend(cards)

        # Now Player 1 should win (Player 2 has no cards)
        winner = game.check_game_over()
        self.assertEqual(winner, "Player 1")

        # Give Player 2 some cards
        game.player2.hand.extend(cards)

        # Now no one should win
        self.assertIsNone(game.check_game_over())

    def test_increment_round(self):
        """Test round number incrementing"""
        game = GameState()
        self.assertEqual(game.round_number, 1)

        game.increment_round()
        self.assertEqual(game.round_number, 2)


class TestGameIntegration(unittest.TestCase):
    """Integration tests for the complete game system"""

    def test_complete_game_cycle(self):
        """Test a complete game setup and basic operations"""
        game = GameState()
        game.setup_game(shuffle_deck=False)  # Predictable deck

        # Both players should have cards
        self.assertTrue(game.player1.has_cards())
        self.assertTrue(game.player2.has_cards())

        # Draw cards from both players
        card1 = game.player1.draw_card()
        card2 = game.player2.draw_card()

        self.assertIsNotNone(card1)
        self.assertIsNotNone(card2)

        # Compare the cards
        result = game.compare_cards(card1, card2)
        self.assertIn(result, [0, 1, 2, 3])  # Valid comparison result

        # Test adding cards to discard
        if result == 1:
            game.player1.add_cards_to_discard([card1, card2])
        elif result == 2:
            game.player2.add_cards_to_discard([card1, card2])

        # Game should continue (players still have cards)
        self.assertIsNone(game.check_game_over())

    def test_deck_completeness(self):
        """Test that setup creates a complete deck"""
        game = GameState()
        game.setup_game(shuffle_deck=False)

        # Should have exactly 52 cards total
        total_cards = game.player1.total_cards() + game.player2.total_cards()
        self.assertEqual(total_cards, 52)

        # Collect all cards to verify completeness
        all_cards = list(game.player1.hand) + list(game.player2.hand)

        # Should have 13 cards of each suit
        for suit in Suit:
            suit_cards = [card for card in all_cards if card.suit == suit]
            self.assertEqual(len(suit_cards), 13)

        # Should have exactly one of each card value/suit combination
        card_strings = [str(card) for card in all_cards]
        self.assertEqual(len(card_strings), len(set(card_strings)))  # No duplicates


class TestBattleWithAdvantage(unittest.TestCase):
    """Test the Battle with Advantage house rule"""

    def setUp(self):
        self.game = GameState()

    def test_is_king_vs_queen(self):
        """Test detection of King vs Queen combinations"""
        king = Card(13, Suit.HEARTS)
        queen = Card(12, Suit.SPADES)
        ace = Card(14, Suit.CLUBS)

        # Should detect King vs Queen
        self.assertTrue(self.game._is_king_vs_queen(king, queen))
        self.assertTrue(self.game._is_king_vs_queen(queen, king))

        # Should not detect other combinations
        self.assertFalse(self.game._is_king_vs_queen(king, ace))
        self.assertFalse(self.game._is_king_vs_queen(queen, ace))

    def test_battle_with_advantage_king_wins_immediately(self):
        """Test battle where King's second card beats Queen's second card"""
        # Setup players with specific cards
        queen_player = Player("Queen Player")
        king_player = Player("King Player")

        # Queen gets: 5 (second card)
        # King gets: 10 (second card) - should win immediately
        queen_player.hand.extend([Card(5, Suit.HEARTS)])
        king_player.hand.extend([Card(10, Suit.SPADES)])

        queen_card = Card(12, Suit.DIAMONDS)
        king_card = Card(13, Suit.CLUBS)

        winner, all_cards = self.game.battle_with_advantage(
            queen_card, king_card, queen_player, king_player
        )

        # King should win (winner = 2)
        self.assertEqual(winner, 2)
        # Should have 4 cards total (original Queen, King, Queen's second, King's second)
        self.assertEqual(len(all_cards), 4)
        self.assertEqual(all_cards[0], queen_card)
        self.assertEqual(all_cards[1], king_card)
        self.assertEqual(str(all_cards[2]), "5h")  # Queen's second
        self.assertEqual(str(all_cards[3]), "10s")  # King's second

    def test_battle_with_advantage_king_wins_with_third_card(self):
        """Test battle where King needs third card to win"""
        queen_player = Player("Queen Player")
        king_player = Player("King Player")

        # Queen gets: 10 (second card)
        # King gets: 5 (second card), then Ace (third card) - should win with third
        queen_player.hand.extend([Card(10, Suit.HEARTS)])
        # Cards are drawn from the top (end), so reverse the order
        king_player.hand.extend([Card(14, Suit.CLUBS), Card(5, Suit.SPADES)])

        queen_card = Card(12, Suit.DIAMONDS)
        king_card = Card(13, Suit.HEARTS)

        winner, all_cards = self.game.battle_with_advantage(
            queen_card, king_card, queen_player, king_player
        )

        # King should win (winner = 2)
        self.assertEqual(winner, 2)
        # Should have 5 cards total
        self.assertEqual(len(all_cards), 5)
        self.assertEqual(str(all_cards[4]), "Ac")  # King's third card

    def test_battle_with_advantage_queen_wins(self):
        """Test battle where Queen wins when King's third card is still lower"""
        queen_player = Player("Queen Player")
        king_player = Player("King Player")

        # Queen gets: 10 (second card)
        # King gets: 5 (second card), then 8 (third card) - Queen should win
        queen_player.hand.extend([Card(10, Suit.HEARTS)])
        # Cards are drawn from the top (end), so reverse the order
        king_player.hand.extend([Card(8, Suit.CLUBS), Card(5, Suit.SPADES)])

        queen_card = Card(12, Suit.DIAMONDS)
        king_card = Card(13, Suit.HEARTS)

        winner, all_cards = self.game.battle_with_advantage(
            queen_card, king_card, queen_player, king_player
        )

        # Queen should win (winner = 1)
        self.assertEqual(winner, 1)
        # Should have 5 cards total
        self.assertEqual(len(all_cards), 5)
        self.assertEqual(str(all_cards[4]), "8c")  # King's third card

    def test_battle_with_advantage_no_cards_left(self):
        """Test battle when a player runs out of cards"""
        queen_player = Player("Queen Player")  # No cards
        king_player = Player("King Player")
        king_player.hand.extend([Card(5, Suit.SPADES)])

        queen_card = Card(12, Suit.DIAMONDS)
        king_card = Card(13, Suit.HEARTS)

        winner, all_cards = self.game.battle_with_advantage(
            queen_card, king_card, queen_player, king_player
        )

        # King should win by default when Queen has no cards
        self.assertEqual(winner, 2)
        self.assertEqual(len(all_cards), 2)  # Only original cards


if __name__ == "__main__":
    unittest.main()
