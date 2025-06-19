# Text2MOO
Using LLM generate config to call MOEAs to solve real life multi-objective problems

## Features

- **Text Input Processing**: Accept natural language descriptions of optimization requirements and raw data
- **LLM Integration**: Use LLM to parse user input and generate structured NSGA-II configurations
- **NSGA-II Optimization**: Execute multi-objective optimization using NSGA-II algorithm
- **Pareto Solutions**: Return Pareto-optimal solutions for multi-objective problems

## Project Structure

- `prompts/` - System prompts for LLM data formatting and config generation
- `pipeline/` - Text2MOO pipelines connecting LLM with optimization algorithm
- `moea/` - MOEAs algorithm implementation

## Current Implementation

The system currently supports:
- Converting text descriptions into NSGA-II problem configurations
- Processing raw data through LLM for structured formatting
- Running NSGA-II optimization with customizable parameters
- Handling multiple objectives and constraints

## Test Result
```terminal
2025-06-19 18:32:28,556 - text2nsga2 - INFO - Formatting data...
2025-06-19 18:32:28,556 - text2nsga2 - INFO - Formatting data using qwen-plus...
2025-06-19 18:32:48,412 - text2nsga2 - INFO - Generating NSGA2Config...
2025-06-19 18:32:48,413 - text2nsga2 - INFO - Generating NSGA2Config using qwen-plus...
2025-06-19 18:33:02,499 - text2nsga2 - INFO - Objective:
{
    "cost": "sum_min",
    "delivery_time_days": "sum_min",
    "carbon_footprint_kg": "sum_min"
}
2025-06-19 18:33:02,500 - text2nsga2 - INFO - Constraints:
{
    "distance_from_supplier_km": {
        "type": "<=",
        "value": 500
    },
    "speed_km_per_h": {
        "type": ">=",
        "value": 40
    }
}
2025-06-19 18:33:02,501 - text2nsga2 - INFO - Setting up NSGA2Problem...
2025-06-19 18:33:02,504 - text2nsga2 - INFO - Initialize NSGA2 algorithm with pop_size=100, n_gen=50, constraint_penalty=1000000.0        
2025-06-19 18:33:02,505 - text2nsga2 - INFO - Running NSGA2...
==========================================================================================
n_gen  |  n_eval  | n_nds  |     cv_min    |     cv_avg    |      eps      |   indicator
==========================================================================================
     1 |       49 |     49 |  0.000000E+00 |  0.000000E+00 |             - |             -
WARNING: Mating could not produce the required number of (unique) offsprings!
     2 |       60 |     60 |  0.000000E+00 |  0.000000E+00 |  0.000000E+00 |             f
     3 |       60 |     60 |  0.000000E+00 |  0.000000E+00 |  0.000000E+00 |             f
2025-06-19 18:33:03,384 - text2nsga2 - INFO - Generate report...
Solution 1:
suppliers: S4
transportation_modes: T3
warehouse_locations: W1
total_cost: 5200.0
total_delivery_time_days: 4.0
total_carbon_footprint_kg: 210.0


Solution 2:
suppliers: S5
transportation_modes: T1
warehouse_locations: W2
total_cost: 4700.0
total_delivery_time_days: 8.0
total_carbon_footprint_kg: 170.0

...
```
![NSGA2 Optimization Results](assets\img\opt_scatter.png)
