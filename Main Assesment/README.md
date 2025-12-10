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
- [Adapting and Customising the Framework](#adapting-and-customising-the-framework)
  - [What You Can Change](#what-you-can-change)
  - [Adapting to a New Experiment](#adapting-to-a-new-experiment)

## Overview

This repository provides an automated system for optimising pipetting parameters on the Opentrons OT-2. Using a JMP-designed experiment, the system:

- Generates parameterised Opentrons protocols (Code A → Code B)
- Executes experiments on the robot
- Processes assay data (Code C)
- Identifies optimal settings using statistical modelling in JMP

JMP experiments can be designed from a long list of avaliable experiment parameters. Using only the JMP design-of-experiment output table, this repository automates production of unique serial dilution protocols with each of the parameter sets specified by JMP. Serial dilutions are then performed to dilute Fluorescein using a dilution medium such as PBS. The accuracy of each dilution can be evaluated by comparing measured fluorescence across the dilution to an expected dilution curve. This comparison is automatically processed by the Data Analysis Code C to give fitness data which can be reinput into the JMP table for analysis. 

We envision this platform being highly applicable to protocol optimisation. Some fluids have challenging properties, such as extreme viscosity or density, reduced surface tension, a tendency to foam, or the presence of particles, cells, or precipitated material. These properties can reduce the accuracy of automated protocols. By performing serial dilution optimisation using these fluids, optimal paramters for pipetting and mixing can be found which will alleviate these problems. 

The experiment execution code can also be altered to perform other pipetting workflows. By assigning our specific parameter names to the variables in a different experiment execution code, pipetting parameters can be optimised for other liquid-handling protocols which include pipetting and mixing steps. Optimised parameters can then be transferred to more complex workflows, allowing users to calibrate pipetting parameters using a simple model assay before applying it to their actual experiment.

## Optimisation workflow

### 1. Experimental Design (JMP)

JMP is used only to design the parameter combinations to test:

- Define the parameters you want to vary from 'Default_Params' (e.g. aspiration rate, dispense height, mixing reps)
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

To load a JMP design add the pathway of the CSV file to the generator Code A: 

- DESIGN_CSV = "Insert Pathway Here"

### 3. Experiment Execution (Code B)

This code is provided by the generator code A and is already formatted to run on the OT-2 system.

- Runs directly on the OT-2
- Loads specified labware and instruments
- Performs the parameterised pipetting workflow (aliquoting, dilution, mixing, etc.)
- Executes steps exactly as defined by Code A
- Produces assay-ready plates for analysis of pipetting accuracy

Prior to runnning the experiment the equipment should be laid out to match the code. To ensure correct pipetting:

- Pipette tips should be added to position 1.
- The resevoir wells should be added to position 2.
- The 96-well plate should be placed in position 3.
- The fluorescein should be added to column 1 of the resevoir.
- The dilution medium (e.g. PBS) should be added to column 6.

If specific labware and instruments are required, these can be changed in the generator code A to ensure they are maintained in all Code B outputs.

Code A was designed such that each output code B starts taking pipette tips from a different column in the tiprack, taking 3 columns of tip per dilution. Each protocol has an in-built start column parameter which indicates the first of the three columns used. This means that four protocols can be run before tips are reloaded. To check the start column, look for the value of the start_col parameter in the dictionary called 'PARAMS'.

### 4. Data Analysis (Code C)

- Imports fluorescence/absorbance data  
- Averages replicates and formats data  
- Fits dilution curves and calculates metrics (e.g., gradient, R²)  
- Outputs a results to a CSV
- This code is bespoke for our fluoresence machine, the arguments in the to_excel() function will need to be changed depending on the output layout.
- **NOTE: YOU MUST COLLECT THE RUNTIME DATA MANUALLY. THE OT-2 DOES NOT SUPPORT OUTPUTTING THE RUNTIME DATA**

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
  
  These are the available paramaters which can be optimised in JMP.
  
  You can tune:
  
  - global parameters: `Aspiration_Rate`, `Dispense_Rate`, `Aspiration_Height`, `Dispense_Height` set the defualt values of parameters not specified by JMP.
  - step-specific behaviour: `Aliquot_Aspiration_Rate`, `Dilution_Dispense_Rate`, `Mix_Aspiration_Height`.
  - mixing parameters: `Mixing_Repetitions`, `Mixing_Fraction`.
  - touch-tip parameters: `Touch_Tip_Speed`, `Touch_Tip_Radius`, `Touch_Tip_V_Offset` control the touch tip function that removes excess liquid from the pipette tip following mixing.

- **Protocol logic in `make_protocol_code()`**  
  
  The current function includes a template code which is specific to serial dilution.

  To use this framework for a different Opentrons protocol:

1. Edit the pipetting steps inside `make_protocol_code()` to implement your new workflow.  
2. Update `Default_Params` with any new parameters you want to optimise.  
3. Create a JMP design where the column names match the keys in `Default_Params`.  

