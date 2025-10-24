from __future__ import annotations

from typing import List, Optional, Tuple


WINNING_LINES: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


# PUBLIC_INTERFACE
def check_winner(board: List[str]) -> Optional[str]:
    """Return 'X' or 'O' if there is a winner, or None otherwise."""
    for a, b, c in WINNING_LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None


# PUBLIC_INTERFACE
def is_draw(board: List[str]) -> bool:
    """Return True if the board is full and there is no winner."""
    return all(cell != " " for cell in board) and check_winner(board) is None


# PUBLIC_INTERFACE
def validate_move(board: List[str], position: int) -> None:
    """Validate that position is empty and within bounds."""
    if not (0 <= position <= 8):
        raise ValueError("Position must be between 0 and 8")
    if board[position] != " ":
        raise ValueError("Position already occupied")
