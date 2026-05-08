# Checkers CLI Game

A command-line Checkers (Draughts) game implementing standard rules with an 8x8 board.

## Features

- 8x8 board with 12 pieces per player
- Alternating turns between Red and White
- Move notation input (e.g., `23-18`, `11 to 15`)
- Capture mechanics with multi-jump support
- Kinging: pieces reaching the opposite end become kings
- Kings can move diagonally in any direction
- Win condition: eliminate all opponent pieces or block all moves

## Installation

No external dependencies required. Uses Python 3 standard library only.

```bash
# Clone or copy checkers.py to your desired location
```

## Usage

```bash
python checkers.py
```

### Move Notation

Enter moves in the format `X-Y` or `X to Y` where X and Y are square numbers:

```
Enter move (e.g., '3-7') or 'q' to quit: 23-18
```

### Quit

Enter `q` to quit the game.

## Game Rules

1. **Board Setup**: Red pieces at squares 21-32 (rows 5-7), White pieces at squares 1-12 (rows 0-2)
2. **Movement**: Pieces move diagonally forward one square
3. **Captures**: Jump over adjacent opponent piece to land on empty square beyond
4. **Multi-jump**: Must continue capturing if another capture is available
5. **Kinging**: Reaching row 0 (for Red) or row 7 (for White) promotes to king
6. **King Movement**: Kings can move diagonally in any direction

## Testing

Run the comprehensive test suite:

```bash
python -c "from checkers import *; run_all_tests()"
```

## File Structure

- `checkers.py`: Main game implementation with standalone functions
