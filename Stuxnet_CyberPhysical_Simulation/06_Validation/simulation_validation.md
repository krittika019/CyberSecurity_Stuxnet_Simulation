# Simulation validation

Run date: 2026-10-08. Command: `python 06_Validation/run_validation.py` (full output saved in `validation_output.txt`). Result: **29 of 29 automated checks passed**.

## Checklist
| Check | Status | How verified |
|---|---|---|
| Code runs successfully | Pass | Fresh run into a temporary folder, exit code 0 |
| No external network required | Pass | Static scan: imports are only argparse, dataclasses, os, sys, numpy, pandas, matplotlib; no socket/http/requests/urllib. The run needs no internet. |
| No real malware involved | Pass | Source is arithmetic, one if-statement and array replay; no eval/exec/os.system/popen |
| No real PLC contacted | Pass | No ICS-protocol or hardware libraries imported (banned list includes snap7, pymodbus, opcua) |
| No exploit present | Pass | No vulnerability, payload or shellcode content; stated scope in docstring and README |
| All four scenarios work | Pass | A, B, C, D present in the summary and time-series CSVs |
| Target validation works | Pass | B: FAILED, controller NORMAL, process identical to A; C and D: PASSED |
| Normal scenario stable | Pass | A: maximum deviation 1.27 %, 0 steps outside 950–1050, no alarms (no false positive) |
| Manipulated scenario gives measurable deviation | Pass | C: maximum deviation 15.73 %, 195 steps outside range, process identical to A before step 100 |
| Concealment behaves as intended | Pass | D: true process identical to C; HMI deviation never above 1.11 % with 0 flags |
| Independent monitor detects the simulated anomaly | Pass | C and D flagged 7 steps after the change (max monitor deviation in D 15.81 %) |
| Graphs generated | Pass | Figures 1–6 required plus Figure 7 (dashboard), all non-empty; visually inspected for overlaps (two label overlaps in Figures 5 and 6 were fixed) |
| CSV results generated | Pass | `simulation_results.csv` (1200 rows) and `simulation_summary.csv` (4 rows) |
| No NaN / undefined values | Pass | Checked in both CSVs; undefined detection delays are written as the text "none" |
| Results reproducible | Pass | Two independent runs give an identical SHA-256 of the results CSV; the saved file equals a fresh run |
| Figure labels readable | Pass | Inspected at full resolution; serif fonts 9–14 pt, footnote on every figure states "fictional; not Stuxnet" |
| Report text matches simulation output | Pass | Nine numbers and the 7-step delay in the report files are checked programmatically against the data |
| No result invented | Pass | Every figure/number is computed by the program; none typed by hand into results |
| Limitations clearly stated | Pass | In the report files, README and figure footnotes |
| Stuxnet facts not mixed with simulation results | Pass | Results_Discussion file has separate "SIMULATION RESULT" and "REAL STUXNET EVIDENCE" sections; evidence grades are quoted from the existing report and not changed |

## Notes and honest caveats
- Experiments A and B share the same random disturbances (paired design), so their process output is identical; this is intentional, not a bug.
- The independent monitor's maximum deviation (15.81 %) is slightly above the process's (15.73 %) because the monitor adds its own sensor noise.
- The results depend on assumed parameters (plant response 0.08, 5 % rule, 3-step debounce, seed 42). Running other seeds will change small numbers (for example the 7-step delay), not the qualitative behaviour. Only seed 42 is reported.
- The simulation was run in the sandbox. It uses standard libraries only and should run on a student laptop, but I have not run it on your machine.
- The existing final report, deck and script were not modified.
