from .position import Position
class Monster:
    def __init__(self, pos: Position, name: str, phrase: str, hp: int):
        self.pos = pos
        self.name = name
        self.phrase = phrase
        self.hp = hp