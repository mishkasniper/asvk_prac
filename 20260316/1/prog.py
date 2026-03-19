from shlex import split
from cowsay import cowsay, list_cows, read_dot_cow
from io import StringIO
import cmd


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
    def __init__(self, pos: Position, name: str, phrase: str, hp: int):
        self.pos = pos
        self.name = name
        self.phrase = phrase
        self.hp = hp

jgsbat = read_dot_cow(StringIO("""
$the_cow = <<EOC;
         $thoughts
          $thoughts
    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\\\\\\\--//|.'-._  (
     )'   .'\/o\/o\/'.   `(
      ) .' . \====/ . '. (
       )  / <<    >> \  (
        '-._/``  ``\_.-'
  jgs     __\\\\\\\\'--'//__
         (((""`  `"")))
EOC
"""))

class MUDcmd(cmd.Cmd):
    intro = "<<< Welcome to Python-MUD 0.1 >>>"
    prompt = "(MUD) "

    def __init__(self):
        super().__init__()
        self.player = Position(0, 0)
        self.monsters = []
        self.here_monster = False

    def check_name(self, name: str) -> bool:
        if name == "jgsbat" or name in list_cows():
            return True
        return False
    
    def encounter(self, x, y):
        self.here_monster = False
        pos = Position(x, y)
        for monster in self.monsters:
            if monster.pos == pos:
                self.here_monster = True
                if monster.name == "jgsbat":
                    print(cowsay(monster.phrase, cowfile=jgsbat))
                else:
                    print(cowsay(monster.phrase, cow=monster.name))

    def do_up(self, arg):
        """Move up. Usage: up"""
        self.player.move(-1, 0)
        print(f"Moved to ({self.player[0]}, {self.player[1]})")
        self.encounter(self.player[0], self.player[1])
    
    def do_down(self, arg):
        """Move down. Usage: down"""
        self.player.move(1, 0)
        print(f"Moved to ({self.player[0]}, {self.player[1]})")
        self.encounter(self.player[0], self.player[1])
    
    def do_left(self, arg):
        """Move left. Usage: left"""
        self.player.move(0, -1)
        print(f"Moved to ({self.player[0]}, {self.player[1]})")
        self.encounter(self.player[0], self.player[1])
    
    def do_right(self, arg):
        """Move right. Usage: right"""
        self.player.move(0, 1)
        print(f"Moved to ({self.player[0]}, {self.player[1]})")
        self.encounter(self.player[0], self.player[1])

    def do_addmon(self, arg: str):
        """
        Create a new monster with given parameters.
        Usage: addmon <monster_name> hello <hello_string> hp <hitpoints> coords <x> <y>
        """
        if not arg:
            print("Invalid arguments")
            return

        try:
            args = split(arg)
        except ValueError:
            print("Invalid arguments")
            return
        
        if len(args) != 8:
            print("Invalid arguments")
            return
        
        name = args[0]
        
        if not self.check_name(name):
            print("Cannot add unknown monster")
            return

        hp = None
        phrase = None
        new_pos = None
        
        i = 1
        while i < len(args):
            if args[i] == "hello":
                if i + 1 >= len(args):
                    print("Invalid arguments")
                    return
                phrase = args[i + 1]
                i += 2
            elif args[i] == "hp":
                if i + 1 >= len(args):
                    print("Invalid arguments")
                    return
                try:
                    hp = int(args[i + 1])
                    if hp <= 0:
                        print("Invalid arguments")
                        return
                except ValueError:
                    print("Invalid arguments")
                    return
                i += 2
            elif args[i] == "coords":
                if i + 2 >= len(args):
                    print("Invalid arguments")
                    return
                try:
                    x = int(args[i + 1])
                    y = int(args[i + 2])
                    if x < 0 or x > 9 or y < 0 or y > 9:
                        print("Invalid arguments")
                        return
                    new_pos = Position(x, y)
                except ValueError:
                    print("Invalid arguments")
                    return
                i += 3
            else:
                print("Invalid arguments")
                return
        
        if hp is None or phrase is None or new_pos is None:
            print("Invalid arguments")
            return
        
        print(f"Added monster {name} to {new_pos} saying {phrase}")
        
        monster_replaced = False
        for i, monster in enumerate(self.monsters):
            if monster.pos == new_pos:
                self.monsters[i] = Monster(new_pos, name, phrase, hp)
                monster_replaced = True
                break
        
        if not monster_replaced:
            self.monsters.append(Monster(new_pos, name, phrase, hp))
        else:
            print("Replaced the old monster")

    def complete_addmon(self, text, line, begidx, endidx):
        """complete for command addmon"""
        args = line[:endidx].split()
        
        if len(args) <= 2:
            cows = list_cows() + ["jgsbat"]
            return [cow for cow in cows if cow.startswith(text)]
        
        elif text in ["hello", "hp", "coords"] or any(arg in ["hello", "hp", "coords"] for arg in args):
    
            keywords = ["hello", "hp", "coords"]
            used_keywords = [arg for arg in args if arg in keywords]
            
            if len(used_keywords) < 3:
                available = [k for k in keywords if k not in used_keywords and k.startswith(text)]
                return available
        
        return []
    
    def do_attack(self, arg):
        """
        Attack monster in your position
        Usage: attack <name_monster> [with <weapon_name>]
        """

        try:
            args = split(arg) if arg else []
        except ValueError:
            print("Invalid arguments")
            return
        
        if len(args) == 0:
            print("Incorrect arguments")
            return
        mon_name = args[0]

        weapons = {
            "sword": 10,
            "spear":15,
            "axe": 20
        }

        if not self.here_monster:
            print(f"No {mon_name} here")
            return

        monster: Monster = None
        monster_id = 0

        for idx, mon in enumerate(self.monsters):
            if mon.pos == self.player:
                if mon.name != mon_name:
                    print(f"No {mon_name} here")
                    return
                monster = mon
                monster_id = idx
                break

        
        if len(args) == 1:
            weapon = "sword"
        elif len(args) == 2:
            if args[1] != "with":
                print("Invalid arguments")
                return
            weapon = args[2]
            if weapon not in weapons:
                print("Unknown weapon")
                return
        else:
            print("Invalid arguments")
            return

        damage = weapons[weapon]

        died = False
        if monster.hp < damage:
            damage = monster.hp
            died = True

        print(f"Attacked {monster.name},  damage {damage} hp")
        
        if died:
            print(f"{monster.name} died")
            self.monsters.pop(monster_id)
        
        else:
            monster.hp -= damage
            print(f"{monster.name} now has {monster.hp}")

        return
    
    def complete_attack(self, text, line, begidx, endidx):
        """complete command attack"""
        monsters_here = []
        for monster in self.monsters:
            if monster.pos == self.player:
                monsters_here.append(monster.name)
                break

        if not monsters_here:
            return []
        
        args = line[:endidx].split()
        
        if len(args) == 1 or len(args) == 2:
            return [name for name in monsters_here if name.startswith(text)]

        return []

    def complete_attack(self, text, line, begidx, endidx):
        """complete command attack"""
        args = line[:endidx].split()

        monsters_here = []
        for monster in self.monsters:
            if monster.pos == self.player:
                monsters_here.append(monster.name)
                break
        
        if len(args) == 1:
            return [name for name in monsters_here if name.startswith(text)]

        if len(args) == 2:
            if "with".startswith(text):
                return ["with"]
            return []
        
        elif len(args) >= 3:
            if args[2] == "with" or (len(args) == 3 and "with".startswith(args[1])):
                weapons = ["sword", "spear", "axe"]
                return [weapon for weapon in weapons if weapon.startswith(text)]
            else:
                return []
        
        return []

    def do_exit(self, arg):
        """Exit the MUD. Usage: exit"""
        print("Goodbye!")
        return True
    
    def do_EOF(self, arg):
        """Handle Ctrl-D"""
        print()
        return self.do_exit(arg)
    
    def default(self, line):
        """Handle unknown commands"""
        print("Invalid command")
    
    def emptyline(self):
        """Do nothing on empty line"""
        pass

def main():
    MUDcmd().cmdloop()
    
if __name__ == "__main__":
    main()