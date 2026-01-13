#!/usr/bin/env python3
"""
Quick demo of CFR training on a small poker game.

This script demonstrates CFR training on Leduc poker, which is faster to train
than full Texas Hold'em. Use this to verify the installation and see results quickly.
"""

from pokertrees import *
from pokerstrategy import *
from pokercfr import *
from pokergames import *
import time

def print_strategy_table(strategy, max_rows=20):
    """Print a formatted strategy table."""
    print(f"\n{'Infoset':<25} {'Fold %':>10} {'Call %':>10} {'Raise %':>10}")
    print("-" * 60)

    count = 0
    for infoset in sorted(strategy.policy.keys()):
        if count >= max_rows:
            print(f"... ({len(strategy.policy) - max_rows} more infosets)")
            break

        probs = strategy.policy[infoset]
        fold_pct = probs[FOLD] * 100
        call_pct = probs[CALL] * 100
        raise_pct = probs[RAISE] * 100

        print(f"{infoset:<25} {fold_pct:>9.1f}% {call_pct:>9.1f}% {raise_pct:>9.1f}%")
        count += 1

def demo_leduc(iterations=1000):
    """
    Run CFR on Leduc poker and display results.

    Leduc poker is a simple poker variant with:
    - 2 players
    - 6 card deck (3 ranks, 2 suits: JJ, QQ, KK)
    - 1 hole card per player
    - 2 rounds: preflop and flop (1 board card)
    """
    print("\n" + "="*80)
    print("LEDUC POKER CFR TRAINING DEMO")
    print("="*80)

    print("\nGame: Leduc Poker")
    print("- 2 players")
    print("- 6 cards: J♠, J♥, Q♠, Q♥, K♠, K♥")
    print("- Each player gets 1 hole card")
    print("- 1 community card dealt on the flop")
    print("- 2 betting rounds")

    # Create Leduc rules
    print("\n[1/3] Setting up Leduc poker...")
    rules = leduc_rules()

    # Use PublicChanceSamplingCFR for faster training
    print("\n[2/3] Running Public Chance Sampling CFR...")
    cfr = PublicChanceSamplingCFR(rules)

    print(f"Information sets: {len(cfr.tree.information_sets)}")
    print(f"Training for {iterations} iterations...")

    start_time = time.time()

    # Train with progress updates
    for i in range(iterations):
        cfr.cfr()
        cfr.iterations += 1

        if (i + 1) % max(1, iterations // 10) == 0:
            progress = (i + 1) / iterations * 100
            elapsed = time.time() - start_time
            print(f"  Progress: {i+1}/{iterations} ({progress:.0f}%) - {elapsed:.1f}s elapsed")

    total_time = time.time() - start_time
    print(f"\nTraining complete in {total_time:.2f} seconds!")
    print(f"Average: {total_time/iterations*1000:.2f}ms per iteration")

    # Display results
    print("\n[3/3] Results:")
    print("="*80)

    # Calculate exploitability
    try:
        br_profile, br_values = cfr.profile.best_response()
        exploitability = sum(br_values)
        print(f"\nExploitability: {exploitability:.6f}")
        print("(Lower is better - perfect Nash equilibrium = 0)")
    except Exception as e:
        print(f"\nCould not calculate exploitability: {e}")

    # Show strategy for player 0
    print("\n" + "="*80)
    print("PLAYER 0 EQUILIBRIUM STRATEGY")
    print("="*80)
    print_strategy_table(cfr.profile.strategies[0], max_rows=15)

    # Show strategy for player 1
    print("\n" + "="*80)
    print("PLAYER 1 EQUILIBRIUM STRATEGY")
    print("="*80)
    print_strategy_table(cfr.profile.strategies[1], max_rows=15)

    # Save strategies
    print("\n" + "="*80)
    print("Saving strategies to files...")
    cfr.profile.strategies[0].save_to_file("leduc_strategy_p0.txt")
    cfr.profile.strategies[1].save_to_file("leduc_strategy_p1.txt")
    print("✓ Saved: leduc_strategy_p0.txt")
    print("✓ Saved: leduc_strategy_p1.txt")

    return cfr

def demo_kuhn(iterations=1000):
    """
    Run CFR on Kuhn poker - the simplest poker game.

    Kuhn poker:
    - 2 players
    - 3 cards: Jack, Queen, King
    - 1 card per player
    - 1 betting round
    """
    print("\n" + "="*80)
    print("KUHN POKER CFR TRAINING DEMO")
    print("="*80)

    print("\nGame: Kuhn Poker")
    print("- 2 players")
    print("- 3 cards: J, Q, K")
    print("- Each player gets 1 card")
    print("- 1 betting round")
    print("- Simplest possible poker game!")

    print("\n[1/3] Setting up Kuhn poker...")
    rules = kuhn_rules()

    print("\n[2/3] Running vanilla CFR...")
    cfr = CounterfactualRegretMinimizer(rules)

    print(f"Information sets: {len(cfr.tree.information_sets)}")
    print(f"Training for {iterations} iterations...")

    start_time = time.time()
    cfr.run(iterations)
    total_time = time.time() - start_time

    print(f"Training complete in {total_time:.2f} seconds!")

    print("\n[3/3] Results:")
    print("="*80)

    # For Kuhn poker, we can calculate exact Nash equilibrium exploitability
    try:
        br_profile, br_values = cfr.profile.best_response()
        exploitability = sum(br_values)
        print(f"\nExploitability: {exploitability:.6f}")
        print("(Kuhn poker Nash equilibrium should have exploitability ≈ 0)")
    except Exception as e:
        print(f"Could not calculate exploitability: {e}")

    # Display strategies
    print("\n" + "="*80)
    print("NASH EQUILIBRIUM STRATEGIES")
    print("="*80)

    for player in range(2):
        print(f"\nPlayer {player}:")
        print_strategy_table(cfr.profile.strategies[player])

    return cfr

if __name__ == "__main__":
    import sys

    print("\n" + "="*80)
    print("PYCFR TRAINING DEMO")
    print("="*80)
    print("\nThis demo shows CFR training on small poker games.")
    print("Choose a game to train:\n")
    print("1. Kuhn Poker (fastest, ~3 info sets)")
    print("2. Leduc Poker (moderate, ~30 info sets)")
    print("3. Both games\n")

    choice = input("Enter choice (1-3): ").strip()

    if choice == '1':
        demo_kuhn(iterations=10000)
    elif choice == '2':
        demo_leduc(iterations=5000)
    elif choice == '3':
        print("\n" + "="*80)
        print("Running both demos...")
        print("="*80)
        demo_kuhn(iterations=10000)
        print("\n\n")
        demo_leduc(iterations=5000)
    else:
        print("Invalid choice. Running Kuhn poker demo by default...")
        demo_kuhn(iterations=10000)

    print("\n" + "="*80)
    print("DEMO COMPLETE!")
    print("="*80)
    print("\nTo train on larger games:")
    print("  python train_holdem.py [iterations] [algorithm]")
    print("\nExample:")
    print("  python train_holdem.py 10000 chance")
