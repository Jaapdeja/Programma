import CNF_encoder
import sat_solver
from collections import defaultdict
#Converts Nondango instances into Boolean formulas
#Instances of Nondango are declared
Nondango6x6 = [[None, None, 1, None, 1, None],
           [2, 3, 3, 4, 4, None],
           [2, None, 5, None, 5, None],
           [6, 6, None, None, 7, None],
           [None, 8, None, None, 9, None],
           [None, 10, 5, 5, 5, None]
           ]
Nondango10x10 = [
    [1, 1, 1, 2, 2, 2, 3, 3, 4, 5],
    [1, 6, None, 7, 8, None, 9, 9, 4, 5],
    [1, 10, 7, 7, 11, 8, 12, None, 12, 13],
    [14, 10, 15, 15, 11, None, 16, 16, None, 13],
    [17, 17, 18, None, 19, 20, 21, 21, 21, 22],
    [17, 23, 18, 24, 19, 25, None, 26, 26, 22],
    [27, 28, 29, 29, 30, None, 25, 31, 31, 32],
    [27, 28, 33, 33, 30, 34, 35, 35, 36, 32],
    [37, 38, 38, 39, 40, 34, 41, 41, 42, 42],
    [37, 43, 43, 39, 40, 34, 44, 44, 42, 45],
]
Nondango12x12 = [
    [1, 1, 2, 2, 2, None, 3, 4, 5, 5, None, None],
    [None, 6, 6, 2, 7, None, 3, 4, None, 5, None, 8],
    [9, 10, None, 11, 11, None, 12, 13, 13, None, 14, None],
    [15, None, 10, 16, None, None, 12, 17, None, 18, 14, 19],
    [15, 20, 20, 16, 21, 21, None, None, None, None, 18, None],
    [None, 22, 23, 23, None, 24, 25, 17, 26, 27, 27, None],
    [28, 22, None, 29, None, None, 25, 26, 26, 27, 30, 19],
    [None, 31, None, 29, 29, None, 32, 33, None, 33, None, 30],
    [31, 31, 34, None, 35, 35, 36, 37, 37, 33, 30, None],
    [None, 31, None, 38, None, 38, 36, None, 37, 39, 39, 40],
    [41, None, None, 42, 42, 43, 36, 44, None, None, None, 40],
    [None, None, None, 45, None, 43, 43, 46, 46, 46, None, 47],
]
Nondango14x14 = [
    [1, None, 2, None, None, 3, 3, None, 4, 5, None, 6, None, None],
    [1, None, 7, 7, 8, None, None, 9, 4, 5, 10, 6, 11, None],
    [None, 12, None, 13, 8, 14, 14, 9, None, None, 15, 15, 11, 16],
    [None, 12, 17, 13, 18, 18, 19, 9, 20, None, 20, 15, None, 11],
    [21, 21, None, 22, 23, None, 19, None, 24, 24, 24, None, 25, None],
    [26, None, None, 22, None, None, None, 27, 27, 28, 29, 29, 25, None],
    [None, None, 17, 30, None, 31, 27, 32, None, None, 29, 29, 33, 34],
    [35, 36, None, None, 23, 37, None, None, 38, 38, None, 39, 33, 34],
    [None, None, 30, 40, None, 37, 41, 32, None, 42, 42, 43, 43, None],
    [None, 36, 44, 44, 40, 41, None, 45, 46, 47, None, 47, None, 48],
    [49, None, 50, 51, None, 52, None, None, 53, 54, 54, 54, None, 48],
    [49, None, 50, 51, None, None, None, 45, 53, None, 55, None, 56, 56],
    [57, 57, 58, 58, 59, 52, None, 60, None, None, 55, 55, 56, 61],
    [None, 62, 62, 59, 59, 63, None, 64, 64, 65, 66, None, 66, 61],
]
def possible_sequences(rows, cols):
    #all possible secuences of 3 boxes in a row are generated
    sequences = []
    #all possible sequences of three for rows
    for r in range(rows):
        for c in range(cols - 2):
            sequences.append([(r, c), (r, c + 1), (r, c + 2)])
    # all possible sequences of three for columns
    for c in range(cols):
        for r in range(rows -2):
            sequences.append([(r, c), (r + 1, c), (r + 2, c)])
    # all possible sequences of three for diagonals
    for r in range(rows - 2):
        for c in range(cols - 2):
            sequences.append([(r, c), (r + 1, c + 1), (r + 2, c + 2)])
    
    for r in range(rows - 2):
        for c in range(2, cols):
            sequences.append([(r, c), (r + 1, c - 1), (r + 2, c - 2)])
    return sequences

def valid_sequence(game):
    #All possible secuences that are possible in the instance of the game are returned
    #This is done by returning all possible secuences on a board that don not contain None
    rows = len(game)
    columns = len(game[0])

    sequences = []

    for seq in possible_sequences(rows, columns):
        if all(game[r][c] is not None for r, c in seq):
            sequences.append(seq)
    return sequences
def get_var(r, c, varmap):
    #Generate var from position on board
    if (r,c) not in varmap:
        varmap[(r,c)] = len(varmap) + 1
    return varmap[(r,c)]
def one_black(vars):
    #Constraints for only one black circle in a region
    clauses = []
    clauses.append(vars)

    for i in range(len(vars)):
        for j in range(i + 1, len(vars)):
            clauses.append([-vars[i], -vars[j]])

    return clauses
def nondango_sat(game):
    #Complete generation of a SAT instance of Nondango
    varmap = {}
    clauses = []

    regions = defaultdict(list)

    rows = len(game)
    cols = len(game[0])
    #Circles are assigned a region
    for row in range(rows):
        for column in range(cols):
            if game[row][column] is not None:
                var = get_var(row, column, varmap)
                region_number = game[row][column]
                regions[region_number].append(var)
    #Generate clauses for one black per region
    for region_vars in regions.values():
        clauses += one_black(region_vars)
    #Generate clauses for no three consecutive circles with same color
    for sequence in valid_sequence(game):
        a, b, c, = [get_var(r, c, varmap) for r, c in sequence]
        clauses.append([a, b, c])
        clauses.append([-a, -b, -c])
    return clauses, varmap

def print_nondango(game, assignment, varmap):
    #Visualization of Nondango
    rows = len(game)
    cols = len(game[0])
    for r in range(rows):
        line = ""

        for c in range(cols):
            if game[r][c] is None:
                line += ". "

            else:
                var = varmap[(r,c)]
                line += "B " if assignment.get(var, False) else "W "
        print(line)

def X(r, c):
    return CNF_encoder.Variable(f"{r},{c}")


def big_and(xs):
    #Generate a big conjunction
    if len(xs) == 1:
        return xs[0]

    f = xs[0]
    for x in xs[1:]:
        f = CNF_encoder.And(f, x)
    return f


def big_or(xs):
    #Generate a big disjunction
    if len(xs) == 1:
        return xs[0]

    f = xs[0]
    for x in xs[1:]:
        f = CNF_encoder.Or(f, x)
    return f

def exactly_one_black_formula(region_vars):
    constraints = []

    # At least one black in the region
    constraints.append(big_or(region_vars))

    # If one cell is black, all other cells in the region are white
    for i in range(len(region_vars)):
        others_white = [
            CNF_encoder.Not(region_vars[j])
            for j in range(len(region_vars))
            if j != i
        ]

        if others_white:
            constraints.append(
                CNF_encoder.Implies(
                    region_vars[i],
                    big_and(others_white)
                )
            )

    return big_and(constraints)

def nondangoimplication(game):
    constraints = []
    regions = defaultdict(list)

    rows = len(game)
    cols = len(game[0])

    # collect region variables
    for r in range(rows):
        for c in range(cols):
            if game[r][c] is not None:
                regions[game[r][c]].append(X(r, c))

    # exactly one black per region
    for region_vars in regions.values():
        constraints.append(exactly_one_black_formula(region_vars))

    # no three same colour
    for sequence in valid_sequence(game):
        a, b, c = [X(r, c) for r, c in sequence]

        # not all black
        constraints.append(
            CNF_encoder.Implies(
                a,
                CNF_encoder.Or(
                    CNF_encoder.Not(b),
                    CNF_encoder.Not(c)
                )
            )
        )

        # not all white
        constraints.append(
            CNF_encoder.Implies(
                CNF_encoder.Not(a),
                CNF_encoder.Or(b, c)
            )
        )

    return big_and(constraints)