# CFR Training Guide

This guide explains how to use the training scripts to find Nash equilibrium strategies for poker games.

## Quick Start

### 1. Demo Script (Recommended for Testing)

Run the interactive demo to see CFR in action on small games:

```bash
python demo_training.py
```

This will let you choose between:
- **Kuhn Poker**: Simplest game, trains in seconds
- **Leduc Poker**: Small but interesting game, trains in under a minute
- **Both**: Run both demos sequentially

### 2. Simplified Poker Training

Train on a Royal Poker variant (simplified multi-round poker):

**Important:** This is NOT full Texas Hold'em. It uses 1 hole card (not 2) and an 8-card deck to make training tractable. Full Hold'em with 52 cards would require days/weeks of training and extensive optimization.

```bash
# Basic usage (1000 iterations with chance sampling)
python train_holdem.py

# Specify iterations
python train_holdem.py 5000

# Specify algorithm
python train_holdem.py 5000 chance

# Full syntax
python train_holdem.py [iterations] [algorithm]
```

**Game details:**
- 8 cards (J, Q, K, A in 2 suits)
- 1 hole card per player
- 3 betting rounds (preflop, flop, turn)
- ~8,600 information sets

**Available algorithms:**
- `chance` - Public Chance Sampling CFR (default, fastest)
- `outcome` - Outcome Sampling CFR (memory efficient)
- `vanilla` - Vanilla CFR (slowest but most accurate)

## Understanding the Output

### Strategy Tables

Each strategy is displayed as a table showing the probability of each action (Fold, Call, Raise) for each information set:

```
Infoset                   Fold %    Call %   Raise %
------------------------------------------------------------
Ks:/c                      0.0%    67.3%    32.7%
Ah:/r                     15.2%     0.0%    84.8%
```

**Information Set Format:**
- `Ks` - Hole cards (King of spades)
- `:` - Separator
- `/c` - Betting history (/ = new round, c = call, r = raise, f = fold)

### Exploitability

The exploitability metric measures how far from Nash equilibrium your strategy is:
- **0.000** = Perfect Nash equilibrium
- **< 0.01** = Very good approximation
- **< 0.1** = Reasonable approximation
- **> 1.0** = Needs more training

Lower exploitability means a better strategy that's harder to exploit.

## Output Files

After training, strategies are saved to text files:

```
poker_strategy_p0.txt     # Player 0 strategy (from train_holdem.py)
poker_strategy_p1.txt     # Player 1 strategy (from train_holdem.py)
leduc_strategy_p0.txt     # Player 0 strategy (from demo)
leduc_strategy_p1.txt     # Player 1 strategy (from demo)
```

Each file contains the complete strategy in a format that can be loaded later:

```
Ks:/c 0.327 0.673 0.000
Ah:/r 0.848 0.000 0.152
```

Format: `<infoset> <raise_prob> <call_prob> <fold_prob>`

## Loading Saved Strategies

To use a trained strategy in your own code:

```python
from pokerstrategy import Strategy
from pokergames import leduc_rules

# Load a strategy
strategy = Strategy(0)
strategy.load_from_file('leduc_strategy_p0.txt')

# Use it to make decisions
infoset = "K:/c"
probs = strategy.probs(infoset)
action = strategy.sample_action(infoset)
```

## Customizing Training

### Modify Game Rules

Edit `train_holdem.py` to customize the game:

```python
def create_holdem_rules():
    # Change deck size
    ranks = [Card.RANK_JACK, Card.RANK_QUEEN,
             Card.RANK_KING, Card.RANK_ACE]
    suits = [1, 2]  # Add more suits: [1, 2, 3, 4]

    # Change betting structure
    rounds = [
        RoundInfo(holecards=2, boardcards=0,
                  betsize=2, maxbets=[2, 2]),  # Preflop
        # Add/modify rounds...
    ]
```

### Adjust Training Parameters

```python
# More iterations = better convergence
train_holdem(iterations=10000)

# Different algorithms have tradeoffs:
# - vanilla: Slowest but most accurate
# - chance: Fast, good for most games
# - outcome: Memory efficient, good for large games
train_holdem(iterations=5000, algorithm='outcome')
```

## Performance Tips

1. **Start small**: Use demo_training.py to verify everything works
2. **Increase gradually**: Start with 1,000 iterations, then 10,000, then more
3. **Use chance sampling**: Fastest algorithm for most games
4. **Limit deck size**: Smaller decks train much faster
5. **Monitor exploitability**: Stop when it's low enough for your needs

## Game Size Reference

| Game | Deck Size | Information Sets | Training Time* |
|------|-----------|------------------|----------------|
| Kuhn Poker | 3 cards | ~3 | Seconds |
| Leduc Poker | 6 cards | ~30 | 1-2 minutes |
| Royal Poker (train_holdem.py) | 8 cards | ~8,600 | 10-30 minutes |
| Full Hold'em | 52 cards | Millions+ | Days/Weeks** |

*Approximate times for 10,000 iterations using chance sampling CFR
**Not supported by this library - would require extensive optimization

## Troubleshooting

### "Out of memory" error
- Use outcome sampling: `python train_holdem.py 1000 outcome`
- Reduce deck size in `create_holdem_rules()`
- Reduce number of betting rounds

### Training is too slow
- Use chance sampling instead of vanilla CFR
- Reduce iterations for initial testing
- Simplify the game (fewer cards, fewer rounds)

### Exploitability not decreasing
- Train for more iterations
- Check if game is set up correctly
- Some games may need 100,000+ iterations to converge

## Further Reading

For more information about CFR and poker AI:
- Original CFR paper: Zinkevich et al. (2008)
- See README.md for full references
- Check test/ directory for more examples

## Need Help?

- Check README.md for API documentation
- Review test cases in test/ directory
- Examine pokergames.py for game setup examples
