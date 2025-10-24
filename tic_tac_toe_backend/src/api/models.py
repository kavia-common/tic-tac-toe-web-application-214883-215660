from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Player(Base):
    """Represents a player."""
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    games_as_x: Mapped[List["Game"]] = relationship(back_populates="player_x", foreign_keys="Game.player_x_id")
    games_as_o: Mapped[List["Game"]] = relationship(back_populates="player_o", foreign_keys="Game.player_o_id")


class Game(Base):
    """Represents a Tic Tac Toe game."""
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Board is stored as a 9-character string with values in {" ", "X", "O"}
    board: Mapped[str] = mapped_column(String(9), default=" " * 9, nullable=False)

    # next_player: "X" or "O"
    next_player: Mapped[str] = mapped_column(String(1), default="X", nullable=False)

    # status: in_progress | won | draw
    status: Mapped[str] = mapped_column(String(20), default="in_progress", nullable=False)

    # winner: None | "X" | "O"
    winner: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)

    player_x_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"), nullable=True)
    player_o_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"), nullable=True)

    player_x: Mapped[Optional[Player]] = relationship(back_populates="games_as_x", foreign_keys=[player_x_id])
    player_o: Mapped[Optional[Player]] = relationship(back_populates="games_as_o", foreign_keys=[player_o_id])

    moves: Mapped[List["Move"]] = relationship("Move", back_populates="game", cascade="all, delete-orphan", order_by="Move.move_number")

    def get_board_list(self) -> List[str]:
        return list(self.board)

    def set_board_list(self, board_list: List[str]) -> None:
        self.board = "".join(board_list)


class Move(Base):
    """Represents a move in a game."""
    __tablename__ = "moves"
    __table_args__ = (
        UniqueConstraint("game_id", "position", name="uq_game_position"),
        UniqueConstraint("game_id", "move_number", name="uq_game_move_number"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False, index=True)
    player_symbol: Mapped[str] = mapped_column(String(1), nullable=False)  # "X" or "O"
    position: Mapped[int] = mapped_column(Integer, nullable=False)  # 0..8
    move_number: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    game: Mapped[Game] = relationship("Game", back_populates="moves")
