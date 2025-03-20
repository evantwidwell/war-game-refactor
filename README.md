# Python Engineer Homework

## Premise
Implemented at the start of this assignement is the deterministic card game "war". [(See Game Rules here)](https://cardgames.io/war/)

### General Information
- Don't spend more than 4 hours on this assignment
- Clone this repo and share it with us. **_Do not_** fork it and submit a PR (keep your work between us)

There's also a pre-implemented house rule:
### House Rule 1 | Suit Up
- If the same suit is played, they have a 'two card' war, but cards are played from the bottom of the hand
- If the second card from each player is the same suit again, ignore the values and play 'suit up' again, continuing from the bottom of the deck
- Regular wars always take precedence over suit up, if the two cards are the same suit or not, if the values match, enter a regular war
    - Wars ending in the same suit do not trigger suit-up

This assignment will be judged by your ability to complete two goals:
1. Refactor the game into a more readable and robust format, utilizing more sophisticated coding practices, with automated tests to ensure consistent behavior.
2. Implement an additional 'house rule' into the game.

### Starting Implementation
When the game is run there are a few optional flags
```
  --auto             Prevent request for user action, move game along automatically
  --output [OUTPUT]  Auto play game and output the game results to a log file
  --suit-up          run game with "suit up" house rule
```
Example output
```
...
---- Round 137 ----
P1: H:7  | D:0  | ['5c']
P2: H:5  | D:38 | ['5d']
War!
P1: H:3  | D:0  | ['5c', '9d', 'Kd', '1s', '4s']
P2: H:1  | D:38 | ['5d', 'Qd', '6c', '5s', 'Qh']*
---- Round 138 ----
P1: H:2  | D:0  | ['10s']*
P2: H:0  | D:48 | ['5h']
---- Round 139 ----
P1: H:1  | D:2  | ['9s']*
P2: H:47 | D:0  | ['4s']
---- Round 140 ----
P1: H:0  | D:4  | ['Ks']
P2: H:46 | D:0  | ['1s']*
---- Round 141 ----
P1: H:3  | D:0  | ['4s']
P2: H:45 | D:2  | ['Kd']*
---- Round 142 ----
P1: H:2  | D:0  | ['9s']
P2: H:44 | D:4  | ['9d']
War!
Player 2 Wins in 142 rounds!

```
Some information is displayed that represent the state of the game at each round:
- `P1` / `P2`: Player 1 or Player 2, each players information is displayed on a single row
- `H`: "Hand": how many cards are in the players hand, after the card for the round is placed down.
- `D`: "Discard": The number of cards the player has collected, but not yet picked up into their hand.
    - These cards are only moved to the hand once the player's hand empties and they need to play a card.
- List after the `|`: the cards the player has put down for the round, bottom of the stack to the top from left to right.
    - Card Notation:
        - The Number or letter at the start is the number or facecard value
        - The lowercase letter at the end is the suit
        - Ex: "9s" = "Nine of Spades", "Jh" = "Jack of Hearts"
    - The `*` at the end of the played cards list means that hand wins the current matchup.

## Part 1 - Refactor
While the initial implementation works, it's far from ideal.

Refactor the code into something more readable, robust, and professional, whatever that means to you. We want to know how you think and code.

Write tests for your code, to ensure that the behavior is consistent before and after the refactor.

## Part 2 - Implement Second House Rule

In your re-factored implementation of the base game with the 'suit up' house rule, implement another house rule. Also be sure to have tests to check the new gameplay behavior.

_Only zero or one house rule should be implemented per game_

### House Rule 2 | Battle "with advantage"
- Occurs when a King and Queen are played at the same time
    - The Queen plays one card
    - The King plays one card
        - If it's higher, the King wins all 4 cards
        - If it's lower than the Queen player's new card, they play a second card.
            - If it's still lower, the Queen player wins all 5 cards.
            - If it's higher, the King wins all 5 cards
- Classic 'Wars' do not take effect until the Battle 'with advantage' is complete

## Installation
Clone the git-repo, and utilize python 3.9 or greater. The game is run in the terminal, and no non-standard python packages are used. (you can use any standard or non-standard packages you like, as long as you have proper installation instructions)

## Bonus: Still have time?

If you finish the above and still have time within the given 4 hours, here is a bonus challenge to show off a bit.

**Implement Multiple house rules per game:** The rules are re-defined below to explain the interplay of the rules

### House Rule 1 | Suit Up
- If the same suit is played, they have a 'two card' war, but cards are played from the bottom of the hand
    - If the second card from each player is the same suit again, ignore the values and play 'suit up' again, continuing from the bottom of the deck
- Regular wars always take precedence over suit up, if the two cards are the same suit or not, if the values match, enter a regular war
    - Wars ending in the same suit do not trigger suit-up
- If Rule 2 is in effect, and a king and queen are played, rule 2 takes over but continues to play from the bottom of the hand.
- If the same suit is played while already playing from the bottom of the deck, continue to play from the bottom of the deck.

### House Rule 2 | Battle "with advantage"
- Occurs when a King and Queen are played at the same time
    - The Queen plays one Card
    - The King plays one card
        - if it's lower than the Queen player's new card, they play a second card.
            - If it's still lower, the Queen player wins all 5 cards.
            - If it's higher, the King wins all 5 cards
        - If it's higher, the King wins all 4 cards
- Classic 'Wars' do not take effect until the Battle 'with advantage' is complete
- If rule 1 is in effect, and the king and queen are the same suit, rule 1 is nullified, but the rest of the "Battle with advantage" (rule 2) is played from the bottom of the hand

## Deliverables

We would like you to create your own repo that has the finished homework assignment. Please include documentation on anything we need to know to set it up and any notes you have for the team.

## Questions?
We are happy to answer questions. Just reach out to your recruiter to get in touch.
