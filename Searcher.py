from InputOutput import read_posting_list


def process_query(query, dictionary, postings_file):
    """
    Generates an in-memory index, containing only terms found in the query.
    Converts the query into a nested operator form (see below).
    Then, uses the generated index to resolve the query starting from the outermost operator.
    """
    index = dict()
    with open(postings_file, "r") as pf:
        for op in query:
            if isinstance(op, tuple):
                term, _ = op
                if term in dictionary:
                    index[term] = read_posting_list(pf, dictionary[term])
                else:
                    index[term] = []

    wrapped = wrap_query(query)
    print(wrapped)
    print(index)

    # if it is an operator, call resolve on the outermost operator
    # to recursively resolve all inner operators
    if isinstance(wrapped, Operator):
        print("Single operator! Resolving...")
        return wrapped.resolve(index)

    # otherwise, it will be a (term, doc freq) tuple
    # just return the posting list
    else:
        term, _ = wrapped
        return index[term]


def wrap_query(query):
    """
    Converts query from postfix form to nested Operator form.
    e.g., [a, b, c, d, 1, 1, 0] -> OR(a, AND(b, c, d))
    """
    stack = []
    for op in query:
        if isinstance(op, tuple):
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

    def resolve(self, index):
        """
        Resolves the operands stored in the current operator using the given index.
        Returns a posting list.
        """
        # first, recursively optimize all unresolved operands in the operand list
        # self.operands should only contain (term, doc freq) tuples
        self.operands = [
            (operand.resolve(index) if isinstance(operand, Operator) else operand)
            for operand in self.operands
        ]
        # at this point, self.operands only contains either term-freq tuples or posting lists

        posting_lists = []
        for op in self.operands:
            # if op is a (term, doc freq) tuple, convert it to a posting list
            if isinstance(op, tuple):
                term, _ = op
                posting_lists.append(index[term])
            # otherwise, it is a posting list and we append it directly
            else:
                posting_lists.append(op)

        final_list = posting_lists[0]
        for next_list in posting_lists[1:]:
            final_list = self.union(final_list, next_list)
        return final_list

    def union(self, list1, list2):
        return list(set([*list1, *list2]))


class And(Operator):
    def __init__(self, operands=tuple()):
        super().__init__(operands)
        self.type = 1

    def resolve(self, index):
        """
        Resolves the operands stored in the current operator using the given index.
        Returns a posting list.
        """
        # first, recursively optimize all unresolved operands in the operand list
        # self.operands should only contain (term, doc freq) tuples
        self.operands = [
            (operand.resolve(index) if isinstance(operand, Operator) else operand)
            for operand in self.operands
        ]
        # at this point, self.operands only contains either term-freq tuples or posting lists

        # sort by ascending doc freq order
        self.operands.sort(key=lambda x: x[1] if isinstance(x, tuple) else len(x))

        posting_lists = []
        for op in self.operands:
            # if op is a (term, doc freq) tuple, convert it to a posting list
            if isinstance(op, tuple):
                term, _ = op
                posting_lists.append(index[term])
            # otherwise, it is a posting list and we append it directly
            else:
                posting_lists.append(op)

        # if there is only one posting list, return it
        if len(posting_lists) == 1:
            return posting_lists[0]

        final_list = posting_lists[0]
        for next_list in posting_lists[1:]:
            final_list = self.intersect(final_list, next_list)
        return final_list

    def intersect(self, list1, list2):
        # TODO: implement this shit
        return list(set(list1) & set(list2))


class Not(Operator):
    def __init__(self, operands=tuple()):
        super().__init__(operands)
        self.type = 2

    def resolve(self, index):
        # TODO: implement this shit
        pass
