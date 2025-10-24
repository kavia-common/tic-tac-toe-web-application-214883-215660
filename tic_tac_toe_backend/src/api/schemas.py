from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, model_validator


Symbol = Literal["X", "O"]
GameStatus = Literal["in_progress", "won", "draw"]


class PlayerCreate(BaseModel):
    name: str = Field(..., description="Unique display name of the player", min_length=1, max_length=100)


class PlayerOut(BaseModel):
    id: int = Field(..., description="Player ID")
    name: str = Field(..., description="Player name")
    created_at: datetime = Field(..., description="Creation timestamp")


class GameCreate(BaseModel):
    player_x_name: Optional[str] = Field(None, description="Optional player X name; will be created if not exists.")
    player_o_name: Optional[str] = Field(None, description="Optional player O name; will be created if not exists.")


class MoveCreate(BaseModel):
    position: int = Field(..., description="Board position 0..8", ge=0, le=8)
    player: Symbol = Field(..., description="Symbol of the player making the move ('X' or 'O')")

    @model_validator(mode="after")
    def validate_consistency(self):
        if self.player not in ("X", "O"):
            raise ValueError("player must be 'X' or 'O'")
        return self


class MoveOut(BaseModel):
    move_number: int = Field(..., description="Sequential move number starting at 1")
    position: int = Field(..., description="Board position 0..8")
    player: Symbol = Field(..., description="Player symbol")
    created_at: datetime = Field(..., description="Timestamp when the move was recorded")


class GameOut(BaseModel):
    id: int = Field(..., description="Game ID")
    board: List[str] = Field(..., description="Board as 9-length list with values ' ', 'X', or 'O'")
    next_player: Symbol = Field(..., description="Next player to move, 'X' or 'O'")
    status: GameStatus = Field(..., description="Game status: in_progress, won, or draw")
    winner: Optional[Symbol] = Field(None, description="Winner symbol if status == 'won'")
    player_x: Optional[PlayerOut] = Field(None, description="Player X details, if assigned")
    player_o: Optional[PlayerOut] = Field(None, description="Player O details, if assigned")
    moves: List[MoveOut] = Field(..., description="Chronological move history")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "board": [" ", "X", " ", " ", "O", " ", " ", " ", " "],
                "next_player": "X",
                "status": "in_progress",
                "winner": None,
                "player_x": {"id": 1, "name": "Alice", "created_at": "2025-01-01T00:00:00Z"},
                "player_o": {"id": 2, "name": "Bob", "created_at": "2025-01-01T00:00:00Z"},
                "moves": [
                    {"move_number": 1, "position": 1, "player": "X", "created_at": "2025-01-01T00:00:00Z"}
                ],
            }
        }


class GamesListOut(BaseModel):
    items: List[GameOut] = Field(..., description="List of recent games")
