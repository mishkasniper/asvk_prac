from cowsay import cowsay

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

class Monster:
    def __init__(self, pos: Position, phrase: str):
        self.pos = pos
        self.phrase = phrase

commands = ["up", "down", "left", "right", "addmon"]
player = Position(0, 0)
monsters = []

def move(direction: str) -> None:
    global player

    directions = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1)
    }

    dx, dy = directions[direction]
    player.move(dx, dy)

    print(f"Moved to ({player[0]}, {player[1]})")

    for monster in monsters:
        if monster.pos == player:
            encounter(player[0], player[1])
    return
    
def encounter(x, y):
    pos = Position(x, y)
    for monster in monsters:
        if monster.pos == pos:
            print(cowsay(monster.phrase))

def get_and_make_command():
    try:
        command_line = input()
    except EOFError:
        exit(0)

    if not command_line.strip():
        return

    command = command_line.split()
    if command[0] not in commands:
        print("Invalid command")
        return
    
    if command[0] != "addmon":
        move(command[0])
        return
    
    if len(command) != 4:
        print("Invalid arguments")
        return
    
    if not command[1].isdigit() or not command[2].isdigit():
        print("Invalid arguments")
        return
    
    x = int(command[1])
    y = int(command[2])

    if x > 9 or y > 9:
        print("Invalid arguments")
        return

    phrase = command[3]
    new_pos = Position(x, y)

    print(f"Added monster to {new_pos} saying {phrase}")

    monster_replaced = False
    for i, monster in enumerate(monsters):
        if monster.pos == new_pos:
            monsters[i] = Monster(new_pos, phrase)
            monster_replaced = True
            break
    
    if not monster_replaced:
        monsters.append(Monster(new_pos, phrase))
    else:
        print("Replaced the old monster")
    
def main():
    
    while True:
        get_and_make_command()
    
if __name__ == "__main__":
    main()