"""Monster class for MUD game."""
from .position import Position


class Monster:
    """Representation of a monster on the map."""

    def __init__(self, pos: Position, name: str, phrase: str, hp: int):
        """Create a monster at given position with name, greeting phrase and hit points."""
        self.pos = pos
        self.name = name
        self.phrase = phrase
        self.hp = hp
