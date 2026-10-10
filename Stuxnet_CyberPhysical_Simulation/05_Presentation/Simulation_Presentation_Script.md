# Presentation explanation — benign simulation (30–45 s)

**Spoken text (about 90 words, roughly 40 s at 130 words per minute):**

"We also built a small, completely benign simulation to illustrate the cyber-to-physical idea from our case study. We didn't reproduce Stuxnet, and there's no real PLC or malware involved. It's a fictional machine, and the simulated controller only changes one number. A non-target controller stays normal. When the target matches, the process drifts about fifteen percent. With the display replaying normal values, the operator view stays quiet, but the independent monitor flags the anomaly within seven steps. The takeaway is that protecting the cyber layer isn't enough; we also need independent visibility into the physical process."

**Shorter 30-second cut (about 70 words):** "We also built a small, completely benign simulation. It's a fictional machine, not Stuxnet and not a real PLC. When the simulated target matched, the process drifted about fifteen percent. With the operator display replaying normal values, only an independent monitor flagged it, within seven steps. So protecting the cyber layer alone isn't enough; we need visibility into the physical process too."

**Numbers used (all from `simulation_summary.csv`):** maximum process deviation 15.73 %; detection 7 steps after the change; HMI deviation in Experiment D never above 1.11 %.

**Fit with the existing talk (important).** The current script is 960 words (about 7:41 at 125 wpm). Adding this paragraph (about 90 words) would push it to about 8:10 to 8:25, which is over the 8:00 limit. Options: (1) keep this for the Q&A and use it as an answer to "did you test anything?"; (2) use the 30-second cut and remove the same amount from slides 5 and 9; (3) show Figure S5 as a backup slide and mention it only if asked. Option 1 is the safest. Do not describe the simulation as a "Stuxnet simulation" unless you say "Stuxnet-inspired conceptual simulation".

**Suggested slide placement if used:** a single backup slide with Figure S5 (HMI vs independent monitor), captioned "Stuxnet-inspired conceptual simulation; fictional process".
