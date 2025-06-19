import os, json, random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

GEN_PROMPT = """
Help me generate 5 user's query with data snippet for real life multi-objective optimization problem.

<example>
User's query:
I want to find a best design for a car. The overall budget is 1000000 and I need to build it as fast as possible.
I got 20 different choices for the car engine, 15 choices for the car body, 10 choices for the car transmission, 60 choices for the car tires.
The data looks like this:

| car_engine | engine_attribute1 | engine_attribute2 | engine_attribute3 | engine_attribute4 | ...
| ---------- | ---------- | ---------- | ---------- | ---------- | ...
| engine_1   | value1        | value2        | value3        | value4        | ...
| engine_2   | value1        | value2        | value3        | value4        | ...
| ...        | ...        | ...        | ...        | ...        | ...
| car_body   | body_attribute1 | body_attribute2 | body_attribute3 | body_attribute4 | ...
| ...        | ...        | ...        | ...        | ...        | ...
| car_transmission   | transmission_attribute1 | transmission_attribute2 | transmission_attribute3 | transmission_attribute4 | ...
| ...        | ...        | ...        | ...        | ...        | ...
| car_tires   | tires_attribute1 | tires_attribute2 | tires_attribute3 | tires_attribute4 | ...
| ...        | ...        | ...        | ...        | ...        | ...
</example>

You can use your imagination to cover different multi-objective optimization scenarios in real life. Those problems might have mulitiple constraints or not.
The data snippet that user provide could be a table or some unstructured description of the data.

<Output JSON Schema>
{
    "user_query": "...",
    "data_snippet": "..."
}
</Output JSON Schema>
"""

SCENARIOS = ["Optimization for supply chain", "Efficient resource allocation", "Logistics Optimal Path Planning", "Optimal Product Design", "Project Staffing Planning"]
client = OpenAI(api_key=os.getenv("DS_KEY"), base_url=os.getenv("DS_BASE_URL"))

data_set = []
for scenario in SCENARIOS:
    for _ in range(5):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": GEN_PROMPT},
                {"role": "user", "content": f"Current scenario is: {scenario}"}
            ],
            temperature=1.0,
            seed=random.randint(0, 1000000),
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        data_set.append(data)

with open("data/data_set.json", "w") as f:
    json.dump(data_set, f, ensure_ascii=False, indent=4)

