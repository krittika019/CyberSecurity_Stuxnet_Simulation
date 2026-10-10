# Stuxnet-Inspired Cyber-Physical Simulation

A small, benign teaching simulation for the CA-2 Stuxnet case study (Group 2). It models a **fictional** rotating machine and shows how a change in controller logic can move a physical process variable, how an operator display (HMI) can look normal while this happens, and how an independent monitor can still detect it.

> **This is not Stuxnet.** It contains no malware, exploits, real PLCs, industrial protocols or network code. Every value in it is a fictional, arbitrary unit and does not represent any real facility.

## Project layout

| Folder | Contents |
|---|---|
| [01_Code/](01_Code/) | The simulation script, `requirements.txt`, and a [README](01_Code/README.md) with the full model description |
| [02_Results/](02_Results/) | `simulation_results.csv` (data for every step) and `simulation_summary.csv` (metrics for each experiment) |
| [03_Figures/](03_Figures/) | Figures 1–7: architecture, normal operation, target validation, process comparison, HMI vs monitor, detection, dashboard |
| [04_Report/](04_Report/) | Sections to add to the case-study report: method, implementation details, results and discussion |
| [05_Presentation/](05_Presentation/) | A short script for presenting the simulation (30–45 s) |
| [06_Validation/](06_Validation/) | An automated validation script, the checklist, and the saved output from the last run |

## Requirements

- Python 3.9 or later (tested with 3.12)
- numpy, pandas, matplotlib

No internet connection is needed at run time.

## How to run

From the project root:

```bash
cd 01_Code
pip install -r requirements.txt
python stuxnet_ics_concept_simulation.py
```

The run takes a few seconds. It writes the CSV files to `02_Results/` and the figures to `03_Figures/` (replacing the existing files), and prints a text dashboard.

| Option | Effect |
|---|---|
| `--seed N` | Uses a different random noise seed (default 42). The same seed always gives the same CSV output. |
| `--no-figures` | Writes only the CSV files |
| `--outroot DIR` | Writes outputs under `DIR/02_Results` and `DIR/03_Figures` instead of this project |

## Experiments

All four experiments use the same random noise, so they can be compared directly.

| Exp. | Scenario | Target validation | Max process deviation | HMI | Independent monitor |
|---|---|---|---|---|---|
| A | Normal operation | Not run | 1.27 % | Normal | Normal |
| B | Non-target controller (`CTRL-B`) | Failed | 1.27 % | Normal | Normal |
| C | Target matched, simulated change | Passed | 15.73 % | Anomaly visible after 7 steps | Anomaly after 7 steps |
| D | As C, with the HMI replaying normal values | Passed | 15.73 % | Normal (deviation stays at or below 1.11 %) | Anomaly after 7 steps |

These are the results for seed 42, taken from `02_Results/simulation_summary.csv`. An anomaly is flagged when a value differs from the expected value by more than 5 % for 3 steps in a row. This rule is an assumption made for the simulation, not an industrial standard.

**Takeaway:** in Experiment D, only the independent monitor detects the change. Securing the cyber layer is not enough; you also need an independent view of the physical process.

## Validation

```bash
python 06_Validation/run_validation.py
```

The script runs the simulation in a temporary folder and checks that:

- the code runs without errors and imports no network or ICS-protocol libraries
- two runs with the same seed give byte-identical results
- the scenario outcomes are as expected
- all figures exist
- the numbers quoted in the report match the simulation output

The last run passed all 29 checks (see [06_Validation/validation_output.txt](06_Validation/validation_output.txt)). One check compares the saved results with a fresh run using seed 42, so run the simulation with the default seed before validating.

## Scope

The simulation illustrates general security principles discussed in the report. It says nothing about how Stuxnet actually behaved physically, what happened at any real facility, or historical damage estimates. See [01_Code/README.md](01_Code/README.md) for the model equations and the full list of what is deliberately left out.
