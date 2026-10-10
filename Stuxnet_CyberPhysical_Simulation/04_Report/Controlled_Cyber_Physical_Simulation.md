# Controlled Cyber-Physical Simulation
*(Proposed new subsection, e.g. Section 4.4 of the report; figures numbered as in the simulation folder and renumbered on insertion.)*

**Objective.** The literature-based reconstruction concludes that the design intent of Stuxnet is well documented, whereas its physical effect is inferential and the process data seen by operators could be falsified (Stages 7–10; Sections 5.4–5.5). A small controlled simulation was built to illustrate these relationships in a safe setting. It is a Stuxnet-inspired conceptual simulation, not an implementation of Stuxnet, and it is not offered as evidence about the historical incident.

**Simulation architecture.** Figure 1 shows the chain engineering workstation → target validation → simulated PLC → process model, with two monitoring paths: an operator HMI (Path A) and an independent monitor with its own sensor (Path B). All elements are mathematical objects in one Python program; no real PLC, industrial protocol, Siemens software or network is involved.

**Assumptions.** The process is a fictional rotating machine in arbitrary units: target 1000, normal range 950–1050, first-order response with small random disturbances (seed 42). A normal controller sets `command = target_value`; the simulated change sets `command = altered_value` (1150) from step 100. Target validation is a conditional on two labels (`CTRL-A`/`TARGET`). Conceptual concealment makes the HMI array replay the last 50 normal samples. Detection flags a value deviating more than 5 % from the expected value for three consecutive steps; this rule is a simulation assumption, not an industrial standard.

**Scenarios and procedure.** Four experiments were run with identical random disturbances: (A) normal operation; (B) malicious condition present but controller `CTRL-B`/`NON-TARGET`, so validation fails; (C) validation passes and the simulated change is applied; (D) as C with conceptual concealment on the HMI path. For each, the program records validation result, controller state, process deviation, HMI result, independent-monitor result and detection delay (Table S1). All values come from the program output (`simulation_summary.csv`) and the run is reproducible.

**Table S1. Experiment results (fictional units).**

| Exp. | Target validation | Controller state | Max process deviation | HMI result | Independent monitor | Detection delay |
|---|---|---|---|---|---|---|
| A | not run | normal | 1.27 % | normal | normal | none |
| B | failed | normal | 1.27 % | normal | normal | none |
| C | passed | simulated change | 15.73 % | anomaly visible | anomaly | 7 steps |
| D | passed | simulated change | 15.73 % | normal | anomaly | 7 steps (monitor only) |

**Results.** In A the process stayed around 1000 (pre-activation mean 999.86) with no alarms. In B validation failed and the process output was identical to A. In C the process mean after step 100 was 1140.16 (final-50-step mean 1150.39), it spent 195 of 300 steps outside the normal range, and both paths flagged the anomaly 7 steps after the change. In D the true process was identical to C, but the HMI never exceeded a 1.11 % deviation and raised no flag, while the independent monitor, whose deviation reached 15.81 %, flagged the anomaly at the same 7-step delay.

**Interpretation.** The simulation illustrates, as general principles, that (1) target validation can confine an action to one configuration, (2) a controller-level change can propagate into a process variable, (3) a normal-looking operator display does not prove the process is normal, and (4) independent process monitoring can reveal discrepancies the operator interface does not. This agrees with the report's recommendation to base monitoring and safety functions on independent sensors [1].

**Limitations.** The process, values and controller are fictional and mathematical; no real protocol is used; concealment is conceptual; the 5 % rule is arbitrary. The results cannot establish what occurred at Natanz or validate any damage estimate, and they are not a reconstruction of Stuxnet's behaviour.

**Ethical and safety scope.** The code contains no malware, exploit, vulnerability, real PLC or Siemens software, network activity, propagation, persistence, command-and-control or credential access, and gives no operational attack capability. It runs offline on an ordinary laptop.

**Figure captions.**
- **Figure S1.** Conceptual architecture of the Stuxnet-inspired simulation: engineering workstation, target validation, simulated PLC, fictional process model, HMI (Path A) and independent monitor (Path B).
- **Figure S2.** Experiment A: normal operation of the fictional process (speed and temperature, arbitrary units) around the target of 1000.
- **Figure S3.** Controlled conceptual simulation of target validation: a non-target configuration (CTRL-B) leaves the process unchanged, whereas the target configuration (CTRL-A) permits the simulated controller change.
- **Figure S4.** Expected process (Experiment A) versus the simulated manipulated process (Experiment C), with the ±5 % simulated detection thresholds.
- **Figure S5.** Stuxnet-inspired conceptual concealment scenario: HMI value versus independent-monitor value for the same fictional process (Experiment D).
- **Figure S6.** Detection result: deviation of both monitoring paths in Experiment D and the detection outcome of each path in Experiments A–D.
- **Figure S7.** Text dashboard of the four experiments (supplementary).
