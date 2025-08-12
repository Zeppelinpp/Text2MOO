import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from openai import OpenAI
from typing import Optional
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.optimize import minimize
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.visualization.scatter import Scatter
from text2moo.moea.moead import MOEADConfig, MOEADConfigforLLM, MOEADProblem
from text2moo.prompts.sys_prompts import GEN_MOEAD_CONFIG_PROMPT, GEN_FORMAT_DATA_PROMPT

import logging

logger = logging.getLogger("text2moead")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


class Text2MOEAD:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        if api_key and base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            raise ValueError("api_key and base_url are required")
        self.model = "qwen-turbo" if model is None else model

    def run(self, user_prompt: str, user_data: str):
        try:
            logger.info("Formatting data...")
            data = self._format_data(user_data)
            data = json.loads(data)
        except Exception as e:
            print(e)
            return "Please provide data snippet for info extraction."
        # Generate MOEADConfig
        logger.info("Generating MOEADConfig...")
        config = self._gen_config(data, user_prompt)
        config = json.loads(config)

        # Setup MOEADProblem
        moead_config = MOEADConfig(data=data, **config)
        objective = json.dumps(moead_config.objective, indent=4)
        constraints = json.dumps(moead_config.constraints, indent=4)
        logger.info(f"Objective:\n{objective}")
        logger.info(f"Constraints:\n{constraints}")

        logger.info("Setting up MOEADProblem...")
        problem = MOEADProblem(moead_config)
        algorithm = MOEAD(
            ref_dirs=get_reference_directions("das-dennis", problem.n_obj, n_partitions=moead_config.n_partitions),
            n_neighbors=moead_config.n_neighbors,
            prob_neighbor_mating=moead_config.prob_neighbor_mating,
            sampling=IntegerRandomSampling(),
            crossover=SBX(prob=1.0, eta=3.0, vtype=float, repair=RoundingRepair()),
            mutation=PM(prob=1.0, eta=3.0, vtype=float, repair=RoundingRepair()),
        )
        logger.info(
            f"Initialize MOEAD algorithm with n_gen={moead_config.n_gen}"
        )

        # Run MOEAD
        logger.info("Running MOEAD...")
        res = minimize(
            problem,
            algorithm,
            ("n_gen", moead_config.n_gen),
            seed=moead_config.seed,
            verbose=True,
        )

        # Return Pareto-Front solutions
        logger.info("Generate report...")
        report = []
        seen = set()
        for i, x in enumerate(res.X):
            selection_tuple = tuple(int(idx) for idx in x)
            obj_values = tuple(
                res.F[i][obj_id] if moead_config.objective[obj_name] == "sum_min" else -res.F[i][obj_id]
                for obj_id, (obj_name, obj_type) in enumerate(moead_config.objective.items())
            )
            dedup_key = (selection_tuple, obj_values)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            report.append(f"Solution {len(seen)}:")
            for idx, index in enumerate(x):
                var_name = moead_config.variable[idx]
                selected_item = moead_config.data[var_name][index]
                report.append(f"{var_name}: {selected_item['name']}")
            obj_id = 0
            for obj_name, obj_type in moead_config.objective.items():
                if obj_type == "sum_min":
                    report.append(f"total_{obj_name}: {res.F[i][obj_id]}")
                else:
                    report.append(f"total_{obj_name}: {-res.F[i][obj_id]}")
                obj_id += 1
            report.append("\n")
        report = "\n".join(report)
        return res, report

    def _format_data(self, data: str):
        """Generate formatted data from user's data snippet."""
        logger.info(f"Formatting data using {self.model}...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": GEN_FORMAT_DATA_PROMPT.format(data=data),
                },
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content

    def _gen_config(self, data: dict, user_prompt: str):
        """Generate MOEADConfig from user's prompt and formatted data."""
        data_snippet = []
        for key, value in data.items():
            value = value[0]
            data_snippet.append(f"{key}: {value}")
        data_snippet = "\n".join(data_snippet)
        logger.info(f"Generating MOEADConfig using {self.model}...")
        response = self.client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {
                    "role": "system",
                    "content": GEN_MOEAD_CONFIG_PROMPT.format(schema=MOEADConfigforLLM.model_json_schema()),
                },
                {
                    "role": "user",
                    "content": f"{user_prompt}\nMy data looks like:\n{data_snippet}",
                },
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    with open("data/data_set.json", "r") as f:
        data_set = json.load(f)

    user_prompt, user_data = data_set[0]["user_query"], str(data_set[0]["data_snippet"])
    optimizer = Text2MOEAD(
        api_key=os.getenv("QWEN_KEY"),
        base_url=os.getenv("QWEN_BASE_URL"),
        model="qwen-plus",
    )
    res, report = optimizer.run(user_prompt, user_data)
    print(report)
    pymoo_scatter = Scatter()
    pymoo_scatter.add(res.F).show()
