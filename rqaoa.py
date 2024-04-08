from typing import Callable
import random
import networkx as nx
import numpy as np
from qat.linalg import LinAlg
from qat.plugins import ScipyMinimizePlugin
from qat.opt import Ising


class Term:
    def __init__(self, u: int, v: int, weight: float):
        self.u = u
        self.v = v
        self.weight = weight

    def __repr__(self):
        return f"({self.u}, {self.v}): {self.weight}"


class Terms:
    def __init__(self, terms: list[Term]) -> None:
        self.terms = terms
        self.compute_vertex_mappings()
        self.n = len(self.original_to_reduced)

    @staticmethod
    def from_graph(graph) -> "Terms":
        terms = []
        for u, v in graph.edges:
            terms.append(Term(u, v, -0.5))
            terms.append(Term(v, u, -0.5))
        return Terms(terms)

    @staticmethod
    def from_problem(problem: Ising) -> "Terms":
        terms = []
        J = problem.j_coupling_matrix
        n = len(J)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                terms.append(Term(i, j, J[i][j]))
        return Terms(terms)

    def compute_vertex_mappings(self):
        vertices = set()
        for term in self.terms:
            vertices.add(term.u)
            vertices.add(term.v)
        vertices = sorted(list(vertices))

        original_to_reduced = {}
        reduced_to_original = {}
        for i, v in enumerate(vertices):
            original_to_reduced[v] = i
            reduced_to_original[i] = v
        self.original_to_reduced = original_to_reduced
        self.reduced_to_original = reduced_to_original

    def collapse_edge(self, edge: tuple[int, int], sign: int):
        k, l = edge
        term_dict = {}

        def add_edge(edge, weight):
            if edge not in term_dict:
                term_dict[edge] = 0
            term_dict[edge] += weight

        for term in self.terms:
            u, v = term.u, term.v
            if u == k or v == k:
                if u == k:
                    u = l
                if v == k:
                    v = l
                add_edge((u, v), sign * term.weight)
            elif u != k and v != k:
                add_edge((u, v), term.weight)
        terms = [
            Term(u, v, weight)
            for (u, v), weight in term_dict.items()
            if u != v and weight != 0
        ]
        return Terms(terms)

    def to_ising(self) -> Ising:
        J = np.zeros((self.n, self.n))
        for term in self.terms:
            i = self.original_to_reduced[term.u]
            j = self.original_to_reduced[term.v]
            J[i, j] = term.weight
        return Ising(J, np.zeros(self.n))


def compute_max_amplitude_M_ij(samples: list[tuple[str, float]], terms: Terms, n_samples=None) -> tuple[tuple[dict[int, int], dict[int, int]], float]:
    if n_samples is not None:
        reduced_samples = [
            (s, 1 / n_samples)
            for s, _ in random.choices(
                samples, weights=[s[1] for s in samples], k=n_samples
            )
        ]
        samples = reduced_samples

    max_M_ij = 0
    max_ij = None
    for term in terms.terms:
        i, j = terms.original_to_reduced[term.u], terms.original_to_reduced[term.v]
        M_ij = 0
        for bitstring, probability in samples:
            if bitstring[i] == bitstring[j]:
                M_ij += probability
            else:
                M_ij -= probability
        # Using > instead of >= would cause problems in rare situations where all M_ij are 0
        if abs(M_ij) >= abs(max_M_ij):
            max_M_ij = M_ij
            max_ij = (i, j)

    i, j = max_ij
    return (terms.reduced_to_original[i], terms.reduced_to_original[j]), max_M_ij


def perform_qaoa(problem: Ising) -> list[tuple[str, float]]:
    ansatz = problem.qaoa_ansatz(2)

    qpu = LinAlg()
    stack = (
        ScipyMinimizePlugin(
            # x0=initial_params,
            method="COBYLA",
            tol=1e-2,
            options={"maxiter": 150},
        )
        | qpu
    )
    result = stack.submit(ansatz)

    params = eval(result.meta_data["parameters"])
    sol_job = ansatz(
        **{key: var for key, var in zip(ansatz.get_variables(), params)}
    ).circuit.to_job()

    result = qpu.submit(sol_job)
    return [(s.state.bitstring, s.probability) for s in result]


def rqaoa(original_problem: Ising, perform_qaoa: Callable[[Ising], list[tuple[str, float]]], n_samples=None) -> list[tuple[str, float]]:
    terms = Terms.from_problem(original_problem)
    spins = []
    while terms.n > 1:
        problem = terms.to_ising().to_combinatorial_problem()
        samples = perform_qaoa(problem)
        (k, l), max_M_ij = compute_max_amplitude_M_ij(samples, terms, n_samples)
        sign = np.sign(max_M_ij)
        spins.append(((k, l), sign))
        terms = terms.collapse_edge((k, l), sign)
    graph = nx.from_numpy_array(original_problem.j_coupling_matrix)
    solution = compute_final_solution(graph, spins)
    return [(solution, 1)]


def compute_final_solution(graph: nx.Graph, spins: list[tuple[tuple[int, int], int]]) -> str:
    n = len(graph)
    edges = {v: [] for v in range(n)}
    assignment = {v: None for v in range(n)}

    for (u, v), spin in spins:
        edges[u].append((v, spin))
        edges[v].append((u, spin))

    def dfs(u):
        for v, spin in edges[u]:
            if assignment[v] is not None:
                continue
            assignment[v] = spin * assignment[u]
            dfs(v)

    for u in range(n):
        if assignment[u] is not None:
            continue
        assignment[u] = random.choice([-1, 1])
        dfs(u)

    return "".join(["1" if assignment[u] == 1 else "0" for u in range(n)])

