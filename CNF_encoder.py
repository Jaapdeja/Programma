class Formula:
    pass
#Logic frame, contains properties of operators
class Variable(Formula):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

class Not(Formula):
    def __init__(self, child):
        self.child = child
    def __repr__(self):
        return f"Not({self.child})"

class Or(Formula):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"Or{self.left, self.right}"

class And(Formula):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"And{self.left, self.right}"
    
class Implies(Formula):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"Implies{self.left, self.right}"

def removeimplication(formula):
    #recursive procedure for removing implication when dealing with different operators
    if isinstance(formula, Implies):
        return Or(Not(removeimplication(formula.left)), removeimplication(formula.right))
    if isinstance(formula, And):
        return And(removeimplication(formula.left), removeimplication(formula.right))
    if isinstance(formula, Or):
        return Or(removeimplication(formula.left), removeimplication(formula.right))
    if isinstance(formula, Not):
        return Not(removeimplication(formula.child))
    else:
        return formula

def removedoublenegation(formula):
    #recursive procedure for removing double negation when dealing with different operators
    if isinstance(formula, Not):
        if isinstance(formula.child, Not):
            return removedoublenegation(formula.child.child)
        else:
            return Not(removedoublenegation(formula.child))
    if isinstance(formula, Or):
        return Or(removedoublenegation(formula.left), removedoublenegation(formula.right))
    if isinstance(formula, And):
        return And(removedoublenegation(formula.left), removedoublenegation(formula.right))
    if isinstance(formula, Implies):
        return Implies(removedoublenegation(formula.left), removedoublenegation(formula.right))
    else:
        return formula

def demorgan(formula):
    #applying demorgan on formula
    if isinstance(formula, Not):
        if isinstance(formula.child, And):
            return Or(
                demorgan(Not(formula.child.left)),
                demorgan(Not(formula.child.right))
                )
        if isinstance(formula.child, Or):
            return And(
                demorgan(Not(formula.child.left)), 
                demorgan(Not(formula.child.right)))
        else:
            return Not(
                demorgan(formula.child))
    if isinstance(formula, And):
        return And(demorgan(formula.left), demorgan(formula.right))
    if isinstance(formula, Or):
        return Or(demorgan(formula.left), demorgan(formula.right))
    if isinstance(formula, Implies):
        return Implies(demorgan(formula.left), demorgan(formula.right))
    else:
        return formula

def distribute(a, b):
    #recursively applying distributivity rule to formula
    if isinstance(a, And):
        return And(distribute(a.left, b), distribute(a.right, b))
    if isinstance(b, And):
        return And(distribute(a, b.left), distribute(a, b.right))
    else:
        return Or(a, b)

def CNF(f):
    #Last step of converting to CNF, applying distributivity when appropritate
    if isinstance(f, And):
        return And(CNF(f.left),CNF(f.right))
    if isinstance(f, Or):
        return distribute(CNF(f.left),CNF(f.right))
    return f

def nnf(f):
    # negation normal form, appropriate algorithms applied to formula
    f = removeimplication(f)
    f = demorgan(f)
    f = removedoublenegation(f)
    return f

def collectclauses(f):
    #collect clauses from formula
    if isinstance(f, And):
        return collectclauses(f.left) + collectclauses(f.right)
    return [collect_literals(f)]

def collect_literals(f):
    #collect literals from clause
    if isinstance(f, Or):
        return collect_literals(f.left) + collect_literals(f.right)
    return [f]
class VarGenerator:
    #variable generator, used to introduce variables for Tseitin transformation
    def __init__(self):
        self.counter = 0
    def declare(self):
        self.counter +=1
        return Variable(f"T{self.counter}")
   
def neg_lit(x):
    #returns negation of a literal
    if isinstance(x, Not) and isinstance(x.child, Variable):
        return x.child
    return Not(x)

def tseitinAnd(t, a, b):
    #Generates CNF clauses representing t <-> (a AND b)
    return[
        Or(Not(t), a),
        Or(Not(t), b),
        Or(t, Or(neg_lit(a), neg_lit(b)))
    ]
def tseitinOr(t, a, b):
    #Generates CNF clauses representing t <-> (a OR b)
    return[
        Or(Not(t), Or(a, b)),
        Or(t, neg_lit(a)),
        Or(t, neg_lit(b))
    ]
def tseitin(formula, gen):
    #recursively applies the Tseitin transformation to a Boolean formula
    if isinstance(formula, Variable):
        return formula, []
    if isinstance(formula, Not):
        return formula, []
    if isinstance(formula, And):
        leftpart, leftclauses = tseitin(formula.left, gen)
        rightpart, rightclauses = tseitin(formula.right, gen)
        t = gen.declare()
        clauses = (leftclauses + rightclauses + tseitinAnd(t, leftpart, rightpart))

        return t, clauses
    if isinstance(formula, Or):
        leftpart, leftclauses = tseitin(formula.left, gen)
        rightpart, rightclauses = tseitin(formula.right, gen)
        t = gen.declare()
        clauses = (leftclauses + rightclauses + tseitinOr(t, leftpart, rightpart))

        return t, clauses

def tseitin_tranformer(formula):
    #complete tseitin transformation applied to formula
    gen = VarGenerator()
    root, clauses = tseitin(formula, gen)
    clauses.append(root)
    return clauses

def literal_to_dimacs(literal, varlist):
    #converts literals to be usable in Dimacs notation
    if isinstance(literal, Variable):
        if literal.name not in varlist:
            varlist[literal.name] = len(varlist) +1
        return varlist[literal.name]
    if isinstance(literal, Not) and isinstance(literal.child, Variable):
        if literal.child.name not in varlist:
            varlist[literal.child.name] = len(varlist) +1
        return -varlist[literal.child.name]


def clauses_to_dimacs(clauses):
    #converts list of clauses to dimacs
    varmap = {}
    dimacs_clauses = []

    for clause in clauses:
        literals = collect_literals(clause)
        dimacs_clause = [literal_to_dimacs(literal, varmap) for literal in literals]
        dimacs_clauses.append(dimacs_clause)

        lines = []
        lines.append(f"p cnf {len(varmap)} {len(dimacs_clauses)}")

    for clause in dimacs_clauses:
            lines.append(" ".join(map(str, clause))+ " 0")

    return "\n".join(lines), varmap

def clauses_to_dimacs_list(clauses):
    #converts list of clauses ot dimacs without header
    varmap = {}
    dimacs_clauses = []

    for clause in clauses:
        dimacs_clause = [literal_to_dimacs(literal, varmap) for literal in clause]
        dimacs_clauses.append(dimacs_clause)

    return dimacs_clauses, varmap