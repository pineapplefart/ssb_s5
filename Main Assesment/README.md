# Optimising Serial Dilution Protocol Parameters for Opentrons OT-2
### A Generalised Pipeline for Automated Experiment Optimisation Using Opentrons + JMP

## Authors
- Matthew Groves
- Wilson Porteus
- Haotong Xiong

## Table of contents 

- [Overview](#overview)
- [Optimisation Workflow](#optimisation-workflow)
  - [1. Experimental Design (JMP)](#1-experimental-design-jmp)
  - [2. Protocol Generation (Code A)](#2-protocol-generation-code-a)
  - [3. Experiment Execution (Code B)](#3-experiment-execution-code-b)
  - [4. Data Analysis (Code C)](#4-data-analysis-code-c)
  - [5. Optimisation in JMP](#5-optimisation-in-jmp)
- [Code Structure](#code-structure)
  - [What You Can Change](#what-you-can-change)
  - [What You Should NOT Change](#what-you-should-not-change)
  - [How to Add New Parameters](#how-to-add-new-parameters)
  - [How to Adapt This to a Different Experiment](#how-to-adapt-this-to-a-different-experiment)
- [Using JMP With This Framework](#using-jmp-with-this-framework)
- [Repository Structure](#repository-structure)
- [Conclusion](#conclusion)

## Overview

This repository provides a complete, automated pipeline for optimising pipetting parameters on the Opentrons OT-2. Using a JMP-designed experiment, the system:

- Generates parameterised Opentrons protocols (Code A → Code B)
- Executes experiments on the robot
- Processes assay data (Code C)
- Identifies optimal settings using statistical modelling in JMP

Serial dilution is used as the demonstration case, but the pipeline is designed to be experiment-agnostic. By modifying only the protocol template inside the generator, users can adapt the system to optimise any liquid-handling workflow, including reagent mixing, plate normalisation, or multi-step assays. The framework supports flexible parameter definition, scalable protocol generation, and quantitative performance evaluation (e.g., gradient, R², execution time). Optimised parameters can then be transferred to more complex or sensitive workflows, allowing users to calibrate pipetting behaviour using a simple model assay before applying it to their actual experiment.

## Optimisation workflow

### 1. Experimental Design (JMP)

JMP is used only to design the parameter combinations to test:

- Define the parameters you want to vary (e.g. aspiration rate, dispense height, mixing reps)
- Build a DOE (e.g. factorial, screening, response surface)
- Export as `.csv` or `.txt` for the generator script

*Note: The names of the columns must match the keys in `Default_Params`.*

### 2. Protocol Generation (Code A)

Code A reads the JMP design and produces **one Opentrons protocol per row** in the design file.

It automatically:

- Loads the JMP design file  
- Loads default pipetting parameters (`Default_Params`)  
- Overrides defaults with values from each design row  
- Fills missing parameter values
- Embeds parameters into a protocol template  
- Generates one Opentrons execution script (Code B) per experiment, which are ready to run on the OT-2

### 3. Experiment Execution (Code B)

- Runs directly on the OT-2
- Loads specified labware and instruments
- Performs the parameterised pipetting workflow (aliquoting, dilution, mixing, etc.)
- Executes steps exactly as defined by Code A
- Produces assay-ready plates for analysis

### 4. Data Analysis (Code C)

- Imports fluorescence/absorbance data  
- Averages replicates and formats data  
- Fits dilution curves and calculates metrics (e.g., gradient, R²)  
- Outputs a results CSV for JMP

### 5. Optimisation in JMP
In JMP, users can:
- Import results from Code C
- Fit statistical models to quantify parameter effects
- Explore prediction profiles
- Use desirability functions to identify optimal parameter settings  
- Select final conditions for validation on the OT-2  

## Adapting and Customising the Framework

This optimisation pipeline is not limited to serial dilution. With small changes, it can be used for any pipetting-based experiment on the Opentrons OT-2.

### What You Can Change

- **`Default_Params`**  
  Add, remove, or adjust parameters to control different aspects of pipetting.  
  For example, you can tune:
  - global defaults: `Aspiration_Rate`, `Dispense_Rate`, `Aspiration_Height`, `Dispense_Height`
  - step-specific behaviour: `Aliquot_Aspiration_Rate`, `Dilution_Dispense_Rate`, `Mix_Aspiration_Height`, etc.
  - mixing: `Mixing_Repetitions`, `Mixing_Fraction`
  - touch-tip: `Touch_Tip_Speed`, `Touch_Tip_Radius`, `Touch_Tip_V_Offset`

  Any parameter you add here can be included as a column in the JMP design file and will override the default value for that experiment.

- **Protocol logic in `make_protocol_code()`**  
  This is the experiment-specific part.  
  To optimise a different workflow (e.g. mixing, plate normalisation, reactions), replace the serial dilution steps with your own protocol while still reading values from `PARAMS["..."]`.

- **Analysis script (Code C)**  
  Only needed if your experiment produces different outputs (e.g. endpoint fluorescence, OD, reaction rate) or you want to calculate different metrics.

### Adapting to a New Experiment

To use this framework for a different Opentrons protocol:

1. Edit the pipetting steps inside `make_protocol_code()` to implement your new workflow.  
2. Update `Default_Params` with any new parameters you want to optimise.  
3. Create a JMP design where the column names match the keys in `Default_Params`.  
4. Update Code C (if required) to calculate new performance metrics.
