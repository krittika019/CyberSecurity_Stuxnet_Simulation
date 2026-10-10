# Results and Discussion — proposed addition
*(Suggested as Section 5.10, "Controlled simulation results"; it keeps simulation results apart from the evidence about the real incident.)*

## SIMULATION RESULT (fictional process, arbitrary units, seed 42)

**Normal baseline (Experiment A).** The process stayed around the target of 1000 (pre-activation mean 999.86, maximum deviation 1.27 %, no steps outside the 950–1050 range). Neither monitoring path raised an alarm, so the 5 % rule produced no false positives in this run.

**Target validation (Experiment B).** The controller `CTRL-B` was configured `NON-TARGET`. Validation failed, the controller stayed in its normal state, and the process output was identical to Experiment A. In the model, a conditional on configuration is enough to confine the simulated change to one controller.

**Simulated controller manipulation and process deviation (Experiment C).** With `CTRL-A`/`TARGET`, validation passed and the command changed from 1000 to 1150 at step 100. The process mean after step 100 was 1140.16 (final-50-step mean 1150.39), the maximum deviation was 15.73 %, the temperature peaked at 56.14 against about 50 in normal operation, and 195 of 300 steps lay outside the normal range. Because no concealment was applied, the HMI showed the deviation and flagged it 7 steps after the change.

**Concealment and independent detection (Experiment D).** The true process was identical to Experiment C. With the conceptual concealment condition, the HMI replayed earlier normal samples: its deviation never exceeded 1.11 % and it raised no flag. The independent monitor, which uses its own sensor, reported deviations up to 15.81 % and flagged the anomaly 7 steps after the change.

| Exp. | Target validation | HMI result | Independent monitor | Detected by |
|---|---|---|---|---|
| A | not run | normal | normal | none (no anomaly present) |
| B | failed | normal | normal | none (no anomaly present) |
| C | passed | anomaly visible | anomaly | HMI path and independent monitor |
| D | passed | normal | anomaly | independent monitor only |

*The 7-step delay is a product of the assumed plant response, the 5 % threshold and a 3-step debounce; it is not a real-world detection time.*

## What the simulation demonstrates
- Target validation can restrict a simulated action to a specific configuration.
- A controller-level change can propagate into a simulated process variable.
- A normal-looking operator display does not necessarily show that the process is normal.
- An independent measurement path can detect discrepancies that are not visible at the operator interface, so process-aware monitoring should complement cyber-layer monitoring.

## What it does NOT demonstrate
It does not show how Stuxnet behaved physically, what its code did, what happened at Natanz, how much damage occurred, or how real PLCs, drives or HMIs behave. It does not test any real detection product. The model is deliberately simple and the thresholds are arbitrary, so the numbers have no meaning outside the model.

## REAL STUXNET EVIDENCE (from the literature review, unchanged)
This subsection is separate from the simulation. The documented facts remain those graded in Section 5.4: the Step 7 library replacement and controller target checks (Grade A), the process-level analysis of attack routines and replay of normal process values reported by Langner (Grade B), the inferred link to about 1,000 removed centrifuges (Grade C, contested), and the press claims of large impact and American and Israeli authorship (Grade D) [2], [4], [16], [17], [19], [32]. The simulation adds no new evidence to these grades; it only illustrates, in a fictional setting, why independent process monitoring is recommended (Section 5.8).

## Limitations
- The process is fictional and its values are illustrative.
- The controller is a mathematical function, not a real PLC.
- The simulation does not reproduce Stuxnet, and no real industrial protocol is used.
- Concealment is conceptual: it replays numbers inside the program and does not model Stuxnet's actual mechanism.
- Results cannot establish what physically occurred at Natanz or validate historical damage estimates.
- The 5 % detection rule and the 3-step debounce are simulation assumptions, and one noise seed (42) was used for the reported run.
- The simulation demonstrates security principles, not historical facts.
