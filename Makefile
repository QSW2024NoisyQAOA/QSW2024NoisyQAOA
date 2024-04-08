.ONESHELL:

N_THREADS?=1

print:
	@echo $(TEST)

PYTHON := PYTHONPATH=$(PYTHONPATH):. .venv/bin/python
PIP := .venv/bin/pip
ACTIVATE := .venv/bin/activate

install:
	$(PIP) install -r requirements.txt

RESULTS_DIR := results
RESULTS_SCRIPTS := $(wildcard $(RESULTS_DIR)/*.bash)
RESULTS := $(patsubst $(RESULTS_DIR)/%.bash, $(RESULTS_DIR)/%.txt, $(RESULTS_SCRIPTS))

$(RESULTS_DIR)/%.txt: $(RESULTS_DIR)/%.bash
	source $(ACTIVATE)
	bash $< $(N_THREADS)

results: $(RESULTS)

circuit_depths.json: compute_circuit_depth.py
	$(PYTHON) $<

csvs/algorithm_comparison_n_layers.csv: csvs/algorithm_comparison_n_layers.py results/main_evaluation.txt results/bounds.txt
	$(PYTHON) $<

csvs/algorithm_comparison_n_qubits.csv: csvs/algorithm_comparison_n_qubits.py results/main_evaluation.txt results/bounds.txt
	$(PYTHON) $<

csvs/fidelity_comparison.csv: csvs/fidelity_comparison.py results/fidelity.txt
	$(PYTHON) $<

csvs/layer_advantage_by_depth.csv: csvs/layer_advantage_by_depth.py results/main_evaluation.txt results/large_noise.txt circuit_depths.json
	$(PYTHON) $<

csvs/layer_advantage_by_depth_total.csv: csvs/layer_advantage_by_depth.py results/main_evaluation.txt results/large_noise.txt circuit_depths.json
	$(PYTHON) $<

csvs/layer_advantage.csv: csvs/layer_advantage.py results/main_evaluation.txt
	$(PYTHON) $<

csvs/readout_and_samples.csv: csvs/readout_and_samples.py results/main_evaluation.txt results/readout.txt results/samples.txt
	$(PYTHON) $<

csvs/rqaoa_large_noise.csv: csvs/rqaoa_large_noise.py results/main_evaluation.txt results/large_noise.txt
	$(PYTHON) $<

csvs/rqaoa_samples.csv: csvs/rqaoa_samples.py results/main_evaluation.txt results/large_noise.txt
	$(PYTHON) $<

csvs: algorithm_comparison_n_layers.csv algorithm_comparison_n_qubits.csv fidelity_comparison.csv layer_advantage_by_depth.csv layer_advantage_by_depth_total.csv layer_advantage.csv readout_and_samples.csv rqaoa_large_noise.csv rqaoa_samples.csv

plots:
	docker build -t qsw-noisy-qaoa . && docker run -v $(pwd)/img-pdf:/app/img-pdf -v $(pwd)/img-tikz:/app/img-tikz qsw-noisy-qaoa

.PHONY: install results csvs plots