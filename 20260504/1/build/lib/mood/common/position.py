"""Position class for 10x10 toroidal grid."""


class Position:
    """Represents coordinates on a 10x10 wrap-around map."""

    def __init__(self, x: int, y: int):
        """Initialize position with x and y coordinates."""
        self.x = x
        self.y = y

    def __eq__(self, other):
        """Check equality with another Position object."""
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y

    def __str__(self):
        """Return string representation (x, y)."""
        return f"({self.x}, {self.y})"

    def move(self, dx: int, dy: int) -> None:
        """Move position by dx, dy with wrap-around."""
        self.x = (self.x + dx) % 10
        self.y = (self.y + dy) % 10

    def copy(self):
        """Return a deep copy of this position."""
        return Position(self.x, self.y)

    def __getitem__(self, index):
        """Allow indexing: 0 -> x, 1 -> y."""
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        raise IndexError("Position index out of range")

    def __setitem__(self, index, value):
        """Allow assignment by index."""
        if index == 0:
            self.x = value % 10
        elif index == 1:
            self.y = value % 10
        else:
            raise IndexError("Position index out of range")

    def __iter__(self):
        """Iterate over (x, y)."""
        yield self.x
        yield self.y
