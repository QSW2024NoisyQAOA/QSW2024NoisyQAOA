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
    "and source.algorithm.type rqaoa graphs.problem maxcut",
)

data = {}
for p in params:
    if p.source.model.noise != p.source.model.time:
        continue
    n_samples = p.source.algorithm.n_samples
    n_layers = p.source.algorithm.n_layers
    size = p.graphs.size
    noise = p.source.model.noise
    if noise == None:
        noise = 0.0

    key = n_samples, n_layers, size, noise

    if key not in data: 
        data[key] = []

    data[key].append(p.value)

samples_name = {
    10: "10",
    100: "100",
    1000: "1000",
    None: "Exact values",
}

rows = []
for n_samples in [10, 100, 1000, None]:
    for size in [5,6,7,8,9,10]:
        for n_layers in [1,2,3]:
            for noise in [0.0, 1.0, 2.0, 3.0, 4.0]:
                values = data[(n_samples, n_layers, size, noise)]
                avg = sum(values) / len(values)
                rows.append((n_layers, size, noise, samples_name[n_samples], avg))
    

headers = ("n_qaoa_layers", "n_qubits", "noise_level", "samples", "performance")
with open("csvs/rqaoa_samples.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(rows)


