from typing import List, Tuple, Set
from kb import WumpusKB
from world import WumpusEnvironment

class LogicAgent:
    def __init__(self, size: int = 4):
        self.size = size
        self.kb = WumpusKB(size=size)
        self.current_pos = (1, 1)
        self.visited: Set[Tuple[int, int]] = set()
        self.has_gold = False

    def perceive_and_tell(self, percepts: dict):
        x, y = self.current_pos

        if percepts["breeze"]:
            self.kb.tell(self.kb.b(x, y))
        else:
            self.kb.tell(~self.kb.b(x, y))

        if percepts["stench"]:
            self.kb.tell(self.kb.s(x, y))
        else:
            self.kb.tell(~self.kb.s(x, y))

    def choose_next_move(self) -> Tuple[int, int]:
        x, y = self.current_pos
        self.visited.add((x, y))

        adjacent = self.kb.get_adjacent(x, y)
        unvisited_adj = [cell for cell in adjacent if cell not in self.visited]

        for nx, ny in unvisited_adj:
            if self.kb.ask_is_safe(nx, ny):
                return (nx, ny)

        for vx, vy in self.visited:
            for nx, ny in self.kb.get_adjacent(vx, vy):
                if (nx, ny) not in self.visited:
                    if self.kb.ask_is_safe(nx, ny):
                        return (nx, ny)

        return None