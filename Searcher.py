from InputOutput import read_posting_list
from copy import deepcopy


def process_query(query, dictionary, postings_file):
    index = dict()
    with open(postings_file, "r") as pf:
        for op in query:
            if isinstance(op, str):
                index[op] = get_posting_list(op, dictionary, pf)

    return index


def get_posting_list(term, dictionary, postings_file):
    """
    Wrapper for read_posting_list. Returns empty list if the term
    does not exist in the dictionary.
    """
    if term in dictionary:
        return read_posting_list(postings_file, dictionary[term])
    else:
        return []


def wrap_query(query):
    """
    Converts query from postfix form to nested Operator form.
    e.g., [a, b, c, d, 1, 1, 0] -> OR(a, AND(b, c, d))
    """
    stack = []
    print(query)
    for op in query:
        if isinstance(op, str):
            stack.append(op)
        else:
            if op == 2:
                newOperator = Not(stack.pop())
                stack.append(newOperator)
            elif op == 1:
                newOperator = And()
                newOperator.add(stack.pop())
                newOperator.add(stack.pop())
                stack.append(newOperator)
            elif op == 0:
                newOperator = Or()
                newOperator.add(stack.pop())
                newOperator.add(stack.pop())
                stack.append(newOperator)
        print(stack)
    # the size of the stack at the end should be 1; otherwise, our postfix conversion failed
    assert (
        len(stack) == 1
    ), f"Nested Operator conversion failed! Stack size is {len(stack)}"
    return stack[0]


class Operator:
    """
    Parent class for all operators.
    Operands are stored in tuples to avoid this weird memory glitch
    where lists get duplicated.
    As such, list methods like 'append' are replaced with tuple equivalents.
    """

    def __init__(self, operands=tuple()):
        self.operands = operands
        self.type = None

    def add(self, operand, debug=""):
        # we cannot add operands to a NOT operator
        if self.type == 2:
            return

        # if new operand is an operator of the same type (e.g. OR and OR),
        # just add the operator's operands into this operator's operands
        if isinstance(operand, Operator):
            if self.type == operand.type:
                self.operands = (*self.operands, *operand.operands)
            else:
                self.operands = (*self.operands, operand)
        else:
            self.operands = (*self.operands, operand)

    def __repr__(self):
        operator = {0: "OR", 1: "AND", 2: "NOT"}[self.type]
        if self.type == 2:
            return f"{operator}({self.operands})"
        else:
            return f"{operator}({','.join(map(str, self.operands))})"


class Or(Operator):
    def __init__(self, operands=tuple()):
        super().__init__(operands)
        self.type = 0

    def resolve(self):
        pass


class And(Operator):
    def __init__(self, operands=tuple()):
        super().__init__(operands)
        self.type = 1

    def resolve(self):
        # first, recursively optimize all unresolved operands in the operand list
        # self.operands should only contain (term, doc freq) tuples
        self.operands = [
            (operand.resolve() if isinstance(operand, Operator) else operand)
            for operand in self.operands
        ]

        # sort by ascending doc freq order
        self.operands.sort(key=lambda x: x[1])


class Not(Operator):
    def __init__(self, operands=tuple()):
        super().__init__(operands)
        self.type = 2

    def resolve(self):
        pass


print(wrap_query(["bill", "Gates", "vista", "XP", 0, "mac", 2, 1, 1, 0]))
