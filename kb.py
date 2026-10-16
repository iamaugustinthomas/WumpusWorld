from typing import List, Tuple
from logic import Symbol, Not, And, Or, Iff, entails, Sentence

class WumpusKB:
    def __init__(self, size: int = 4):
        self.size = size
        self.clauses: List[Sentence] = []
        self.axiomatized_tiles = set()
        
        self.tell(~self.p(1, 1))
        self.tell(~self.w(1, 1))

    def p(self, x, y): return Symbol(f"P_{x}_{y}")
    def w(self, x, y): return Symbol(f"W_{x}_{y}")
    def b(self, x, y): return Symbol(f"B_{x}_{y}")
    def s(self, x, y): return Symbol(f"S_{x}_{y}")

    def get_adjacent(self, x: int, y: int) -> List[Tuple[int, int]]:
        adj = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 1 <= nx <= self.size and 1 <= ny <= self.size:
                adj.append((nx, ny))
        return adj

    def add_tile_axioms(self, x: int, y: int):
        if (x, y) in self.axiomatized_tiles: return
        adj = self.get_adjacent(x, y)
        
        pit_disjuncts = [self.p(ax, ay) for ax, ay in adj]
        self.tell(Iff(self.b(x, y), Or(*pit_disjuncts)))
        
        wumpus_disjuncts = [self.w(ax, ay) for ax, ay in adj]
        self.tell(Iff(self.s(x, y), Or(*wumpus_disjuncts)))
        
        self.axiomatized_tiles.add((x, y))

    def tell(self, sentence: Sentence):
        self.clauses.append(sentence)

    def get_kb_sentence(self) -> Sentence:
        return And(*self.clauses)

    def ask_is_safe(self, x: int, y: int) -> bool:
        kb_conjunction = self.get_kb_sentence()
        no_pit = entails(kb_conjunction, ~self.p(x, y))
        no_wumpus = entails(kb_conjunction, ~self.w(x, y))
        return no_pit and no_wumpus