class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def move(self, dx: int, dy: int) -> None:
        self.x = (self.x + dx) % 10
        self.y = (self.y + dy) % 10
    
    def copy(self):
        return Position(self.x, self.y)
    
    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Position index out of range")
        
    def __setitem__(self, index, value):
        if index == 0:
            self.x = value % 10
        elif index == 1:
            self.y = value % 10
        else:
            raise IndexError("Position index out of range")
    
    def __iter__(self):
        yield self.x
        yield self.y