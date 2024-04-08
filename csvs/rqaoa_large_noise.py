import csv
import json
from parse_params import Params
from filter_results import apply_filter

files = [
    "results/main_evaluation.txt",
    "results/large_noise.txt",
]

params = []

for file_name in files:
    with open(file_name) as file:
        lines = file.readlines()
    params.extend([Params(**json.loads(line)) for line in lines])

params = apply_filter(
    params,
    "or != source.algorithm.type rqaoa source.algorithm.n_samples 10"
)

data = {}
for p in params:
    if p.source.model.noise != p.source.model.time:
        continue
    problem = p.graphs.problem
    alg = p.source.algorithm.type
    n_layers = p.source.algorithm.n_layers
    size = p.graphs.size
    noise = p.source.model.noise
    if noise == None:
        noise = 0.0

    key = problem, alg, n_layers, size, noise

    data[key] = p.raw

problem_name = {
    "maxcut": "Max-cut",
    "partition": "Partition",
}
alg_name = {
    "qaoa": "QAOA",
    "rqaoa": "RQAOA",
}

rows = []
for problem in ["maxcut", "partition"]:
    for alg in ["qaoa", "rqaoa"]:
        for size in [5,6,7,8,9,10]:
            for n_layers in [1,2,3]:
                for noise in [0.0, 1.0, 2.0, 3.0, 4.0]:
                    values = data[(problem, alg, n_layers, size, noise)]
                    avg = sum(values) / len(values)
                    rows.append((
                        problem_name[problem], alg_name[alg], n_layers, size, noise, avg
                    ))
    

headers = ("problem", "algorithm", "n_qaoa_layers", "n_qubits", "noise_level", "performance")
with open("csvs/rqaoa_large_noise.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(rows)


