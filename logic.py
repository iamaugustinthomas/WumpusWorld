from typing import Set, Dict, List

class Sentence:
    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __invert__(self):
        return Not(self)


class Symbol(Sentence):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name


class Not(Sentence):
    def __init__(self, operand: Sentence):
        self.operand = operand

    def __repr__(self):
        return f"~{self.operand}"

    def __hash__(self):
        return hash(("not", hash(self.operand)))

    def __eq__(self, other):
        return isinstance(other, Not) and self.operand == other.operand


class And(Sentence):
    def __init__(self, *conjuncts: Sentence):
        self.conjuncts = list(conjuncts)

    def __repr__(self):
        return f"({' & '.join(str(c) for c in self.conjuncts)})"


class Or(Sentence):
    def __init__(self, *disjuncts: Sentence):
        self.disjuncts = list(disjuncts)

    def __repr__(self):
        return f"({' | '.join(str(d) for d in self.disjuncts)})"


class Implies(Sentence):
    def __init__(self, antecedent: Sentence, consequent: Sentence):
        self.antecedent = antecedent
        self.consequent = consequent

    def __repr__(self):
        return f"({self.antecedent} => {self.consequent})"


class Iff(Sentence):
    def __init__(self, left: Sentence, right: Sentence):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left} <=> {self.right})"


def evaluate(sentence: Sentence, model: Dict[str, bool]) -> bool:
    if isinstance(sentence, Symbol):
        return model[sentence.name]
    elif isinstance(sentence, Not):
        return not evaluate(sentence.operand, model)
    elif isinstance(sentence, And):
        return all(evaluate(c, model) for c in sentence.conjuncts)
    elif isinstance(sentence, Or):
        return any(evaluate(d, model) for d in sentence.disjuncts)
    elif isinstance(sentence, Implies):
        return not evaluate(sentence.antecedent, model) or evaluate(sentence.consequent, model)
    elif isinstance(sentence, Iff):
        return evaluate(sentence.left, model) == evaluate(sentence.right, model)
    raise ValueError(f"Unknown sentence type: {type(sentence)}")


def get_symbols(sentence: Sentence) -> Set[str]:
    if isinstance(sentence, Symbol):
        return {sentence.name}
    elif isinstance(sentence, Not):
        return get_symbols(sentence.operand)
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


def check_all(kb_sentence: Sentence, query: Sentence, symbols: List[str], model: Dict[str, bool]) -> bool:
    if not symbols:
        if evaluate(kb_sentence, model):
            return evaluate(query, model)
        return True
    
    p = symbols[0]
    rest = symbols[1:]
    
    model[p] = False
    if not check_all(kb_sentence, query, rest, model):
        return False
        
    model[p] = True
    return check_all(kb_sentence, query, rest, model)


def entails(kb: Sentence, query: Sentence) -> bool:
    symbols = list(get_symbols(kb).union(get_symbols(query)))
    return check_all(kb, query, symbols, {})