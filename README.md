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
2025-06-19 15:32:57,947 - text2nsga2 - INFO - Formatting data...
2025-06-19 15:32:57,948 - text2nsga2 - INFO - Formatting data using qwen-plus...
2025-06-19 15:33:28,702 - text2nsga2 - INFO - Generating NSGA2Config...
2025-06-19 15:33:28,702 - text2nsga2 - INFO - Generating NSGA2Config using qwen-plus...
2025-06-19 15:33:45,727 - text2nsga2 - INFO - Objective:
{
    "carbon_footprint_kg": "sum_min",
    "carbon_footprint_kg_per_km": "sum_min",
    "speed_km_per_h": "sum_max"
}
2025-06-19 15:33:45,728 - text2nsga2 - INFO - Constraints:
{
    "cost": {
        "type": "<=",
        "value": 10000
    },
    "delivery_time_days": {
        "type": "<=",
        "value": 7
    },
    "distance_from_supplier_km": {
        "type": "<=",
        "value": 200
    }
}
2025-06-19 15:33:45,730 - text2nsga2 - INFO - Setting up NSGA2Problem...
2025-06-19 15:33:45,734 - text2nsga2 - INFO - Initialize NSGA2 algorithm with pop_size=100, n_gen=50, constraint_penalty=1000000.0        
2025-06-19 15:33:45,734 - text2nsga2 - INFO - Running NSGA2...
==========================================================================================
n_gen  |  n_eval  | n_nds  |     cv_min    |     cv_avg    |      eps      |   indicator
==========================================================================================
     1 |       49 |     10 |  0.000000E+00 |  2.040816E+05 |             - |             -
WARNING: Mating could not produce the required number of (unique) offsprings!
     2 |       60 |     12 |  0.000000E+00 |  2.000000E+05 |  0.000000E+00 |             f
     3 |       60 |     12 |  0.000000E+00 |  2.000000E+05 |  0.000000E+00 |             f
2025-06-19 15:33:46,461 - text2nsga2 - INFO - Generate report...
Solution 1:
suppliers: S2
transportation_modes: T3
warehouse_locations: W3
total_carbon_footprint_kg: 180.0
total_carbon_footprint_kg_per_km: 0.35
total_speed_km_per_h: 70.0


Solution 2:
suppliers: S2
transportation_modes: T3
warehouse_locations: W1
total_carbon_footprint_kg: 180.0
total_carbon_footprint_kg_per_km: 0.35
total_speed_km_per_h: 70.0

...
```