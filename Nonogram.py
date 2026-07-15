import sat_solver
import time
import CNF_encoder as C
#Converts Nonogram instance to SAT

column = [
    [3, 1],
    [5],
    [1],
    [1, 3],
    [3]
]

Row = [
    [2, 2],
    [2, 1],
    [2, 2],
    [3],
    [2, 1]
]


def all_patterns(length, clue):
    #Generates all possible pattern that can be made on a column or row of a length with a certain clue
    if clue == []:
        return [[0] * length]

    patterns = []
    first_block = clue[0]
    rest_clue = clue[1:]

    min_rest = sum(rest_clue) + max(0, len(rest_clue) - 1)
    max_start = length - first_block - min_rest

    for start in range(max_start + 1):
        begin = [0] * start
        block = [1] * first_block

        if rest_clue:
            rest_length = length - start - first_block - 1
            for rest in all_patterns(rest_length, rest_clue):
                patterns.append(begin + block + [0] + rest)
        else:
            end = [0] * (length - start - first_block)
            patterns.append(begin + block + end)

    return patterns


def big_and(formulas):
    f = formulas[0]
    for x in formulas[1:]:
        f = C.And(f, x)
    return f


def big_or(formulas):
    f = formulas[0]
    for x in formulas[1:]:
        f = C.Or(f, x)
    return f


def X(r, c):
    return C.Variable(f"{r},{c}")


def pattern_formula(cells, pattern):
    #Generate big conjunction of variables and negations in a pattern
    literals = []

    for cell, value in zip(cells, pattern):
        if value == 1:
            literals.append(cell)
        else:
            literals.append(C.Not(cell))

    return big_and(literals)


def line_formula(cells, clue):
    #Generate all possible patterns of a cell, return disjunction of all possible patterns
    patterns = all_patterns(len(cells), clue)

    pattern_formulas = [
        pattern_formula(cells, pattern)
        for pattern in patterns
    ]

    return big_or(pattern_formulas)


def build_nonogram_formula(row_clues, column_clues):
    #Builds the complete Nonogram formula with all clues
    rows = len(row_clues)
    cols = len(column_clues)

    constraints = []

    # Row constraints
    for r, clue in enumerate(row_clues):
        cells = [X(r, c) for c in range(cols)]
        constraints.append(line_formula(cells, clue))

    # Column constraints
    for c, clue in enumerate(column_clues):
        cells = [X(r, c) for r in range(rows)]
        constraints.append(line_formula(cells, clue))

    return big_and(constraints)


