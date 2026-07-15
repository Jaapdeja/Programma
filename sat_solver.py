import CNF_encoder
def resolution(clauses):
    for watchedclause in clauses:
        result = resolvent(watchedclause, clauses)
        if result == "UNSAT":
            return "UNSAT"



def resolvent(watchedclause, clauses):
    for clause in clauses:
        for literal in clause:
            if -literal in watchedclause:
                remove = {literal, -literal}
                merged = [x for x in watchedclause + clause if x not in remove]
                if merged not in clauses:
                    clauses.append(merged)
                if merged == []:
                    return "UNSAT"

def unitpropogate(clauses, assignment, stats= None):
    # performs unit propagation on a CNF formula
    # return simplified formula and updated assignment, None if a conflict is found
    difference = True
    while difference:
        difference = False

        for clause in clauses:
            if len(clause) == 1:
                lit = clause[0]
                var = abs(lit)
                value = lit > 0

                if var in assignment:
                    if assignment[var] != value:
                        return None, assignment
                    
                else:
                    assignment[var] = value
                    if stats is not None:
                        stats["propagations"]+=1
                    difference = True

        clauses = simplify(clauses, assignment)

        if clauses is None:
            return None, assignment
    return clauses, assignment

def simplify(clauses, assignment):
    #Simplifies a CNF formula given a partial variable assignment
    new_clauses = []

    for clause in clauses:
        new_clause = []
        clause_satisfied = False
        for lit in clause:
            value = litevaluation(lit, assignment)

            if value is True:
                clause_satisfied = True
                break
            elif value is None:
                new_clause.append(lit)
        if clause_satisfied:
            continue

        if len(new_clause) == 0:
            return None
        new_clauses.append(new_clause)
    return new_clauses


def litevaluation(lit, assignment):
    #Determines the truth value of a literal under current assignment
    var = abs(lit)
    if var not in assignment:
        return None
    value = assignment[var]
    if lit > 0:
        return value
    else:
        return not value

clauses = [[1, 2], [-1]]
assignment = {}

def dpll(clauses, assignment = None, stats = None):
    #Recursive application of the DPLL SAT solver algorithm
    #First unit propagation is applied, if the formula is not solved an unassigned variable is selected and both possible truth assignments are explored
    #When a branch results in a conflict the solver backtracks one step and explores the alternative assignment
    #Statistics for decisions, conflicts, propagations, and nodes are collected
    if assignment is None:
        assignment = {}
    if stats is None:
        stats = {
            "decisions": 0,
            "conflicts": 0,
            "propagations": 0,
            "nodes": 0
        }
    stats["nodes"]+=1

    clauses, assignment = unitpropogate(clauses, assignment, stats)

    if clauses is None:
        stats["conflicts"]+=1
        return False, None, stats
    if len(clauses) == 0:
        return True, assignment, stats
    
    var = variable_assignment(clauses, assignment)

    for value in [True, False]:
        stats["decisions"]+=1
        new_assignment = assignment.copy()
        new_assignment[var] = value

        sat, result, stats = dpll(clauses, new_assignment, stats)

        if sat:
            return True, result, stats
    return False, None, stats
    
def variable_assignment(clauses, assignment):
    #Selects the next branching variable.
    for clause in clauses:
        for lit in clause:
            var = abs(lit)
            if var not in assignment:
                return var
    return None
