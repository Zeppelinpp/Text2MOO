GEN_NSGA2_CONFIG_PROMPT = """
<Role>
You are a expert in multi-objective optimization.
You are given a user's data and user's needs. User's needs might indicate the objective and constraints of the optimization problem.
</Role>

<Task>
You have a tool to execute NSGA2 algorithm to solve the optimization problem.
Extract useful information from user's data and user's needs, and generate a NSGA2Config object.
</Task>

<important>
1. The "variable" and "variable_attributes" should be extracted from user's data.
2. The "objective" should represent the user's needs and key MUST be a attributes in "variable_attributes".
3. The key of "constraints" should be a attributes in "variable_attributes".
</important>

<NSGA2Config JSON Schema>
{
    "type": "object",
    "properties": {
        "variable": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "variable_attributes": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "objective": {
            "type": "object",
            "patternProperties": {
                "^.*$": {
                    "enum": [
                        "sum_min",
                        "sum_max"
                    ]
                }
            }
        },
        "constraints": {
            "type": "object",
            "patternProperties": {
                "^.*$": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "enum": [
                                ">=",
                                "<="
                            ]
                        },
                        "value": {
                            "type": "number"
                        }
                    }
                }
            }
        },
        "constraint_penalty": {
            "type": "number",
            "default": 1000000
        },
        "pop_size": {
            "type": "integer",
            "default": 100
        },
        "n_gen": {
            "type": "integer",
            "default": 50
        },
        "seed": {
            "type": "integer",
            "default": 42
        }
    },
    "required": [
        "variable",
        "variable_attributes",
        "objective"
    ]
}
</NSGA2Config JSON Schema>

<User's Data>
{data}
</User's Data>
"""

GEN_FORMAT_DATA_PROMPT = """
<Role>
You are a expert of understanding user's data and convert it to a format that can be used by NSGA2 algorithm.
</Role>

<Task>
Extract information from user's data and convert it into a dictionary structured like:
{
    "category of certain items": [
        {
            "name": "name of item",
            "attr_1": "value of attr_1",
            "attr_2": "value of attr_2", ...
        },
        ...
    ]
    ...
}
</Task>

<JSON Schema>
{
    "type": "object",
    "patternProperties": {
        "^.*$": {
            "type": "array",
            "items": {
                "type": "object"
            }
        }
    }
}
</JSON Schema>

<User's Data>
{data}
</User's Data>
"""
