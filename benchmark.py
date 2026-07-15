import time
import csv

import CNF_encoder as CNF
import Nqueens as Nq
import Nondango
import sat_solver as SAT
import cdcl
import Nonogram


def make_nqueens_cnf(n):
    #Generates CNF formulas for N-Queens instances of size n
    formula = Nq.nqueens(n)
    goodclauses = [
    CNF.collect_literals(clause)
    for clause in formula
    ]
    clauses, varmap = CNF.clauses_to_dimacs_list(goodclauses)
    return clauses, len(varmap)

def run_dpll(clauses):
    #Run DPLL on clauses in CNF and record time of process
    start = time.perf_counter()
    sat, assignment, stats = SAT.dpll(clauses)
    runtime = time.perf_counter() - start

    return sat, runtime, stats


def run_cdcl(clauses, num_vars):
    #Run CDCL on clauses in CNF and record time of process
    start = time.perf_counter()
    sat, assignment, stats = cdcl.cdcl(clauses, num_vars)
    runtime = time.perf_counter() - start

    return sat, runtime, stats

def naive_encode(formula):
    #Encode a formula into CNF using naive encoding
    start = time.perf_counter()

    nnf_formula = CNF.nnf(formula)
    cnf_formula = CNF.CNF(nnf_formula)
    literal_clauses = CNF.collectclauses(cnf_formula)
    clauses, varmap = CNF.clauses_to_dimacs_list(literal_clauses)

    return clauses, varmap, time.perf_counter() - start


def Tseitin_encode(formula):
    #Encode a formula into CNF using Tseitin transformation
    start = time.perf_counter()
    formula = CNF.nnf(formula)
    tseitin_formula = CNF.tseitin_tranformer(formula)
    literal_clauses = [
        CNF.collect_literals(clause)
        for clause in tseitin_formula
    ]
    clauses, varmap = CNF.clauses_to_dimacs_list(literal_clauses)

    return clauses, varmap, time.perf_counter() - start


def benchmark_instance(problem, size, clauses, num_vars):
    #Create benchmark instance of a problem of a certain size. Let it both run on DPLL and CDCL and return collected data
    rows = []

    sat, runtime, stats = run_dpll(clauses)
    rows.append({
        "problem": problem,
        "size": size,
        "solver": "DPLL",
        "variables": num_vars,
        "clauses": len(clauses),
        "runtime": round(runtime, 6),
        "sat": sat,
        "decisions": stats["decisions"],
        "conflicts": stats["conflicts"],
        "propagations": stats["propagations"],
        "learned_clauses": ""
    })

    sat, runtime, stats = run_cdcl(clauses, num_vars)
    rows.append({
        "problem": problem,
        "size": size,
        "solver": "CDCL",
        "variables": num_vars,
        "clauses": len(clauses),
        "runtime": round(runtime, 6),
        "sat": sat,
        "decisions": stats.get("decisions", ""),
        "conflicts": stats.get("conflicts", ""),
        "propagations": stats.get("propagations", ""),
        "learned_clauses": stats.get("learned_clauses", "")
    })

    return rows
'''
for n in [2, 4, 6, 8, 10, 12, 14, 16, 18]:
    #test instances of N-Queens of different sizes
    clauses, varmaplength = make_nqueens_cnf(n)
    rows = benchmark_instance("N-Queens", n, clauses, varmaplength)
    print(rows)
'''

#Here instances of Nonogram are declared
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
rows_5 = [[1], [3], [5], [3], [1]]
cols_5 = [[1], [3], [5], [3], [1]]
rows_10 = [
    [2], [4], [6], [8], [10],
    [8], [6], [4], [2], [1]
]

cols_10 = [
    [1], [2], [4], [6], [8],
    [10], [8], [6], [4], [2]
]
rows_10b = [
    [3], [1,1], [5], [2,2], [7],
    [1,3,1], [6], [2,2], [1,1], [3]
]

cols_10b = [
    [2], [4], [1,1], [6], [3,3],
    [3,3], [6], [1,1], [4], [2]
]
rows_15 = [
    [3], [5], [7], [2,3,2], [9],
    [1,1,1], [3,3], [15], [3,3],
    [1,1,1], [9], [2,3,2], [7], [5], [3]
]

cols_15 = [
    [3], [5], [7], [2,3,2], [9],
    [1,1,1], [3,3], [15], [3,3],
    [1,1,1], [9], [2,3,2], [7], [5], [3]
]
nonogram_instances1 = [
    ("5x5", rows_5, cols_5),
    ("15x15", rows_15, cols_15)
]

nonogram_instances2 = [
    ("5x5", rows_5, cols_5),
    ("10x10", rows_10, cols_10),
    ("10x10b", rows_10b, cols_10b),
    ("15x15", rows_15, cols_15),
]
'''
for name, rows, cols in nonogram_instances1:
    #Nonogram instances are tested, on naive and Tseitin encoding, and then run on DPLL and CDCL

    print(f"\n========== {name} ==========")

    formula = Nonogram.build_nonogram_formula(rows, cols)

    for encoding_name, encoder in [
        #("Naive", naive_encode),
        ("Tseitin", Tseitin_encode)
    ]:

        clauses, varmap, enc_time = encoder(formula)

        print(f"\nEncoding: {encoding_name}")
        print(f"Variables: {len(varmap)}")
        print(f"Clauses: {len(clauses)}")
        print(f"Encoding time: {enc_time:.6f}")

        sat, runtime, stats = run_dpll([c[:] for c in clauses])

        print("DPLL")
        print("SAT:", sat)
        print("Runtime:", runtime)
        print(stats)

        sat, runtime, stats = run_cdcl(
            [c[:] for c in clauses],
            len(varmap)
        )

        print("CDCL")
        print("SAT:", sat)
        print("Runtime:", runtime)
        print(stats)
'''
for name, rows, cols in nonogram_instances2:

    print(f"\n========== {name} ==========")

    formula = Nonogram.build_nonogram_formula(rows, cols)
    clauses, varmap, enc_time = Tseitin_encode(formula)
    print("Tseitin")
    print(f"Variables: {len(varmap)}")
    print(f"Clauses: {len(clauses)}")
    print(f"Encoding time: {enc_time:.6f}")

    sat, runtime, stats = run_dpll([c[:] for c in clauses])

    print("DPLL")
    print("SAT:", sat)
    print("Runtime:", runtime)
    print(stats)

    sat, runtime, stats = run_cdcl(
        [c[:] for c in clauses],
        len(varmap)
    )

    print("CDCL")
    print("SAT:", sat)
    print("Runtime:", runtime)
    print(stats)

'''
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

Nondango_instances = [
    ("6x6", Nondango6x6),
    ("10x10", Nondango10x10),
    ("12x12", Nondango12x12),
    ("14x14", Nondango14x14)
]

for name, game in Nondango_instances:
    #Nondango instances are tested here
    formula, varmap = Nondango.nondango_sat(game)
    sat, runtime, stats = run_dpll([c[:] for c in formula])
    print(f"\n========== {name} ==========")
    print("DPLL")
    print("SAT:", sat)
    print("Runtime:", runtime)
    print(stats)

    sat, runtime, stats = run_cdcl(
        [c[:] for c in formula],
        len(varmap)
    )

    print("CDCL")
    print("SAT:", sat)
    print("Runtime:", runtime)
    print(stats)
'''
'''
nqueen_results = []

for n in [2, 4, 6, 8, 10, 12, 14, 16, 18]:
    N-Queens tester, tested on both encodings and both SAT solver algorithms
    print(f"\n========== N-Queens {n} ==========")

    formula = Nq.nqueensimplication(n)

    for encoding_name, encoder in [
        ("Naive", naive_encode),
        ("Tseitin", Tseitin_encode)
    ]:
        clauses, varmap, encoding_time = encoder(formula)

        print(f"\nEncoding: {encoding_name}")
        print(f"Variables: {len(varmap)}")
        print(f"Clauses: {len(clauses)}")
        print(f"Encoding time: {encoding_time:.6f}")

        sat, runtime, stats = run_dpll([c[:] for c in clauses])
        print("DPLL:", sat, runtime, stats)

        nqueen_results.append({
            "problem": "N-Queens",
            "size": n,
            "encoding": encoding_name,
            "solver": "DPLL",
            "variables": len(varmap),
            "clauses": len(clauses),
            "encoding_time": encoding_time,
            "runtime": runtime,
            "sat": sat,
            "decisions": stats["decisions"],
            "conflicts": stats["conflicts"],
            "propagations": stats["propagations"],
            "learned_clauses": ""
        })

        sat, runtime, stats = run_cdcl([c[:] for c in clauses], len(varmap))
        print("CDCL:", sat, runtime, stats)

        nqueen_results.append({
            "problem": "N-Queens",
            "size": n,
            "encoding": encoding_name,
            "solver": "CDCL",
            "variables": len(varmap),
            "clauses": len(clauses),
            "encoding_time": encoding_time,
            "runtime": runtime,
            "sat": sat,
            "decisions": stats["decisions"],
            "conflicts": stats["conflicts"],
            "propagations": stats["propagations"],
            "learned_clauses": stats["learned_clauses"]
        })
'''
'''
nondango_instances = [
    ("6x6", Nondango.Nondango6x6),
    ("10x10", Nondango.Nondango10x10),
    ("12x12", Nondango.Nondango12x12),
    ("14x14", Nondango.Nondango14x14),
]
results = []

for name, game in nondango_instances:
    #testing Nondango on both encoding strategies and Solver algorithms
    print(f"\n========== Nondango {name} ==========")

    formula = Nondango.nondangoimplication(game)

    for encoding_name, encoder in [
        ("Naive", naive_encode),
        ("Tseitin", Tseitin_encode)
    ]:
        clauses, varmap, encoding_time = encoder(formula)
        num_vars = len(varmap)

        print(f"\nEncoding: {encoding_name}")
        print("Variables:", num_vars)
        print("Clauses:", len(clauses))
        print("Encoding time:", round(encoding_time, 6))

        sat, runtime, stats = run_dpll([c[:] for c in clauses])
        print("DPLL:", sat, runtime, stats)

        results.append({
            "problem": "Nondango",
            "size": name,
            "encoding": encoding_name,
            "solver": "DPLL",
            "variables": num_vars,
            "clauses": len(clauses),
            "encoding_time": round(encoding_time, 6),
            "runtime": round(runtime, 6),
            "sat": sat,
            "decisions": stats["decisions"],
            "conflicts": stats["conflicts"],
            "propagations": stats["propagations"],
            "learned_clauses": ""
        })

        sat, runtime, stats = run_cdcl([c[:] for c in clauses], num_vars)
        print("CDCL:", sat, runtime, stats)

        results.append({
            "problem": "Nondango",
            "size": name,
            "encoding": encoding_name,
            "solver": "CDCL",
            "variables": num_vars,
            "clauses": len(clauses),
            "encoding_time": round(encoding_time, 6),
            "runtime": round(runtime, 6),
            "sat": sat,
            "decisions": stats.get("decisions", ""),
            "conflicts": stats.get("conflicts", ""),
            "propagations": stats.get("propagations", ""),
            "learned_clauses": stats.get("learned_clauses", "")
        })
'''