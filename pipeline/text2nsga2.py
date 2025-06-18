import json
from openai import OpenAI
from typing import Optional
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from moea.nsga2 import NSGA2Config, NSGA2Problem
from prompts.sys_prompts import GEN_NSGA2_CONFIG_PROMPT, GEN_FORMAT_DATA_PROMPT


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
            data = self._format_data(user_data)
            data = json.loads(data)
        except Exception as _:
            return "Please provide data snippet for info extraction."
        # Generate NSGA2Config
        config = self._gen_config(data, user_prompt)
        config = json.loads(config)
        # Setup NSGA2Problem
        nsga2_config = NSGA2Config(data=data, **config)
        problem = NSGA2Problem(nsga2_config)
        algorithm = NSGA2(
            pop_size=nsga2_config.pop_size,
            sampling=IntegerRandomSampling(),
            crossover=SBX(prob=1.0, eta=3.0, vtype=float, repair=RoundingRepair()),
            mutation=PM(prob=1.0, eta=3.0, vtype=float, repair=RoundingRepair()),
            eliminate_duplicates=True,
        )
        # Run NSGA2
        res = minimize(
            problem,
            algorithm,
            ("n_gen", nsga2_config.n_gen),
            seed=nsga2_config.seed,
            verbose=True,
        )
        # Return Pareto-Front solutions
        return res.X

    def _format_data(self, data: str):
        """Generate formatted data from user's data snippet."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": GEN_FORMAT_DATA_PROMPT.format(data=data),
                },
            ],
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content

    def _gen_config(self, data: dict, user_prompt: str):
        """Generate NSGA2Config from user's prompt and formatted data."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": GEN_NSGA2_CONFIG_PROMPT.format(data=data),
                },
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content
