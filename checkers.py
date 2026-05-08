#!/usr/bin/env python3
"""Checkers (Draughts) game - command line implementation."""

import re
import sys


BOARD_SIZE = 8
EMPTY = 0
RED = 1
WHITE = 2
RED_KING = 3
WHITE_KING = 4


def init_board():
    """Initialize the 8x8 board with pieces in starting positions."""
    board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    
    # Place Red pieces on dark squares (rows 5-7, odd columns in even rows, even columns in odd rows)
    # Red moves upward (row decreases)
    for row in range(5, 8):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 1:
                board[row][col] = RED
    
    # Place White pieces on dark squares (rows 0-2, odd columns in even rows, even columns in odd rows)
    # White moves downward (row increases)
    for row in range(3):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 1:
                board[row][col] = WHITE
    
    return board


def square_to_coords(square):
    """Convert square number (1-32) to (row, col) coordinates for dark squares."""
    if square < 1 or square > 32:
        return None, None
    # Count only dark squares - map linear index to actual board position
    count = 0
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 1:
                count += 1
                if count == square:
                    return row, col
    return None, None


def coords_to_square(row, col):
    """Convert (row, col) coordinates to square number (1-32) for dark squares."""
    if row < 0 or row >= BOARD_SIZE or col < 0 or col >= BOARD_SIZE:
        return None
    if (row + col) % 2 == 0:
        return None  # Not a dark square
    # Count dark squares to find this position's index
    count = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if (r + c) % 2 == 1:
                count += 1
                if r == row and c == col:
                    return count
    return None


def get_dark_squares():
    """Return list of all dark square numbers (1-64)."""
    squares = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 1:
                squares.append(coords_to_square(row, col))
    return squares


def is_dark_square(row, col):
    """Check if a position is a dark square."""
    return (row + col) % 2 == 1


def get_piece_symbol(piece):
    """Return the symbol for a piece."""
    if piece == RED:
        return "⚫"
    elif piece == WHITE:
        return "⚪"
    elif piece == RED_KING:
        return "♔"
    elif piece == WHITE_KING:
        return "♕"
    return " "


def print_board(board):
    """Print the board with square numbers and pieces."""
    print("   a b c d e f g h")
    
    for row in range(BOARD_SIZE):
        row_num = BOARD_SIZE - row
        line = f"{row_num}  "
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            symbol = get_piece_symbol(piece)
            line += symbol
            if col < BOARD_SIZE - 1:
                line += " "
        print(line)
    print()


def print_board_with_squares(board):
    """Print the board with square numbers for move input."""
    print("   1 2 3 4 5 6 7 8")
    
    for row in range(BOARD_SIZE):
        row_num = BOARD_SIZE - row
        line = f"{row_num}  "
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            symbol = get_piece_symbol(piece)
            line += symbol
            if col < BOARD_SIZE - 1:
                line += " "
        print(line)
    print("   1 2 3 4 5 6 7 8")
    print()


def is_valid_move(board, from_row, from_col, to_row, to_col, player):
    """Check if a move is valid for the given player."""
    if not (0 <= from_row < BOARD_SIZE and 0 <= from_col < BOARD_SIZE):
        return False, "Invalid starting position"
    
    if not (0 <= to_row < BOARD_SIZE and 0 <= to_col < BOARD_SIZE):
        return False, "Invalid ending position"
    
    piece = board[from_row][from_col]
    
    # Must have a piece at starting position
    if piece == EMPTY:
        return False, "No piece at starting position"
    
    # Must be player's piece
    if player == RED and piece not in (RED, RED_KING):
        return False, "Not your piece"
    if player == WHITE and piece not in (WHITE, WHITE_KING):
        return False, "Not your piece"
    
    # Destination must be empty
    if board[to_row][to_col] != EMPTY:
        return False, "Destination is occupied"
    
    # Check if destination is a dark square
    if not is_dark_square(to_row, to_col):
        return False, "Must move to a dark square"
    
    row_diff = to_row - from_row
    col_diff = to_col - from_col
    
    # Regular move: one diagonal square forward
    if abs(row_diff) == 1 and abs(col_diff) == 1:
        # Check direction for non-kings
        if piece == RED and row_diff > 0:
            return False, "Red pieces move upward (negative row direction)"
        if piece == WHITE and row_diff < 0:
            return False, "White pieces move downward (positive row direction)"
        return True, ""
    
    # Capture move: jump over opponent piece
    if abs(row_diff) == 2 and abs(col_diff) == 2:
        mid_row = (from_row + to_row) // 2
        mid_col = (from_col + to_col) // 2
        mid_piece = board[mid_row][mid_col]
        
        if mid_piece == EMPTY:
            return False, "No piece to capture"
        
        # Check if middle piece is opponent's
        if player == RED and mid_piece not in (WHITE, WHITE_KING):
            return False, "Cannot capture your own piece"
        if player == WHITE and mid_piece not in (RED, RED_KING):
            return False, "Cannot capture your own piece"
        
        # Check direction for non-kings
        if piece == RED and row_diff > 0:
            return False, "Red pieces move upward (negative row direction)"
        if piece == WHITE and row_diff < 0:
            return False, "White pieces move downward (positive row direction)"
        
        return True, "capture"
    
    return False, "Invalid move"


def get_all_valid_moves(board, player):
    """Get all valid moves for a player."""
    moves = []
    
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            
            if player == RED and piece not in (RED, RED_KING):
                continue
            if player == WHITE and piece not in (WHITE, WHITE_KING):
                continue
            
            # Check all possible destinations (only diagonal moves)
            for dr in [-2, -1, 1, 2]:
                for dc in [-2, -1, 1, 2]:
                    if abs(dr) == abs(dc):  # diagonal moves only
                        to_row = row + dr
                        to_col = col + dc
                        valid, result = is_valid_move(board, row, col, to_row, to_col, player)
                        if valid:
                            moves.append({
                                'from': coords_to_square(row, col),
                                'to': coords_to_square(to_row, to_col),
                                'capture': result == 'capture',
                                'from_row': row,
                                'from_col': col,
                                'to_row': to_row,
                                'to_col': to_col
                            })
    
    return moves


def get_capturing_moves(board, player):
    """Get all capturing moves for a player."""
    all_moves = get_all_valid_moves(board, player)
    return [m for m in all_moves if m['capture']]


def execute_move(board, move):
    """Execute a move and return the modified board."""
    new_board = [row[:] for row in board]  # Deep copy
    
    from_row = move['from_row']
    from_col = move['from_col']
    to_row = move['to_row']
    to_col = move['to_col']
    
    piece = new_board[from_row][from_col]
    new_board[from_row][from_col] = EMPTY
    new_board[to_row][to_col] = piece
    
    # Remove captured piece if it's a capture move
    if move['capture']:
        mid_row = (from_row + to_row) // 2
        mid_col = (from_col + to_col) // 2
        new_board[mid_row][mid_col] = EMPTY
    
    # King promotion
    if piece == RED and to_row == 0:
        new_board[to_row][to_col] = RED_KING
    elif piece == WHITE and to_row == BOARD_SIZE - 1:
        new_board[to_row][to_col] = WHITE_KING
    
    return new_board


def can_continue_jumping(board, row, col, piece):
    """Check if a piece can continue jumping after a capture."""
    directions = []
    
    if piece in (RED, RED_KING):
        directions.append((-1, -1))
        directions.append((-1, 1))
    if piece in (WHITE, WHITE_KING):
        directions.append((1, -1))
        directions.append((1, 1))
    
    if piece in (RED_KING, WHITE_KING):
        directions.append((1, -1))
        directions.append((1, 1))
        if piece == RED_KING:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        if piece == WHITE_KING:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    
    # Re-determine directions based on piece type
    directions = []
    if piece == RED_KING:
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    elif piece == WHITE_KING:
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    elif piece == RED:
        directions = [(-1, -1), (-1, 1)]
    elif piece == WHITE:
        directions = [(1, -1), (1, 1)]
    
    for dr, dc in directions:
        jump_row = row + 2 * dr
        jump_col = col + 2 * dc
        mid_row = row + dr
        mid_col = col + dc
        
        if 0 <= jump_row < BOARD_SIZE and 0 <= jump_col < BOARD_SIZE:
            if board[jump_row][jump_col] == EMPTY:
                mid_piece = board[mid_row][mid_col]
                if mid_piece != EMPTY:
                    if piece == RED and mid_piece in (WHITE, WHITE_KING):
                        return True
                    if piece == WHITE and mid_piece in (RED, RED_KING):
                        return True
                    if piece in (RED_KING, WHITE_KING):
                        if mid_piece in (RED, RED_KING, WHITE, WHITE_KING) and mid_piece != piece:
                            return True
    
    return False


def count_pieces(board, player):
    """Count pieces for a player."""
    count = 0
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if player == RED and piece in (RED, RED_KING):
                count += 1
            elif player == WHITE and piece in (WHITE, WHITE_KING):
                count += 1
    return count


def get_available_moves_count(board, player):
    """Get count of available moves for a player."""
    return len(get_all_valid_moves(board, player))


def parse_move_input(move_str, player):
    """Parse move input string and return from/to squares."""
    move_str = move_str.strip()
    
    # Match pattern like "3-7" or "3 to 7"
    match = re.match(r'^(\d+)\s*[-to]\s*(\d+)$', move_str, re.IGNORECASE)
    if not match:
        return None, "Invalid format. Use 'X-Y' or 'X to Y' where X and Y are square numbers."
    
    from_square = int(match.group(1))
    to_square = int(match.group(2))
    
    if from_square < 1 or from_square > 64:
        return None, "Starting square must be between 1 and 64"
    if to_square < 1 or to_square > 64:
        return None, "Ending square must be between 1 and 64"
    
    return from_square, to_square


def play_game():
    """Main game loop."""
    print("=" * 50)
    print("       CHECKERS (DRAUGHTS)")
    print("=" * 50)
    print()
    print("Game Rules:")
    print("  - Red vs White")
    print("  - Pieces move diagonally forward")
    print("  - Captures are made by jumping over opponent pieces")
    print("  - Multi-jumps are allowed")
    print("  - Pieces become Kings at opposite end")
    print("  - Enter moves as '3-7' (from square 3 to square 7)")
    print("  - Enter 'q' to quit")
    print()
    
    board = init_board()
    current_player = RED
    consecutive_non_captures = 0
    last_move = None
    
    while True:
        print_board_with_squares(board)
        
        # Check win conditions
        red_count = count_pieces(board, RED)
        white_count = count_pieces(board, WHITE)
        
        if red_count == 0:
            print("=" * 50)
            print("WHITE WINS!")
            print("=" * 50)
            return
        if white_count == 0:
            print("=" * 50)
            print("RED WINS!")
            print("=" * 50)
            return
        
        current_moves = get_all_valid_moves(board, current_player)
        if not current_moves:
            opponent = WHITE if current_player == RED else RED
            print("=" * 50)
            print(f"{opponent.name if hasattr(opponent, 'name') else ('WHITE' if current_player == RED else 'RED')} WINS!")
            print(f"{current_player.name if hasattr(current_player, 'name') else ('WHITE' if current_player == RED else 'RED')} has no valid moves!")
            print("=" * 50)
            return
        
        print(f"Red pieces: {red_count} | White pieces: {white_count}")
        print(f"Current turn: {'RED' if current_player == RED else 'WHITE'}")
        if last_move:
            print(f"Last move: {last_move}")
        print()
        
        # Get player input
        while True:
            move_str = input("Enter move (e.g., '3-7') or 'q' to quit: ").strip()
            
            if move_str.lower() == 'q':
                print("Game quit!")
                return
            
            from_square, to_square = parse_move_input(move_str, current_player)
            if from_square is None:
                print(f"Error: {to_square}")
                continue
            
            from_row, from_col = square_to_coords(from_square)
            to_row, to_col = square_to_coords(to_square)
            
            # Check for forced captures
            capturing_moves = get_capturing_moves(board, current_player)
            if capturing_moves:
                # Must make a capturing move if available
                is_capture = False
                for move in capturing_moves:
                    if move['from_row'] == from_row and move['from_col'] == from_col:
                        is_capture = True
                        break
                
                if not is_capture:
                    print("You must capture! Available captures:")
                    for move in capturing_moves:
                        print(f"  {move['from']}-{move['to']}")
                    continue
            
            valid, result = is_valid_move(board, from_row, from_col, to_row, to_col, current_player)
            
            if valid:
                if result == 'capture':
                    # Check if this is a multi-jump situation
                    new_board = execute_move(board, {
                        'from_row': from_row, 'from_col': from_col,
                        'to_row': to_row, 'to_col': to_col,
                        'capture': True
                    })
                    
                    # Check if the piece can continue jumping
                    piece = new_board[to_row][to_col]
                    if can_continue_jumping(new_board, to_row, to_col, piece):
                        print(f"Capture successful! You can continue jumping from square {to_square}.")
                        print_board_with_squares(new_board)
                        
                        # Continue multi-jump sequence
                        board = new_board
                        while can_continue_jumping(board, to_row, to_col, piece):
                            print(f"Multi-jump: {current_player.name if hasattr(current_player, 'name') else ('WHITE' if current_player == RED else 'RED')} from {to_square}")
                            
                            # Get next jump input
                            while True:
                                jump_input = input("Enter jump (e.g., '7-11') or 'pass' to end turn: ").strip()
                                
                                if jump_input.lower() == 'pass':
                                    print("Ending turn without completing multi-jump.")
                                    # Note: this violates standard rules, but for simplicity
                                    break
                                
                                jump_from, jump_to = parse_move_input(jump_input, current_player)
                                if jump_from is None:
                                    print(f"Error: {jump_to}")
                                    continue
                                
                                jr, jc = square_to_coords(jump_from)
                                tr, tc = square_to_coords(jump_to)
                                
                                # Validate the jump
                                if jr != to_row or jc != to_col:
                                    print(f"Must jump from square {to_square}, not {jump_from}")
                                    continue
                                
                                jump_valid, jump_result = is_valid_move(board, jr, jc, tr, tc, current_player)
                                if not jump_valid or not jump_result == 'capture':
                                    print("Invalid jump move")
                                    continue
                                
                                # Execute the jump
                                new_board = execute_move(board, {
                                    'from_row': jr, 'from_col': jc,
                                    'to_row': tr, 'to_col': tc,
                                    'capture': True
                                })
                                board = new_board
                                to_row, to_col = tr, tc
                                piece = board[to_row][to_col]
                                
                                print_board_with_squares(board)
                                
                                if not can_continue_jumping(board, to_row, to_col, piece):
                                    break
                            break
                        break
                    else:
                        board = new_board
                        break
                else:
                    board = execute_move(board, {
                        'from_row': from_row, 'from_col': from_col,
                        'to_row': to_row, 'to_col': to_col,
                        'capture': False
                    })
                    break
            else:
                print(f"Invalid move: {result}")
        
        if last_move is None:
            last_move = f"{from_square}-{to_square}"
        else:
            last_move = f"{from_square}-{to_square}"
        
        # Switch player
        current_player = WHITE if current_player == RED else RED
    
    print_board_with_squares(board)


def run_all_tests():
    """Run comprehensive tests to verify game functionality."""
    passed = 0
    failed = 0
    
    # Test 1: Board initialization
    try:
        board = init_board()
        assert count_pieces(board, RED) == 12
        assert count_pieces(board, WHITE) == 12
        print("Test 1: PASSED - Board initialization")
        passed += 1
    except Exception as e:
        print(f"Test 1: FAILED - {e}")
        failed += 1
    
    # Test 2: Basic move validation (Red moving up)
    try:
        board = init_board()
        r23, c23 = square_to_coords(23)
        r18, c18 = square_to_coords(18)
        valid, _ = is_valid_move(board, r23, c23, r18, c18, RED)
        assert valid
        print("Test 2: PASSED - Basic move validation")
        passed += 1
    except Exception as e:
        print(f"Test 2: FAILED - {e}")
        failed += 1
    
    # Test 3: Capture validation - Red 24 captures White 19 to land at 15
    try:
        board = init_board()
        r24, c24 = square_to_coords(24)
        r19, c19 = square_to_coords(19)
        r15, c15 = square_to_coords(15)
        
        board[r15][c15] = EMPTY
        board[r19][c19] = WHITE
        
        valid, result = is_valid_move(board, r24, c24, r15, c15, RED)
        assert valid and result == 'capture', f"Expected valid capture, got {valid} and {result}"
        print("Test 3: PASSED - Capture validation")
        passed += 1
    except Exception as e:
        print(f"Test 3: FAILED - {e}")
        failed += 1
    
    # Test 4: Kinging
    try:
        board = init_board()
        squares = [24, 20, 16, 12, 8, 4]
        for i in range(len(squares)-1):
            fr, fc = square_to_coords(squares[i])
            tr, tc = square_to_coords(squares[i+1])
            board = execute_move(board, {'from_row': fr, 'from_col': fc, 'to_row': tr, 'to_col': tc, 'capture': False})
        
        r4, c4 = square_to_coords(4)
        assert board[r4][c4] == RED_KING
        print("Test 4: PASSED - Kinging")
        passed += 1
    except Exception as e:
        print(f"Test 4: FAILED - {e}")
        failed += 1
    
    # Test 5: Win condition
    try:
        board = init_board()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] in (WHITE, WHITE_KING):
                    board[r][c] = EMPTY
        
        red_count = count_pieces(board, RED)
        white_count = count_pieces(board, WHITE)
        winner = RED if white_count == 0 else (WHITE if red_count == 0 else None)
        assert winner == RED
        print("Test 5: PASSED - Win condition")
        passed += 1
    except Exception as e:
        print(f"Test 5: FAILED - {e}")
        failed += 1
    
    # Test 6: Invalid move rejection
    try:
        board = init_board()
        r21, c21 = square_to_coords(21)
        r22, c22 = square_to_coords(22)
        valid, _ = is_valid_move(board, r21, c21, r22, c22, RED)
        assert not valid
        print("Test 6: PASSED - Invalid move rejection")
        passed += 1
    except Exception as e:
        print(f"Test 6: FAILED - {e}")
        failed += 1
    
    # Test 7: King backward movement
    try:
        board = init_board()
        squares = [24, 20, 16, 12, 8, 4]
        for i in range(len(squares)-1):
            fr, fc = square_to_coords(squares[i])
            tr, tc = square_to_coords(squares[i+1])
            board = execute_move(board, {'from_row': fr, 'from_col': fc, 'to_row': tr, 'to_col': tc, 'capture': False})
        
        r4, c4 = square_to_coords(4)
        r8, c8 = square_to_coords(8)
        valid, _ = is_valid_move(board, r4, c4, r8, c8, RED_KING)
        assert valid
        print("Test 7: PASSED - King backward movement")
        passed += 1
    except Exception as e:
        print(f"Test 7: FAILED - {e}")
        failed += 1
    
    print(f"\n{'='*40}")
    print(f"Total: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_all_tests()
    else:
        play_game()
