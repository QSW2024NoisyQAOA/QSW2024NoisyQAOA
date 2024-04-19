import json5 as json
from typing import Type


def auto_repr(cls: Type) -> Type:
    def __repr__(self):
        return "%s(%s)" % (
            type(self).__name__,
            ", ".join("%s=%s" % item for item in vars(self).items()),
        )

    cls.__repr__ = __repr__
    return cls


def auto_eq(cls: Type) -> Type:
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        for key in vars(self):
            if getattr(self, key) != getattr(other, key):
                return False
        return True

    cls.__eq__ = __eq__
    return cls


def auto_hash(cls: Type) -> Type:
    def __hash__(self):
        hashable_members = tuple(
            getattr(self, key)
            for key in vars(self)
            if isinstance(getattr(self, key), (int, float, str, bool))
        )
        return hash(hashable_members)

    cls.__hash__ = __hash__
    return cls


input_types = {
    "maxcut": ["erdos_renyi"],
    "partition": ["uniform"],
}


@auto_repr
@auto_eq
@auto_hash
class Graphs:
    def __init__(self, size: int, problem: str="maxcut", type: str=None, n: int=100):
        if problem not in ["maxcut", "partition"]:
            raise ValueError(f"Unknown problem {problem}")
        if type is None:
            type = input_types[problem][0]
        if type not in input_types[problem]:
            raise ValueError(f"Unknown input type {type} for problem {problem}")
        self.problem = problem
        self.size = size
        self.type = type
        self.n = n

    def to_dict(self) -> dict:
        d = {
            "type": self.type,
            "size": self.size,
            "n": self.n,
        }
        if self.problem != "maxcut":
            d["problem"] = self.problem
        return d


@auto_repr
@auto_eq
@auto_hash
class Model:
    def __init__(
        self,
        type: str,
        noise: float = None,
        params: str = None,
        nSamples: int = None,
        time: float = None,
        sx: bool = True,
        readout: float = 0.0,
    ):
        """
        type:
            ideal: no noise
            noisy_fidelity: idle: thermal relaxation + gate: depolarizing 
            noisy_composite: idle: thermal relaxation + gate: hardware-matched composite noise
        params:
            T1, T2, gate lengths, gate unfidelities
            qiskit_average: Qiskit fake backends average values
            qiskit_median: Qiskit fake backends median values
            qiskit_best: Qiskit fake backends best values
        nSamples:
            number samples when sampling Hamiltonian during QAOA (only supported for noisy models)
        """
        if type not in [
            "ideal",
            "noisy",
            "noisy_fidelity",
            "noisy_composite",
            "noisy_depolarizing",
        ]:
            raise ValueError(f"Unknown model type {type}")
        if type == "ideal" and noise is not None:
            raise ValueError("Model type 'ideal' does not support noise")
        if type == "ideal" and nSamples is not None:
            raise ValueError("Model type 'ideal' does not support nSamples")
        if type == "ideal":
            sx = False
        if type == "ideal" and readout != 0.0:
            raise ValueError("Readout error only supported for noisy models")
        if type != "ideal" and noise is None:
            noise = 1.0
        if type != "ideal" and time is None:
            time = 1.0
        if type != "ideal" and params is None:
            params = "qiskit_median"
        if noise is not None:
            noise = float(noise)
        if time is not None:
            time = float(time)
        self.type = type
        self.noise = noise
        self.time = time
        self.params = params
        self.n_samples = nSamples
        self.sx = sx
        self.readout = readout

    def to_dict(self) -> dict:
        d = {"type": self.type}
        if self.noise is not None:
            d["noise"] = self.noise
        if self.time is not None:
            d["time"] = self.time
        if self.params is not None:
            d["params"] = self.params
        if self.n_samples is not None:
            d["nSamples"] = self.n_samples
        if self.sx:
            d["sx"] = self.sx
        if self.readout != 0.0:
            d["readout"] = self.readout
        return d

    def __str__(self) -> str:
        if self.type == "ideal":
            return "ideal"
        else:
            name = self.type
            if self.sx:
                name += " sx"
            if self.readout != 0:
                name += " readout"
                if self.readout != 1.0:
                    name += " " + str(self.readout)
            if self.noise == 1.0 and self.time == 1.0:
                result = f"{name} ({self.params})"
            else:
                result = f"{name} ({self.params}, {self.noise}, {self.time})"
            if self.n_samples is not None:
                return result + f"{self.n_samples} samples"
            return result


@auto_repr
@auto_eq
@auto_hash
class Algorithm:
    def __init__(self, type: str, nLayers: int, nShots: int=1, nSamples: int=None):
        """
        type:
            QAOA: regular QAOA
            WSQAOA: Warm-start with GW rounding solution, changed initial state and mixer
            WS-Init-QAOA (https://arxiv.org/pdf/2301.05750.pdf): like WSQAOA but with original QAOA mixer
            RQAOA: find highest correlated edge, add constraint (same/different side of cut), repeat
        nLayers: QAOA depth (often called p)
        nShots: Number of runs per graph (average results)
        nSamples (only for RQAOA): number samples used for determining edge correlation
        """
        if type not in ["qaoa", "wsqaoa", "wsinitqaoa", "rqaoa"]:
            raise ValueError(f"Unknown algorithm {type}")
        if nSamples is not None and type != "rqaoa":
            raise ValueError("nSamples parameter only supported for RQAOA")
        self.type = type
        self.n_layers = nLayers
        self.n_shots = nShots
        self.n_samples = nSamples

    def to_dict(self) -> dict:
        result = {"type": self.type, "nLayers": self.n_layers}
        if self.n_shots > 1:
            result["nShots"] = self.n_shots
        if self.n_samples is not None:
            result["nSamples"] = self.n_samples
        return result

    def __str__(self) -> dict:
        if self.type == "rqaoa":
            n_samples = str(self.n_samples) if self.n_samples is not None else "inf"
            return f"{self.type.upper()} (depth: {self.n_layers}, samples: {n_samples})"
        return f"{self.type.upper()} (depth: {self.n_layers})"


def algorithm_equals(a: Algorithm, b: Algorithm) -> bool:
    if a is None:
        return b is None
    if b is None:
        return False
    return a.type == b.type and a.n_samples == b.n_samples


@auto_repr
@auto_eq
@auto_hash
class Source:
    def __init__(self, type: str=None, algorithm: Algorithm=None, model: Model=None):
        if type is None:
            type = "qpu"
        if type not in ["random", "qpu", "approximation"]:
            raise ValueError(f"Unknown source type {type}")
        if type != "qpu" and (algorithm is not None or model is not None):
            raise ValueError(
                f"Source type '{type}' does not support algorithms or models"
            )
        if type == "qpu" and (algorithm is None or model is None):
            raise ValueError(f"QPU Source requires an algorithm and model")
        self.type = type
        if algorithm is None or isinstance(algorithm, Algorithm):
            self.algorithm = algorithm
        else:
            self.algorithm = Algorithm(**algorithm)
        if model is None or isinstance(model, Model):
            self.model = model
        else:
            self.model = Model(**model)

    def to_dict(self) -> dict:
        d = {"type": self.type}
        if self.algorithm is not None:
            d["algorithm"] = self.algorithm.to_dict()
        if self.model is not None:
            d["model"] = self.model.to_dict()
        return d


def source_equals(a: Source, b: Source) -> bool:
    if a is None:
        return b is None
    if b is None:
        return False
    return (
        a.type == b.type
        and a.model == b.model
        and algorithm_equals(a.algorithm, b.algorithm)
    )


@auto_repr
@auto_eq
@auto_hash
class Params:
    def __init__(
        self,
        graphs: Graphs,
        source: Source,
        metric: str = "approx_ratio",
        value: float = None,
        time: int = None,
        meta: dict = None,
        raw: list[float] = None,
    ):
        if metric not in ["approx_ratio", "success_prob", "fidelity"]:
            raise ValueError(f"Unknown metric {metric}")
        self.metric = metric
        if isinstance(graphs, Graphs):
            self.graphs = graphs
        else:
            self.graphs = Graphs(**graphs)
        if isinstance(source, Source):
            self.source = source
        else:
            self.source = Source(**source)

        if metric == "fidelity":
            if self.source.type != "qpu":
                raise ValueError(
                    f"Metric fidelity not supported for source '{self.source.type}'"
                )
            if self.source.model.type == "ideal":
                raise ValueError(f"Metric fidelity not supported for ideal qpu")
            if self.source.algorithm.type == "rqaoa":
                raise ValueError(f"Metric fidelity not supported for algorithm RQAOA")
        self.value = value
        self.time = time
        self.meta = meta
        self.raw = raw

    def to_dict(self) -> dict:
        d = {
            "metric": self.metric,
            "graphs": self.graphs.to_dict(),
            "source": self.source.to_dict(),
        }
        if self.raw is not None:
            d["raw"] = self.raw
        if self.value is not None:
            d["value"] = self.value
        if self.time is not None:
            d["time"] = self.time
        if self.meta is not None:
            d["meta"] = self.meta
        return d

    def dump_json(self, raw=True) -> str:
        d = self.to_dict()
        if not raw:
            del d["raw"]
        return json.dumps(d, separators=(",", ":"), quote_keys=True)


if __name__ == "__main__":
    with open("results.csv") as file:
        lines = [[p.strip() for p in l.split(",")] for l in file.readlines()][1:]

    for metric, algorithm, model, size, n_layers, value in lines:
        if model in ["random", "gw_rounding"]:
            source = {"type": model}
        else:
            if model == "ideal":
                model_dict = {"type": "ideal"}
            if model == "noisy":
                model_dict = {"type": "noisy", "noise": 1.0}
            if model == "noisy10percent":
                model_dict = {"type": "noisy", "noise": 0.1}
            source = {
                "type": "qpu",
                "model": model_dict,
                "algorithm": {"type": algorithm, "nLayers": int(n_layers)},
            }
        j = {
            "metric": metric,
            "value": float(value),
            "graphs": {"size": int(size)},
            "source": source,
        }
        print(Params(**j).dump_json())

    # with open("params.json") as file:
    #     params = json.load(file)
    #     params = spread_json(params)
    #     print(params)
    #     for p in params:
    #         param_set = Params(**p)
    #         print(param_set)
