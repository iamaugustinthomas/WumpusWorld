from typing import Tuple, Set

class WumpusEnvironment:
    def __init__(
        self,
        size: int = 4,
        pits: Set[Tuple[int, int]] = None,
        wumpus: Tuple[int, int] = (1, 3),
        gold: Tuple[int, int] = (2, 3),
    ):
        self.size = size
        self.pits = pits if pits is not None else {(3, 1), (3, 3), (4, 4)}
        self.wumpus = wumpus
        self.gold = gold

    def get_percept(self, x: int, y: int) -> dict:
        breeze = any(adj in self.pits for adj in self._get_adjacent(x, y))
        stench = self.wumpus in self._get_adjacent(x, y)
        glitter = (x, y) == self.gold
        
        return {
            "breeze": breeze,
            "stench": stench,
            "glitter": glitter
        }

    def _get_adjacent(self, x: int, y: int):
        adj = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 1 <= nx <= self.size and 1 <= ny <= self.size:
                adj.append((nx, ny))
        return adj