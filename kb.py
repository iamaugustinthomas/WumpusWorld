from typing import List, Tuple
from logic import Symbol, Not, And, Or, Iff, entails, Sentence

class WumpusKB:
    def __init__(self, size: int = 4):
        self.size = size
        self.clauses: List[Sentence] = []
        self._init_rules()

    def p(self, x: int, y: int) -> Symbol:
        return Symbol(f"P_{x}_{y}")

    def w(self, x: int, y: int) -> Symbol:
        return Symbol(f"W_{x}_{y}")

    def b(self, x: int, y: int) -> Symbol:
        return Symbol(f"B_{x}_{y}")

    def s(self, x: int, y: int) -> Symbol:
        return Symbol(f"S_{x}_{y}")

    def get_adjacent(self, x: int, y: int) -> List[Tuple[int, int]]:
        adj = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 1 <= nx <= self.size and 1 <= ny <= self.size:
                adj.append((nx, ny))
        return adj

    def _init_rules(self):
        self.tell(~self.p(1, 1))
        self.tell(~self.w(1, 1))

        for x in range(1, self.size + 1):
            for y in range(1, self.size + 1):
                adj = self.get_adjacent(x, y)
                
                pit_disjuncts = [self.p(ax, ay) for ax, ay in adj]
                self.tell(Iff(self.b(x, y), Or(*pit_disjuncts)))
                
                wumpus_disjuncts = [self.w(ax, ay) for ax, ay in adj]
                self.tell(Iff(self.s(x, y), Or(*wumpus_disjuncts)))

    def tell(self, sentence: Sentence):
        self.clauses.append(sentence)

    def get_kb_sentence(self) -> Sentence:
        return And(*self.clauses)

    def ask_is_safe(self, x: int, y: int) -> bool:
        kb_conjunction = self.get_kb_sentence()
        return entails(kb_conjunction, ~self.p(x, y)) and entails(kb_conjunction, ~self.w(x, y))

    def ask_has_pit(self, x: int, y: int) -> bool:
        return entails(self.get_kb_sentence(), self.p(x, y))

    def ask_has_wumpus(self, x: int, y: int) -> bool:
        return entails(self.get_kb_sentence(), self.w(x, y))