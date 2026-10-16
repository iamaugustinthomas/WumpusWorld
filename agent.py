from typing import Set, Tuple
from collections import deque
from kb import WumpusKB

class LogicAgent:
    def __init__(self, size: int = 4):
        self.size = size
        self.kb = WumpusKB(size=size)
        self.current_pos = (1, 1)
        self.visited: Set[Tuple[int, int]] = set()
        self.has_gold = False

    def perceive_and_tell(self, percepts: dict):
        x, y = self.current_pos
        self.visited.add((x, y))
        
        self.kb.add_tile_axioms(x, y)

        if percepts["breeze"]: self.kb.tell(self.kb.b(x, y))
        else: self.kb.tell(~self.kb.b(x, y))

        if percepts["stench"]: self.kb.tell(self.kb.s(x, y))
        else: self.kb.tell(~self.kb.s(x, y))

    def choose_next_move(self) -> Tuple[int, int]:
        """Exploration phase: find unvisited safe tiles."""
        x, y = self.current_pos
        adjacent = self.kb.get_adjacent(x, y)
        for nx, ny in adjacent:
            if (nx, ny) not in self.visited and self.kb.ask_is_safe(nx, ny):
                return (nx, ny)

        for vx, vy in self.visited:
            for nx, ny in self.kb.get_adjacent(vx, vy):
                if (nx, ny) not in self.visited and self.kb.ask_is_safe(nx, ny):
                    return (nx, ny)

        return None

    def choose_return_move(self) -> Tuple[int, int]:
        """Escape phase: BFS pathfinding exclusively through visited tiles to reach (1,1)."""
        queue = deque([(self.current_pos, [])])
        seen = {self.current_pos}
        
        while queue:
            curr, path = queue.popleft()
            
            # If we reached the start, return the very first step of the path that gets us there
            if curr == (1, 1):
                return path[0] if path else (1, 1)
                
            for nx, ny in self.kb.get_adjacent(curr[0], curr[1]):
                if (nx, ny) in self.visited and (nx, ny) not in seen:
                    seen.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
                    
        return None