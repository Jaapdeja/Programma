import Nondango
import CNF_encoder
import Nqueens
def assign(var, value, current_level, reason_clause,
           assignment, level, reason, trail):
    #Assign a value to a variable and stores information required for CDCL
    assignment[var] = value
    level[var] = current_level
    reason[var] = reason_clause
    trail.append(var)

def lit_value(lit, assignment):
    #Evaluates truth value of literal under current assignment
    var = abs(lit)

    if var not in assignment:
        return None

    value = assignment[var]
    return value if lit > 0 else not value

def unit_propagate_cdcl(clauses, assignment, level, reason, trail, current_level, stats):
    #Performs unit propagation for CDCL
    #When a clause contains exactly one unassigned literal and all other literals are false, the remaining literal is assigned.
    #The assignment stores the current decision level and the clause that caused the implication.
    changed = True

    while changed:
        changed = False

        for clause in clauses:
            values = [lit_value(lit, assignment) for lit in clause]

            if True in values:
                continue

            unassigned = [
                lit for lit, val in zip(clause, values)
                if val is None
            ]

            if len(unassigned) == 0:
                stats["conflicts"] += 1
                return clause

            if len(unassigned) == 1:
                lit = unassigned[0]
                var = abs(lit)
                value = lit > 0

                if var not in assignment:
                    assign(
                        var,
                        value,
                        current_level,
                        clause,
                        assignment,
                        level,
                        reason,
                        trail
                    )
                    stats["propagations"] += 1
                    changed = True

    return None

def analyze_conflict(conflict_clause, assignment, level, reason, trail, current_level):
    #Performs conflict analysis after a contradiction is found
    #The implementation identifies decision assignments involved in the
    #conflict and constructs a learned clause that prevents the same conflict
    #from occurring again.
    #Returns learned clause and level solver should backjump to
    decision_lits = []

    for var in trail:
        if level[var] > 0 and reason[var] is None:
            if assignment[var] is True:
                decision_lits.append(-var)
            else:
                decision_lits.append(var)

    if not decision_lits:
        return list(conflict_clause), 0

    learned = decision_lits

    levels = sorted(set(level[abs(lit)] for lit in learned))

    if len(levels) <= 1:
        backjump_level = 0
    else:
        backjump_level = levels[-2]

    return learned, backjump_level

def backjump(target_level, assignment, level, reason, trail):
    #Removes assignments made after target decision level
    #Unlike DPLL can jump back multiple steps in one go
    while trail:
        var = trail[-1]

        if level[var] > target_level:
            trail.pop()
            del assignment[var]
            del level[var]
            del reason[var]
        else:
            break

def choose_unassigned_variable(num_vars, clauses, assignment):
    #Selects the next branching variable
    #Unassigned variable appearing most in clauses is chosen to be assigned
    counts = {}

    for clause in clauses:
        for lit in clause:
            var = abs(lit)
            if var not in assignment:
                counts[var] = counts.get(var, 0) + 1

    if not counts:
        return None

    return max(counts, key=counts.get)

def cdcl(clauses, num_vars, max_steps=100000):
    #Full CDCL procedure
    #Solver performs following steps repeatedly
    #1. Unit propagation
    #2. Conflict anlysis and clause learning if a conflict occurs
    #3. Backjumping to a previous decision level
    #4. A new decision assignment if no conflict is found
    assignment = {}
    level = {}
    reason = {}
    trail = []

    current_level = 0
    learned_clauses = []

    stats = {
        "decisions": 0,
        "propagations": 0,
        "conflicts": 0,
        "learned_clauses": 0,
        "steps": 0
    }

    while True:
        stats["steps"] += 1

        if stats["steps"] > max_steps:
            print("CDCL stopped: max steps reached")
            print(stats)
            return False, None, stats

        #all_clauses = clauses + learned_clauses

        conflict = unit_propagate_cdcl(
            clauses,
            assignment,
            level,
            reason,
            trail,
            current_level,
            stats
        )
        if conflict is not None:
            if current_level == 0:
                return False, None, stats

            learned, backjump_level = analyze_conflict(
                conflict,
                assignment,
                level,
                reason,
                trail,
                current_level
            )

            if learned not in learned_clauses:
                learned_clauses.append(learned)
                clauses.append(learned)
                stats["learned_clauses"] += 1

            backjump(
                backjump_level,
                assignment,
                level,
                reason,
                trail
            )

            current_level = backjump_level

        else:
            if len(assignment) == num_vars:
                return True, assignment, stats

            var = choose_unassigned_variable(num_vars, clauses, assignment)

            current_level += 1
            stats["decisions"] += 1

            assign(
                var,
                True,
                current_level,
                None,
                assignment,
                level,
                reason,
                trail
            )