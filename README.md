# Text2MOO
Using LLM generate config to call MOEAs to solve real life multi-objective problems

## Features

- **Text Input Processing**: Accept natural language descriptions of optimization requirements and raw data
- **LLM Integration**: Use LLM to parse user input and generate structured NSGA-II configurations
- **NSGA-II Optimization**: Execute multi-objective optimization using NSGA-II algorithm
- **Pareto Solutions**: Return Pareto-optimal solutions for multi-objective problems

## Project Structure

- `prompts/` - System prompts for LLM data formatting and config generation
- `pipeline/` - Text2NSGA2 pipeline connecting LLM with optimization algorithm
- `moea/` - NSGA-II algorithm implementation

## Current Implementation

The system currently supports:
- Converting text descriptions into NSGA-II problem configurations
- Processing raw data through LLM for structured formatting
- Running NSGA-II optimization with customizable parameters
- Handling multiple objectives and constraints
