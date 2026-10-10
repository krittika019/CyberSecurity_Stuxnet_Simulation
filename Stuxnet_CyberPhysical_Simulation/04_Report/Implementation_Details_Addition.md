# Implementation Details — proposed addition
*(Suggested as a new Section 4.4 "Controlled conceptual simulation"; do not replace the existing Section 4 text, which states that nothing was run or tested against the malware. This addition qualifies "no experiments" as described below.)*

In addition to the literature-based reconstruction, a controlled conceptual simulation was developed to demonstrate the relationship between controller-level manipulation and process-level anomaly detection. **The simulation is an implementation of the analytical cyber-physical model developed in this study, not an implementation of Stuxnet.** It does not reproduce Stuxnet, any Stuxnet component, or any real industrial-control configuration.

The program (`stuxnet_ics_concept_simulation.py`, Python with NumPy, pandas and Matplotlib) models a fictional rotating machine in arbitrary units. It contains five elements: a simulated controller that outputs a command, a one-line conditional standing in for target validation, a first-order process model, an operator HMI path, and an independent monitor path with its own sensor. A "simulated change" replaces the controller's command with a fictional altered value, and a "conceptual concealment" condition makes the HMI array replay earlier normal-looking samples. Both are plain arithmetic and array operations inside the program.

The following were deliberately not implemented: malware or exploit code, any Windows or Siemens vulnerability, communication with a real or emulated PLC, industrial protocols, network activity, propagation, persistence, command-and-control, credential access, evasion of real security products, and any real process or centrifuge parameters. The code uses a fixed random seed, writes its results to CSV files and generates all figures itself, and runs offline on an ordinary laptop. A separate validation script re-runs it, checks reproducibility and scans the source for network, process and ICS-protocol libraries.

The earlier statement that no measurements were taken and that nothing was run against the malware remains true. The only quantities reported from this component are outputs of the fictional model, and they are presented separately from the evidence about Stuxnet itself.

**Mapping to the ten-stage model (conceptual only).**

| Report stage | Simulation element | What is and is not represented |
|---|---|---|
| 5–6 Engineering workstation / industrial software | "Engineering Workstation" box feeding the simulated PLC | Role only; no software, library or protocol is modelled |
| 7 Target validation | Conditional on controller ID and configuration | Illustrates selectivity; not the real checks |
| 8 Controller manipulation | `command = altered_value` | One arithmetic change; no code blocks or real logic |
| 9 Physical effect | Process-variable deviation | Fictional deviation, not a damage model |
| 10 Concealment | HMI replay of recorded samples | Conceptual principle only; not the real mechanism |
