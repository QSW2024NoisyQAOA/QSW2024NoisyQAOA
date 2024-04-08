import json
import csv
from parse_params import Params

files = [
    "results/fidelity.txt",
]

params = []

for file_name in files:
    with open(file_name) as file:
        lines = file.readlines()
    params.extend([Params(**json.loads(line)) for line in lines])

data = {}
counter = 0
for p in params:
    model = p.source.model
    problem = p.graphs.problem
    alg = p.source.algorithm.type
    depth = p.source.algorithm.n_layers
    size = p.graphs.size
    noisy = (model.noise, model.time)

    key = problem, alg, depth, size, noisy

    data[key] = p.raw

problem_name = {
    "maxcut": "Max-cut",
    "partition": "Partition",
}
alg_name = {
    "qaoa": "QAOA",
    "wsqaoa": "WSQAOA",
    "wsinitqaoa": "WS-Init-QAOA",
}
noisy_name = {
    (1.0, 0.0): "Depolarizing",
    (0.0, 1.0): "Thermal Relaxation",
    (1.0, 1.0): "Both",
}

rows = []
for problem in ["maxcut", "partition"]:
    for alg in ["qaoa", "wsqaoa", "wsinitqaoa"]:
        for noisy in [(1.0, 0.0), (0.0, 1.0), (1.0, 1.0)]:
            for depth in [1, 2, 3]:
                fidelity = []
                for size in [5, 6, 7, 8, 9, 10]:
                    fidelity.extend(data[(problem, alg, depth, size, noisy)])
                avg = sum(fidelity) / len(fidelity)
                rows.append((problem_name[problem], alg_name[alg], noisy_name[noisy], depth, avg))

headers = ("problem", "algorithm", "noise_source", "n_qaoa_layers", "fidelity")
with open("csvs/circuit_fidelity.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(rows)