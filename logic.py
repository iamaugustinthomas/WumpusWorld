from typing import Set, Dict, List

class Sentence:
    def __and__(self, other): return And(self, other)
    def __or__(self, other): return Or(self, other)
    def __invert__(self): return Not(self)

class Symbol(Sentence):
    def __init__(self, name: str): self.name = name
    def __repr__(self): return self.name
    def __hash__(self): return hash(self.name)
    def __eq__(self, other): return isinstance(other, Symbol) and self.name == other.name

class Not(Sentence):
    def __init__(self, operand: Sentence): self.operand = operand
    def __repr__(self): return f"~{self.operand}"
    def __hash__(self): return hash(("not", hash(self.operand)))
    def __eq__(self, other): return isinstance(other, Not) and self.operand == other.operand

class And(Sentence):
    def __init__(self, *conjuncts: Sentence): self.conjuncts = list(conjuncts)
    def __repr__(self): return f"({' & '.join(str(c) for c in self.conjuncts)})"

class Or(Sentence):
    def __init__(self, *disjuncts: Sentence): self.disjuncts = list(disjuncts)
    def __repr__(self): return f"({' | '.join(str(d) for d in self.disjuncts)})"

class Implies(Sentence):
    def __init__(self, antecedent: Sentence, consequent: Sentence):
        self.antecedent = antecedent
        self.consequent = consequent
    def __repr__(self): return f"({self.antecedent} => {self.consequent})"

class Iff(Sentence):
    def __init__(self, left: Sentence, right: Sentence):
        self.left = left
        self.right = right
    def __repr__(self): return f"({self.left} <=> {self.right})"

def get_symbols(sentence: Sentence) -> Set[str]:
    if isinstance(sentence, Symbol): return {sentence.name}
    elif isinstance(sentence, Not): return get_symbols(sentence.operand)
    elif isinstance(sentence, (And, Or)):
        symbols = set()
        for child in (sentence.conjuncts if isinstance(sentence, And) else sentence.disjuncts):
            symbols.update(get_symbols(child))
        return symbols
    elif isinstance(sentence, (Implies, Iff)):
        left = sentence.antecedent if isinstance(sentence, Implies) else sentence.left
        right = sentence.consequent if isinstance(sentence, Implies) else sentence.right
        return get_symbols(left).union(get_symbols(right))
    return set()

def evaluate_partial(sentence: Sentence, model: Dict[str, bool]):
    if isinstance(sentence, Symbol): return model.get(sentence.name, None)
    elif isinstance(sentence, Not):
        val = evaluate_partial(sentence.operand, model)
        return not val if val is not None else None
    elif isinstance(sentence, And):
        has_none = False
        for c in sentence.conjuncts:
            val = evaluate_partial(c, model)
            if val is False: return False
            if val is None: has_none = True
        return None if has_none else True
    elif isinstance(sentence, Or):
        has_none = False
        for d in sentence.disjuncts:
            val = evaluate_partial(d, model)
            if val is True: return True
            if val is None: has_none = True
        return None if has_none else False
    elif isinstance(sentence, Iff):
        val_a = evaluate_partial(sentence.left, model)
        val_b = evaluate_partial(sentence.right, model)
        if val_a is not None and val_b is not None: return val_a == val_b
        return None

def check_all(kb_sentence: Sentence, query: Sentence, symbols: List[str], model: Dict[str, bool]) -> bool:
    kb_val = evaluate_partial(kb_sentence, model)
    if kb_val is False: return True
    if not symbols: return bool(evaluate_partial(query, model))
    
    p = symbols[0]
    rest = symbols[1:]
    
    model[p] = False
    if not check_all(kb_sentence, query, rest, model):
        del model[p]
        return False
        
    model[p] = True
    if not check_all(kb_sentence, query, rest, model):
        del model[p]
        return False
        
    del model[p]
    return True

def entails(kb: Sentence, query: Sentence) -> bool:
    if not kb.conjuncts: return False
    symbols = list(get_symbols(kb).union(get_symbols(query)))
    return check_all(kb, query, symbols, {})