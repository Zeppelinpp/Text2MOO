import numpy as np
import matplotlib.pyplot as plt
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.core.problem import Problem
from pymoo.visualization.scatter import Scatter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Literal


class NSGA2Config(BaseModel):
    data: Dict[str, List[Any]]
    variable: List[str]
    variable_attributes: List[str]
    objective: Dict[str, Literal["sum_min", "sum_max"]]
    constraints: Optional[Dict[str, Dict[str, Any]]] = None
    constraint_penalty: Optional[float] = 1000000
    pop_size: int = 100
    n_gen: int = 50
    seed: Optional[int] = 42


class NSGA2Problem(Problem):
    def __init__(self, config: NSGA2Config):
        n_var = len(config.variable)
        n_obj = len(config.objective)
        n_constraints = len(config.constraints) if config.constraints else None

        self.constraints_mapping = config.constraints
        self.constraint_penalty = config.constraint_penalty
        self.objective_mapping = config.objective
        self.n_obj = n_obj
        self.n_constraints = n_constraints
        self.n_var = n_var
        self.opt_data = config.data

        xl = np.array([0] * n_var)
        xu = []
        for var in config.variable:
            xu.append(len(config.data[var]) - 1)
        xu = np.array(xu)

        super().__init__(
            n_var=n_var,
            n_obj=n_obj,
            n_ieq_constr=n_constraints if n_constraints else 0,
            xl=xl,
            xu=xu,
            vtype=int,
        )

    def _evaluate(self, x, out, *args, **kwargs):
        f = [[] for _ in range(self.n_obj)]
        g = [[] for _ in range(self.n_constraints)] if self.n_constraints else None

        for individual in x:
            # get combination data
            selected_idx = [int(individual[i]) for i in range(self.n_var)]
            combination = []
            for idx, options in zip(selected_idx, self.opt_data.values()):
                combination.append(options[idx])

            # f: objective function
            for idx, objective in enumerate(self.objective_mapping.items()):
                obj_attr, obj_type = objective
                if obj_type == "sum_min":
                    value = sum([item[obj_attr] for item in combination])
                    f[idx].append(value)
                elif obj_type == "sum_max":
                    value = -sum([item[obj_attr] for item in combination])
                    f[idx].append(value)

            # g: constraint function
            if self.n_constraints:
                for idx, constraint in enumerate(self.constraints_mapping.items()):
                    constraint_attr, constraint_config = constraint
                    if constraint_config["type"] == ">=":
                        if any(
                            item[constraint_attr] < constraint_config["value"]
                            for item in combination
                        ):
                            g[idx].append(self.constraint_penalty)
                        else:
                            g[idx].append(0)
                    if constraint_config["type"] == "<=":
                        if any(
                            item[constraint_attr] > constraint_config["value"]
                            for item in combination
                        ):
                            g[idx].append(self.constraint_penalty)
                        else:
                            g[idx].append(0)
        if self.n_constraints:
            out["F"] = np.column_stack(f)
            out["G"] = np.column_stack(g)
        else:
            out["F"] = np.column_stack(f)


