from parse_params import Params
import csv
import json
from filter_results import apply_filter

baseline_files = [
    "results/main_evaluation.txt"
]

samples_files = [
    "results/samples.txt"
]

readout_files = [
    "results/readout.txt"
]

def parse_files(files):
    params = []
    for file_name in files:
        with open(file_name) as file:
            lines = file.readlines()
        params.extend([Params(**json.loads(line)) for line in lines])
    return params

baseline_params = apply_filter(
    parse_files(baseline_files),
    "and graphs.problem maxcut and source.model.noise 1.0 source.model.time 1.0",
)
samples_params = apply_filter(
    parse_files(samples_files),
    "source.model.n_samples 100",
)
readout_params = apply_filter(
    parse_files(readout_files),
    "and and and graphs.problem maxcut source.model.noise 1.0 source.model.time 1.0 source.model.readout 1.0",
)

def parse_data(params):
    data = {}
    for p in params:
        alg = p.source.algorithm.type
        n_layers = p.source.algorithm.n_layers
        size = p.graphs.size
        key = alg, n_layers, size
        if key not in data:
            data[key] = []
        data[key].append(p.value)
    return data

baseline_data = parse_data(baseline_params)
samples_data = parse_data(samples_params)
readout_data = parse_data(readout_params)

alg_name = {
    "qaoa": "QAOA",
    "wsqaoa": "WSQAOA",
    "wsinitqaoa": "WS-Init-QAOA",
    "rqaoa": "RQAOA",
}

rows = []
for data, source in [(readout_data, "Readout errors"), (samples_data, "Sample size 100")]:
    for alg in ["qaoa", "wsqaoa", "wsinitqaoa", "rqaoa"]:
        for n_layers in [1,2,3]:
            values = []
            for size in [5,6,7,8,9,10]:
                value = sum(data[(alg, n_layers, size)]) / len(data[(alg, n_layers, size)])
                baseline_value = sum(baseline_data[(alg, n_layers, size)]) / len(baseline_data[(alg, n_layers, size)])
                values.append((value - baseline_value) / baseline_value)
            avg = sum(values) / len(values)
            rows.append((alg_name[alg], n_layers, avg, source))

headers = ("algorithm", "n_qaoa_layers", "relative_performance_decrease", "source")
with open("csvs/readout_and_samples.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(rows)
                
