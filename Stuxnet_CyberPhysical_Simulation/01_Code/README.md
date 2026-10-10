# Benign Stuxnet-Inspired ICS Cyber-Physical Simulation

**Conceptual ICS Simulation Inspired by the Stuxnet Attack Chain** (CA-2 case study, Group 2).

> This is **not** Stuxnet and does **not** reproduce it. It is a small, purely mathematical teaching simulation of a *fictional* rotating machine. *This process model is fictional and does not represent the physical parameters of any real industrial facility.*

## What it demonstrates
Target validation → simulated controller-logic change → process-variable deviation → operator/HMI visibility → independent anomaly detection, and the difference between what a cyber-layer display reports and what a process-layer monitor measures.

## Run
```
pip install -r requirements.txt        # numpy, pandas, matplotlib (no internet needed at run time)
python stuxnet_ics_concept_simulation.py            # default seed 42
python stuxnet_ics_concept_simulation.py --seed 7   # other noise realisation
python stuxnet_ics_concept_simulation.py --no-figures
```
Outputs: `../02_Results/simulation_results.csv` (per-step data), `../02_Results/simulation_summary.csv` (per-experiment metrics), `../03_Figures/figure_1…7_*.png`, and a text dashboard on screen. Runs in a few seconds on an ordinary laptop. With the same seed the CSV output is byte-identical (checked by `../06_Validation/run_validation.py`).

## Model (all values fictional, arbitrary units)
| Item | Value |
|---|---|
| Target speed / normal range | 1000 / 950–1050 |
| Plant | first-order lag, `x += 0.08·(command − x) + noise` (σ = 2) |
| Temperature | simple lag toward `50 + 0.04·(x − 1000)` |
| Normal controller | `command = target_value` (1000) |
| Simulated change | `command = altered_value` (1150) from step 100 |
| Target validation | plain conditional: controller ID `CTRL-A` and configuration `TARGET` |
| Path A (HMI) | controller's own sensor value (+noise) |
| Path B (independent monitor) | separate sensor of the true process value (+noise) |
| Conceptual concealment (Exp. D) | after step 100 the HMI array replays the last 50 recorded normal samples |
| Detection rule | `abs(value − expected)/expected > 5 %` for 3 consecutive steps |

The 5 % rule, the 3-step debounce and every number above are **simulation assumptions**, not industrial standards and not Stuxnet facts. The same random noise is used in every experiment so comparisons are paired (hence Experiments A and B give identical process output).

## Experiments
A normal operation · B target validation failed (`CTRL-B`, `NON-TARGET`) · C target matched + simulated manipulation · D = C + conceptual concealment + independent monitoring.

## Safety and scope — what is NOT in this code
No malware, exploit, vulnerability, Siemens software, real PLC or real industrial protocol; no network access, propagation, persistence, command-and-control, credential access or evasion; no real process or centrifuge parameters; no operational attack capability. The "malicious condition" is an if-statement over two labels, the "controller" is one line of arithmetic, and the "concealment" is an array replay inside the program. `../06_Validation/run_validation.py` statically checks that the code imports no network, process or ICS-protocol libraries.

## What it does and does not show
It illustrates general principles discussed in the report. It says **nothing** about how Stuxnet physically behaved, what happened at any facility, or the historical damage estimates.
