import numpy as np
import csv
import json
from parse_params import Params

files = [
    "results/main_evaluation.txt",
    "results/large_noise.txt",
]

with open("circuit_depths.json") as file:
    circuit_depths = json.load(file)

params = []

for file_name in files:
    with open(file_name) as file:
        lines = file.readlines()
    params.extend([Params(**json.loads(line)) for line in lines])

for p in params:
    if p.source.model is not None:
        if p.source.model.noise is None:
            p.source.model.noise = 0.0
        if p.source.model.time is None:
            p.source.model.time = 0.0

data_points_raw = {}
for p in params:
    model = p.source.model
    if not (
        model is not None
        # and 0.0 <= model.noise <= 1.0
        # and 0.0 <= model.time <= 1.0
        and model.noise == model.time
        and model.n_samples is None
    ):
        continue
    problem = p.graphs.problem
    n = p.graphs.size
    alg = p.source.algorithm.type
    depth = p.source.algorithm.n_layers
    noisy = model.noise

    data_points_raw[(problem, n, alg, depth, noisy)] = p.raw

problems = ["maxcut", "partition"]
ns = [5, 6, 7, 8, 9, 10]
algs = ["qaoa", "wsqaoa", "wsinitqaoa", "rqaoa"]
noisys = [0.0, 0.25, 0.5, 1.0, 2.0, 4.0]
depths = [1, 2, 3]

problem_name = {
    "maxcut": "Max-cut",
    "partition": "Partition",
}
alg_name = {
    "qaoa": "QAOA",
    "wsqaoa": "WSQAOA",
    "wsinitqaoa": "WS-Init-QAOA",
    "rqaoa": "RQAOA",
}


np.random.seed(0)
rows = []
total_rows = []
for alg, noisy in [(a, n) for a in algs for n in noisys]:
    problem_averages = {}
    for problem in problems:
        # print(alg, noisy)
        xs = []
        ys = []
        y_by_x = {}
        for n in ns:
            key1 = (problem, n, alg, 1, noisy)
            key2 = (problem, n, alg, 2, noisy)
            if key1 not in data_points_raw or key2 not in data_points_raw:
                continue
            ratios = [
                l2 / l1
                for l1, l2 in zip(
                    data_points_raw[key1],
                    data_points_raw[key2],
                )
            ]
            circuit_ds = [circuit_depths[problem][str(n)][seed] for seed in range(100)]
            xs.extend(circuit_ds)
            ys.extend(ratios)

        for x, y in zip(xs, ys):
            if x not in y_by_x:
                y_by_x[x] = []
            y_by_x[x].append(y)

        distinct_xs = sorted(list(y_by_x.keys()))
        averages = [sum(y_by_x[x]) / len(y_by_x[x]) for x in distinct_xs]
        problem_averages[problem] = (distinct_xs, averages)

        margin = 0.25
        for x, ys_for_x in y_by_x.items():
            quantile_25 = np.quantile(ys_for_x, margin)
            quantile_75 = np.quantile(ys_for_x, 1 - margin)
            filtered_ys = []
            for y in ys_for_x:
                if quantile_25 <= y <= quantile_75:
                    filtered_ys.append(y)
            y_by_x[x] = filtered_ys

        xs = []
        ys = []
        for x, ys_for_x in y_by_x.items():
            xs.extend([x] * len(ys_for_x))
            ys.extend(ys_for_x)

        for i, x in enumerate(xs):
            xs[i] += (np.random.random() - 0.5) * 2
        
        for x, y in zip(xs, ys):
            total_rows.append((alg_name[alg], noisy, problem_name[problem], x, y))


    for problem in problems:
        distinct_xs, averages = problem_averages[problem]
        for x, y in zip(distinct_xs, averages):
            rows.append((alg_name[alg], noisy, problem_name[problem], x, y))

headers = ("algorithm", "noise_level", "problem", "circuit_depth", "relative_performance")
with open("csvs/layer_advantage_by_circuit_depth.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(rows)

with open("csvs/layer_advantage_by_circuit_depth_total.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(total_rows)