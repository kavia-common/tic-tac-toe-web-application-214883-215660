from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import get_db
from .models import Game, Move, Player
from .schemas import (
    GameCreate,
    GameOut,
    GamesListOut,
    MoveCreate,
    MoveOut,
    PlayerCreate,
    PlayerOut,
)
from .services import check_winner, is_draw, validate_move

router = APIRouter(tags=["tic-tac-toe"])


def _player_to_out(p: Optional[Player]) -> Optional[PlayerOut]:
    if not p:
        return None
    return PlayerOut(id=p.id, name=p.name, created_at=p.created_at)


def _move_to_out(m: Move) -> MoveOut:
    return MoveOut(
        move_number=m.move_number, position=m.position, player=m.player_symbol, created_at=m.created_at
    )


def _game_to_out(g: Game) -> GameOut:
    moves = [_move_to_out(m) for m in g.moves]
    return GameOut(
        id=g.id,
        board=list(g.board),
        next_player=g.next_player,  # type: ignore
        status=g.status,  # type: ignore
        winner=g.winner,  # type: ignore
        player_x=_player_to_out(g.player_x),
        player_o=_player_to_out(g.player_o),
        moves=moves,
    )


# PUBLIC_INTERFACE
@router.post(
    "/players",
    response_model=PlayerOut,
    summary="Create player",
    description="Create a new player with a unique name.",
    status_code=status.HTTP_201_CREATED,
)
def create_player(payload: PlayerCreate, db: Session = Depends(get_db)) -> PlayerOut:
    """Create a player if name not taken."""
    existing = db.scalar(select(Player).where(Player.name == payload.name))
    if existing:
        raise HTTPException(status_code=400, detail="Player name already exists")
    player = Player(name=payload.name)
    db.add(player)
    db.commit()
    db.refresh(player)
    return _player_to_out(player)  # type: ignore


# PUBLIC_INTERFACE
@router.post(
    "/games",
    response_model=GameOut,
    summary="Start a new game",
    description="Create a new Tic Tac Toe game with optional player names for X and O.",
    status_code=status.HTTP_201_CREATED,
)
def create_game(payload: GameCreate, db: Session = Depends(get_db)) -> GameOut:
    """Start a new game."""
    player_x = None
    player_o = None
    if payload.player_x_name:
        player_x = db.scalar(select(Player).where(Player.name == payload.player_x_name))
        if not player_x:
            player_x = Player(name=payload.player_x_name)
            db.add(player_x)
            db.flush()
    if payload.player_o_name:
        player_o = db.scalar(select(Player).where(Player.name == payload.player_o_name))
        if not player_o:
            player_o = Player(name=payload.player_o_name)
            db.add(player_o)
            db.flush()

    game = Game(
        board=" " * 9,
        next_player="X",
        status="in_progress",
        winner=None,
        player_x_id=player_x.id if player_x else None,
        player_o_id=player_o.id if player_o else None,
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    return _game_to_out(game)


# PUBLIC_INTERFACE
@router.get(
    "/games/{game_id}",
    response_model=GameOut,
    summary="Get game state",
    description="Fetch the current game state including board, status, next player, and moves.",
)
def get_game(game_id: int, db: Session = Depends(get_db)) -> GameOut:
    """Retrieve game state by ID."""
    game = db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    # load relationships
    _ = game.moves, game.player_x, game.player_o
    return _game_to_out(game)


# PUBLIC_INTERFACE
@router.get(
    "/games",
    response_model=GamesListOut,
    summary="List recent games",
    description="List recent games ordered by creation time descending, limited to 50.",
)
def list_games(db: Session = Depends(get_db)) -> GamesListOut:
    """Return latest games with their states."""
    games: List[Game] = db.scalars(select(Game).order_by(Game.created_at.desc()).limit(50)).all()
    # Eager load relationships for each game
    for g in games:
        _ = g.moves, g.player_x, g.player_o
    return GamesListOut(items=[_game_to_out(g) for g in games])


# PUBLIC_INTERFACE
@router.post(
    "/games/{game_id}/moves",
    response_model=GameOut,
    summary="Submit a move",
    description="Submit a move for the given game. Validates turn order, empty cell, and game status. Updates game state and detects wins/draws.",
)
def submit_move(game_id: int, payload: MoveCreate, db: Session = Depends(get_db)) -> GameOut:
    """Submit a move in the specified game with validations."""
    game = db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game.status != "in_progress":
        raise HTTPException(status_code=400, detail="Game already finished")

    if payload.player != game.next_player:
        raise HTTPException(status_code=400, detail=f"It is {game.next_player}'s turn")

    board = game.get_board_list()

    try:
        validate_move(board, payload.position)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Apply move
    board[payload.position] = payload.player
    game.set_board_list(board)

    move_number = (game.moves[-1].move_number + 1) if game.moves else 1
    move = Move(
        game_id=game.id,
        player_symbol=payload.player,
        position=payload.position,
        move_number=move_number,
    )
    db.add(move)

    # Update next player or finalize game
    winner = check_winner(board)
    if winner:
        game.status = "won"
        game.winner = winner
    elif is_draw(board):
        game.status = "draw"
        game.winner = None
    else:
        game.next_player = "O" if game.next_player == "X" else "X"

    db.add(game)
    db.commit()
    db.refresh(game)
    _ = game.moves, game.player_x, game.player_o
    return _game_to_out(game)
