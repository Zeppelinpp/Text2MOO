from pymoo.core.problem import Problem
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.optimize import minimize
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel
import numpy as np


class MOEADConfig(BaseModel):
    data: Dict[str, List[Any]]
    variable: List[str]
    variable_attributes: List[str]
    objective: Dict[str, Literal["sum_min", "sum_max"]]
    constraints: Optional[Dict[str, Dict[str, Any]]] = None
    constraint_penalty: Optional[float] = 1000000
    n_partitions: Optional[int] = 12
    prob_neighbor_mating: Optional[float] = 0.7
    n_neighbors: Optional[int] = 10
    n_gen: Optional[int] = 50
    seed: Optional[int] = 42


class MOEADConfigforLLM(BaseModel):
    variable: List[str]
    variable_attributes: List[str]
    objective: Dict[str, Literal["sum_min", "sum_max"]]
    constraints: Optional[Dict[str, Dict[str, Any]]] = None
    constraint_penalty: Optional[float] = 1000000
    n_partitions: Optional[int] = 12
    prob_neighbor_mating: Optional[float] = 0.7
    n_neighbors: Optional[int] = 10
    n_gen: Optional[int] = 50
    seed: Optional[int] = 42


class MOEADProblem(Problem):
    def __init__(self, config: MOEADConfig):
        n_var = len(config.variable)
        n_obj = len(config.objective)
        self.n_constraints = len(config.constraints) if config.constraints else None
        self.constraint_penalty = config.constraint_penalty
        self.constraints_mapping = config.constraints
        self.objective_mapping = config.objective
        self.opt_data = config.data

        xl = np.array([0] * n_var)
        xu = []
        for var in config.variable:
            xu.append(len(config.data[var]) - 1)
        xu = np.array(xu)

        super().__init__(
            n_var=n_var,
            n_obj=n_obj,
            xl=xl,
            xu=xu,
            vtype=int,
        )

    def _evaluate(self, x, out, *args, **kwargs):
        f = [[] for _ in range(self.n_obj)]

        for individual in x:
            # 获取组合数据
            selected_idx = [int(individual[i]) for i in range(self.n_var)]
            combination = []
            for idx, options in zip(selected_idx, self.opt_data.values()):
                combination.append(options[idx])

            # f
            for idx, objective in enumerate(self.objective_mapping.items()):
                obj_attr, obj_type = objective
                if obj_type == "sum_min":
                    value = sum(
                        [item[obj_attr] for item in combination if obj_attr in item]
                    )
                    if self.n_constraints:
                        for (
                            constraint_attr,
                            constraint_config,
                        ) in self.constraints_mapping.items():
                            if (
                                constraint_config["type"] == ">="
                                and any(
                                    item[constraint_attr] < constraint_config["value"]
                                    for item in combination
                                    if constraint_attr in item
                                )
                                or (
                                    constraint_config["type"] == "<="
                                    and any(
                                        item[constraint_attr]
                                        > constraint_config["value"]
                                        for item in combination
                                        if constraint_attr in item
                                    )
                                )
                            ):
                                f[idx].append(self.constraint_penalty)
                            else:
                                f[idx].append(value)
                    else:
                        f[idx].append(value)
                elif obj_type == "sum_max":
                    value = -sum(
                        [item[obj_attr] for item in combination if obj_attr in item]
                    )
                    if self.n_constraints:
                        for idx, constraint in enumerate(
                            self.constraints_mapping.items()
                        ):
                            constraint_attr, constraint_config = constraint
                            if constraint_config["type"] == ">=" and any(
                                item[constraint_attr] < constraint_config["value"]
                                for item in combination
                                if constraint_attr in item
                            ):
                                f[idx].append(self.constraint_penalty)
                            if constraint_config["type"] == "<=" and any(
                                item[constraint_attr] > constraint_config["value"]
                                for item in combination
                                if constraint_attr in item
                            ):
                                f[idx].append(self.constraint_penalty)
                    else:
                        f[idx].append(value)

        out["F"] = np.column_stack(f)
