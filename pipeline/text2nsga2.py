import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from openai import OpenAI
from typing import Optional, Any
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from moea.nsga2 import NSGA2Config, NSGA2Problem
import matplotlib.pyplot as plt
from prompts.sys_prompts import GEN_NSGA2_CONFIG_PROMPT, GEN_FORMAT_DATA_PROMPT

import logging

logger = logging.getLogger("text2nsga2")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


class Text2NSGA2:
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
            logger.info(f"Formatting data...")
            data = self._format_data(user_data)
            data = json.loads(data)
        except Exception as e:
            print(e)
            return "Please provide data snippet for info extraction."
        # Generate NSGA2Config
        logger.info(f"Generating NSGA2Config...")
        config = self._gen_config(data, user_prompt)
        config = json.loads(config)

        # Setup NSGA2Problem
        nsga2_config = NSGA2Config(data=data, **config)
        objective = json.dumps(nsga2_config.objective, indent=4)
        constraints = json.dumps(nsga2_config.constraints, indent=4)
        logger.info(f"Objective:\n{objective}")
        logger.info(f"Constraints:\n{constraints}")

        logger.info(f"Setting up NSGA2Problem...")
        problem = NSGA2Problem(nsga2_config)
        algorithm = NSGA2(
            pop_size=nsga2_config.pop_size,
            sampling=IntegerRandomSampling(),
            crossover=SBX(prob=1.0, eta=3.0, vtype=float, repair=RoundingRepair()),
            mutation=PM(prob=1.0, eta=3.0, vtype=float, repair=RoundingRepair()),
            eliminate_duplicates=True,
        )
        logger.info(
            f"Initialize NSGA2 algorithm with pop_size={nsga2_config.pop_size}, n_gen={nsga2_config.n_gen}"
        )

        # Run NSGA2
        logger.info(f"Running NSGA2...")
        res = minimize(
            problem,
            algorithm,
            ("n_gen", nsga2_config.n_gen),
            seed=nsga2_config.seed,
            verbose=True,
        )

        # Return Pareto-Front solutions
        logger.info(f"Generate report...")
        report = []
        for i, x in enumerate(res.X):
            report.append(f"Solution {i+1}:")
            for idx, index in enumerate(x):
                var_name = nsga2_config.variable[idx]
                selected_item = data[var_name][index]
                report.append(f"{var_name}: {selected_item['name']}")
            obj_id = 0
            for obj_name, obj_type in nsga2_config.objective.items():
                if obj_type == "sum_min":
                    report.append(f"total_{obj_name}: {res.F[i][obj_id]}")
                else:
                    report.append(f"total_{obj_name}: {-res.F[i][obj_id]}")
                obj_id += 1
            report.append("\n")
        report = "\n".join(report)

        return res.X, report

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
        """Generate NSGA2Config from user's prompt and formatted data."""
        data_snippet = []
        for key, value in data.items():
            value = value[0]
            data_snippet.append(f"{key}: {value}")
        data_snippet = "\n".join(data_snippet)
        logger.info(f"Generating NSGA2Config using {self.model}...")
        response = self.client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {
                    "role": "system",
                    "content": GEN_NSGA2_CONFIG_PROMPT,
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
    optimizer = Text2NSGA2(
        api_key=os.getenv("QWEN_KEY"),
        base_url=os.getenv("QWEN_BASE_URL"),
        model="qwen-plus",
    )
    res, report = optimizer.run(user_prompt, user_data)
    print(report)
    plt.scatter(res[:, 0], res[:, 1])
    plt.show(block=True)
