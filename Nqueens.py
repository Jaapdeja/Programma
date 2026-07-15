import CNF_encoder
def X(r, c):
    return CNF_encoder.Variable(f"{r},{c}")

def big_and(xs):
    f = xs[0]
    for x in xs[1:]:
        f = CNF_encoder.And(f, x)
    return f

def big_or(xs):
    f = xs[0]
    for x in xs[1:]:
        f = CNF_encoder.Or(f, x)
    return f

def row_constraints(n):
    #Generates clauses for all rows
    clauses = []

    for r in range(n):
        clause = X(r,0)
        #At least one queen on every row
        for c in range(1, n):
            clause = CNF_encoder.Or(clause, X(r, c))
        clauses.append(clause)

        #At most one queen on every row
        for c1 in range(n):
            for c2 in range(c1+1, n):
                clause = CNF_encoder.Or(CNF_encoder.Not(X(r,c1)),CNF_encoder.Not(X(r,c2)))
                clauses.append(clause)
    
    return clauses
def column_constraints(n):
    #Generates clauses for every column
    clauses = []

    for c in range(n):
        clause = X(0,c)
        #At least one queen per column
        for r in range(1, n):
            clause = CNF_encoder.Or(clause, X(r, c))
        clauses.append(clause)

        #At most one queen per column
        for r1 in range(n):
            for r2 in range(r1+1, n):
                clause = CNF_encoder.Or(CNF_encoder.Not(X(r1,c)),CNF_encoder.Not(X(r2,c)))
                clauses.append(clause)
    
    return clauses
def diagonal_constraints(n):
    #Generates all clauses to ensure a maximum of one queen per column
    clauses = []

    for r1 in range(n):
        for c1 in range(n):
            for r2 in range(n):
                for c2 in range(n):
                    if (r1, c1) < (r2, c2):
                        if abs(r1 - r2) == abs(c1 - c2):
                            clause = CNF_encoder.Or(CNF_encoder.Not(X(r1,c1)), CNF_encoder.Not(X(r2, c2)))
                            clauses.append(clause)

    return clauses

def nqueens(n):
    #Returns full nqueens SAT for a certain n
    return(
        row_constraints(n)+
        column_constraints(n)+
        diagonal_constraints(n)
    )

def nqueensimplication(n):
    #N-Queens variant using implication, more intuitive
    constraints = []
    for r in range(n):
        row_vars = [X(r, c) for c in range(n)]
        constraints.append(big_or(row_vars))

        for c in range(n):
            others_empty = [
                CNF_encoder.Not(X(r, c2))
                for c2 in range(n)
                if c2 != c
            ]

            constraints.append(
                CNF_encoder.Implies(X(r,c), big_and(others_empty))
            )
    for c in range(n):
        col_vars = [X(r,c) for r in range(n)]
        constraints.append(big_or(col_vars))

        for r in range(n):
            others_empty = [
                CNF_encoder.Not(X(r2, c))
                for r2 in range(n)
                if r2 != r
            ]

            constraints.append(CNF_encoder.Implies(X(r,c), big_and(others_empty)))

    for r in range(n):
        for c in range(n):
            diagonal_others = []

            for r2 in range(n):
                for c2 in range(n):
                    if (r, c) != (r2, c2):
                        if abs(r - r2) == abs(c - c2):
                            diagonal_others.append(
                                CNF_encoder.Not(X(r2, c2))
                            )

            if diagonal_others:
                constraints.append(
                    CNF_encoder.Implies(
                        X(r, c),
                        big_and(diagonal_others)
                    )
                )

    return big_and(constraints)