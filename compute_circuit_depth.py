import warnings
from qat.opt import Ising, MaxCut, NumberPartitioning
import numpy as np
import networkx as nx
from parse_params import *
import json


def gen_problem(graphs: Graphs, seed: int) -> Ising:
    if graphs.problem == "maxcut":
        graph = nx.generators.random_graphs.erdos_renyi_graph(
            graphs.size, 0.5, seed=seed
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return MaxCut(graph)
    if graphs.problem == "partition":
        np.random.seed(seed)
        numbers = np.random.rand(graphs.size)
        return NumberPartitioning(numbers)
    raise ValueError(f"Unsupported problem {graphs.problem}")


def compute_depth(problem: Ising) -> int:
    return problem.qaoa_ansatz(1).circuit.depth(gates=["CNOT"])


output = dict()
for problem_type in ["maxcut", "partition"]:
    output[problem_type] = {}
    for size in range(5, 10 + 1):
        results = []
        graphs = Graphs(size=size, problem=problem_type)
        for seed in range(100):
            problem = gen_problem(graphs, seed)
            depth = compute_depth(problem)
            results.append(depth)
        output[problem_type][str(size)] = results

with open("circuit_depths.json", "w") as file:
    json.dump(output, file)
