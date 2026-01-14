#!/usr/bin/env python3
"""
Texas Hold'em Poker CFR Training Script

This script trains a Nash equilibrium strategy for heads-up Texas Hold'em poker
using Counterfactual Regret Minimization (CFR) and outputs strategy tables.
"""

from pokertrees import *
from pokerstrategy import *
from pokercfr import *
from card import Card
import sys
import time

def create_holdem_rules():
    """
    Create a simplified heads-up poker game rules.
    Uses a limited deck and simplified rules for faster training.

    This is a Royal Poker variant - similar to Texas Hold'em but:
    - Only 1 hole card per player (instead of 2)
    - Smaller deck (8 cards: J, Q, K, A in 2 suits)
    - 3 rounds: preflop, flop (1 card), turn (1 card)

    For full Texas Hold'em, you'd need a 52-card deck and days of training.
    """
    # Create a limited deck for feasible training time
    # Using high cards only: J, Q, K, A in two suits
    ranks = [Card.RANK_JACK, Card.RANK_QUEEN, Card.RANK_KING, Card.RANK_ACE]
    suits = [1, 2]  # Spades and Hearts only

    deck = [Card(rank, suit) for rank in ranks for suit in suits]

    print(f"Deck size: {len(deck)} cards")
    print("Cards:", [str(card) for card in deck])

    # Game parameters
    players = 2
    ante = 1
    blinds = None  # Simplified - use ante instead of blinds

    # Simplified round structure
    # Note: 1 hole card (not 2) makes the game tractable
    rounds = [
        RoundInfo(holecards=1, boardcards=0, betsize=2, maxbets=[2, 2]),  # Preflop
        RoundInfo(holecards=0, boardcards=1, betsize=4, maxbets=[2, 2]),  # Flop
        RoundInfo(holecards=0, boardcards=1, betsize=4, maxbets=[2, 2]),  # Turn
    ]

    # Use Royal poker evaluation (from pokergames.py)
    from pokergames import royal_eval, royal_format

    rules = GameRules(
        players=players,
        deck=deck,
        rounds=rounds,
        ante=ante,
        blinds=blinds,
        handeval=royal_eval,
        infoset_format=royal_format
    )

    return rules

def print_strategy_summary(strategy, player_num, round_name, max_infosets=50):
    """
    Print a summary of the strategy for a given player and round.
    """
    print(f"\n{'='*80}")
    print(f"Player {player_num} Strategy - {round_name}")
    print(f"{'='*80}")
    print(f"{'Infoset':<40} {'Fold %':>10} {'Call %':>10} {'Raise %':>10}")
    print("-" * 80)

    # Filter infosets by round (based on bet history structure)
    round_filters = {
        'Preflop': lambda x: x.count('/') == 1,
        'Flop': lambda x: x.count('/') == 2,
        'Turn': lambda x: x.count('/') == 3,
        'River': lambda x: x.count('/') == 4
    }

    filter_func = round_filters.get(round_name, lambda x: True)

    # Sort infosets for consistent output
    sorted_infosets = sorted(strategy.policy.keys())
    filtered_infosets = [info for info in sorted_infosets if filter_func(info)]

    count = 0
    for infoset in filtered_infosets:
        if count >= max_infosets:
            print(f"... ({len(filtered_infosets) - max_infosets} more infosets)")
            break

        probs = strategy.policy[infoset]
        fold_pct = probs[FOLD] * 100
        call_pct = probs[CALL] * 100
        raise_pct = probs[RAISE] * 100

        # Truncate long infosets
        display_infoset = infoset[:37] + "..." if len(infoset) > 40 else infoset

        print(f"{display_infoset:<40} {fold_pct:>9.1f}% {call_pct:>9.1f}% {raise_pct:>9.1f}%")
        count += 1

    print("-" * 80)

def print_detailed_strategy(cfr_trainer, output_file=None):
    """
    Print detailed strategy tables for all rounds and both players.
    """
    output = []

    header = f"\n{'='*80}\n"
    header += "TEXAS HOLD'EM NASH EQUILIBRIUM STRATEGY\n"
    header += f"Trained for {cfr_trainer.iterations} iterations\n"
    header += f"{'='*80}\n"

    print(header)
    if output_file:
        output.append(header)

    rounds = ['Preflop', 'Flop', 'Turn', 'River']

    for player in range(cfr_trainer.rules.players):
        strategy = cfr_trainer.profile.strategies[player]

        player_header = f"\n\n### PLAYER {player} ###\n"
        print(player_header)
        if output_file:
            output.append(player_header)

        for round_name in rounds:
            # Capture stdout for this round
            print_strategy_summary(strategy, player, round_name, max_infosets=30)

def train_holdem(iterations=1000, algorithm='vanilla'):
    """
    Train a simplified poker strategy using CFR.

    Args:
        iterations: Number of CFR iterations to run
        algorithm: 'vanilla', 'chance', or 'outcome' for different CFR variants
    """
    print("\n" + "="*80)
    print("SIMPLIFIED POKER - CFR TRAINING")
    print("(Royal Poker variant - 1 hole card, 8-card deck)")
    print("="*80)

    # Create game rules
    print("\n[1/4] Setting up game rules...")
    rules = create_holdem_rules()

    # Initialize CFR trainer
    print("\n[2/4] Initializing CFR trainer...")
    if algorithm == 'vanilla':
        trainer = CounterfactualRegretMinimizer(rules)
    elif algorithm == 'chance':
        trainer = PublicChanceSamplingCFR(rules)
    elif algorithm == 'outcome':
        trainer = OutcomeSamplingCFR(rules)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    print(f"Algorithm: {algorithm.upper()} CFR")
    print(f"Information sets: {len(trainer.tree.information_sets)}")

    # Train
    print(f"\n[3/4] Training for {iterations} iterations...")
    start_time = time.time()

    for i in range(iterations):
        trainer.cfr()
        trainer.iterations += 1

        if (i + 1) % max(1, iterations // 10) == 0:
            elapsed = time.time() - start_time
            progress = (i + 1) / iterations * 100
            print(f"  Iteration {i+1}/{iterations} ({progress:.1f}%) - Elapsed: {elapsed:.2f}s")

    total_time = time.time() - start_time
    print(f"\nTraining complete! Total time: {total_time:.2f}s")
    print(f"Average time per iteration: {total_time/iterations:.4f}s")

    # Print results
    print("\n[4/4] Generating strategy tables...")
    print_detailed_strategy(trainer)

    # Calculate expected values
    print("\n" + "="*80)
    print("GAME ANALYSIS")
    print("="*80)

    try:
        ev = trainer.profile.expected_value()
        print(f"\nExpected value for Player 0: {ev[0]:.4f}")
        print(f"Expected value for Player 1: {ev[1]:.4f}")
        print(f"Sum (should be ~0 for Nash equilibrium): {sum(ev):.6f}")
    except Exception as e:
        print(f"\nNote: Could not calculate expected value: {e}")

    # Save strategies to files
    print("\n" + "="*80)
    print("SAVING STRATEGIES")
    print("="*80)

    for player in range(rules.players):
        filename = f"poker_strategy_p{player}.txt"
        trainer.profile.strategies[player].save_to_file(filename)
        print(f"Player {player} strategy saved to: {filename}")

    return trainer

def main():
    """Main entry point for the training script."""
    # Parse command line arguments
    iterations = 1000
    algorithm = 'chance'  # Default to chance sampling (faster)

    if len(sys.argv) > 1:
        try:
            iterations = int(sys.argv[1])
        except ValueError:
            print(f"Invalid iteration count: {sys.argv[1]}")
            sys.exit(1)

    if len(sys.argv) > 2:
        algorithm = sys.argv[2].lower()
        if algorithm not in ['vanilla', 'chance', 'outcome']:
            print(f"Invalid algorithm: {algorithm}")
            print("Valid options: vanilla, chance, outcome")
            sys.exit(1)

    # Run training
    trainer = train_holdem(iterations=iterations, algorithm=algorithm)

    print("\n" + "="*80)
    print("TRAINING COMPLETE")
    print("="*80)
    print("\nYou can now use the saved strategy files or continue training by")
    print("loading them with Strategy.load_from_file()")
    print("\nUsage: python train_holdem.py [iterations] [algorithm]")
    print("  iterations: Number of CFR iterations (default: 1000)")
    print("  algorithm: vanilla, chance, or outcome (default: chance)")

if __name__ == "__main__":
    main()
