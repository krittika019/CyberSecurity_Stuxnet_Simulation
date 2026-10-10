#!/usr/bin/env python3
"""
Benign Stuxnet-Inspired ICS Cyber-Physical Simulation
=====================================================

A conceptual, purely mathematical teaching simulation for the CA-2 Stuxnet
case study. It illustrates the security PRINCIPLE that a controller-level
change can propagate into a physical process variable, that an operator
display need not prove the process is normal, and that an independent
measurement path can expose the discrepancy.

SAFETY / SCOPE (read before running)
------------------------------------
* This is NOT Stuxnet and does NOT reproduce Stuxnet or any malware.
* No exploit, no vulnerability, no Siemens software, no real PLC, no real
  industrial protocol, no network access of any kind.
* No propagation, persistence, command-and-control, credential access or
  operational attack capability. The "malicious condition" is an ordinary
  if-statement over fictional labels; the "controller" is one line of
  arithmetic; the "concealment" is an array that replays earlier numbers.
* The process model is fictional and does not represent the physical
  parameters of any real industrial facility. All values are arbitrary units.

Usage:  python stuxnet_ics_concept_simulation.py [--seed 42] [--no-figures]
Outputs go to ../02_Results and ../03_Figures (relative to this file).
"""
import argparse
import os
import sys
from dataclasses import dataclass

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Fictional simulation parameters (arbitrary units; educational only)
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class Params:
    steps: int = 300              # simulated time steps (arbitrary time units)
    activation_step: int = 100    # step at which the simulated change takes effect
    target_value: float = 1000.0  # normal commanded/target speed (arbitrary units)
    altered_value: float = 1150.0 # fictional altered command (+15 %)
    normal_low: float = 950.0     # fictional normal operating range
    normal_high: float = 1050.0
    plant_gain: float = 0.08      # first-order lag: x += gain * (command - x)
    process_noise: float = 2.0    # std. dev. of process disturbance
    sensor_noise: float = 2.0     # std. dev. of each sensor path
    temp_start: float = 50.0      # fictional process temperature (arbitrary units)
    temp_coeff: float = 0.04      # equilibrium temp rises with speed above target
    temp_gain: float = 0.10
    threshold: float = 0.05       # SIMULATION ASSUMPTION: 5 % deviation rule
    consecutive: int = 3          # consecutive exceedances needed (debounce)
    replay_len: int = 50          # length of recorded "normal" buffer (scenario D)


TARGET_ID, TARGET_CFG = "CTRL-A", "TARGET"   # fictional labels

EXPERIMENTS = [
    # name, title, controller id, configuration, malicious condition present, concealment
    ("A", "Normal operation",                              "CTRL-A", "TARGET",     False, False),
    ("B", "Target validation failed",                      "CTRL-B", "NON-TARGET", True,  False),
    ("C", "Target matched + simulated manipulation",       "CTRL-A", "TARGET",     True,  False),
    ("D", "Target matched + manipulation + concealment",   "CTRL-A", "TARGET",     True,  True),
]


# ----------------------------------------------------------------------------
# Simulation core
# ----------------------------------------------------------------------------
def target_validation(controller_id, config):
    """Fictional configuration check: a plain conditional on two labels."""
    return controller_id == TARGET_ID and config == TARGET_CFG


def first_detection(flags, consecutive):
    """Index of the step at which `consecutive` flagged samples in a row complete,
    or None if that never happens."""
    run = 0
    for i, f in enumerate(flags):
        run = run + 1 if f else 0
        if run >= consecutive:
            return i
    return None


def run_experiment(exp, p, noise):
    name, title, cid, cfg, malicious, conceal = exp
    if malicious:
        validation = "PASSED" if target_validation(cid, cfg) else "FAILED"
    else:
        validation = "NOT RUN"
    changed = validation == "PASSED"
    controller_state = "SIMULATED CHANGE" if changed else "NORMAL"

    n = p.steps
    command = np.full(n, p.target_value)
    actual = np.zeros(n)
    temp = np.zeros(n)
    x, tmp = p.target_value, p.temp_start
    for t in range(n):
        # controller logic: normal = target_value ; simulated change = altered_value
        command[t] = p.altered_value if (changed and t >= p.activation_step) else p.target_value
        x = x + p.plant_gain * (command[t] - x) + noise["proc"][t]
        t_eq = p.temp_start + p.temp_coeff * (x - p.target_value)
        tmp = tmp + p.temp_gain * (t_eq - tmp)
        actual[t], temp[t] = x, tmp

    # Path A: value the operator HMI receives from the controller's own sensor
    hmi_true = actual + noise["hmi"]
    hmi = hmi_true.copy()
    if conceal:
        # CONCEPTUAL concealment: after activation the display shows previously
        # recorded normal-looking samples (array replay). Not any real mechanism.
        buf = hmi_true[p.activation_step - p.replay_len:p.activation_step].copy()
        for t in range(p.activation_step, n):
            hmi[t] = buf[(t - p.activation_step) % p.replay_len]
    # Path B: independent process monitor with its own sensor
    mon = actual + noise["mon"]

    expected = p.target_value
    hmi_dev = np.abs(hmi - expected) / expected
    mon_dev = np.abs(mon - expected) / expected
    hmi_flag, mon_flag = hmi_dev > p.threshold, mon_dev > p.threshold
    hmi_det = first_detection(hmi_flag, p.consecutive)
    mon_det = first_detection(mon_flag, p.consecutive)

    post = slice(p.activation_step, n)
    act_dev = np.abs(actual - expected) / expected
    out_of_range = (actual < p.normal_low) | (actual > p.normal_high)

    def delay(i):
        return "none" if i is None else int(i - p.activation_step)

    if mon_det is not None and hmi_det is not None:
        detected_by = "HMI path and independent monitor"
    elif mon_det is not None:
        detected_by = "independent monitor only"
    elif hmi_det is not None:
        detected_by = "HMI path only"
    else:
        detected_by = "none"

    summary = dict(
        experiment=name, scenario=title, controller_id=cid, configuration=cfg,
        target_validation=validation, controller_state=controller_state,
        conceptual_concealment="ON" if conceal else "OFF",
        baseline_mean_pre_activation=round(float(actual[:p.activation_step].mean()), 2),
        process_mean_post_activation=round(float(actual[post].mean()), 2),
        process_mean_final_50_steps=round(float(actual[-50:].mean()), 2),
        max_process_deviation_pct=round(float(act_dev[post].max() * 100), 2),
        max_process_temperature=round(float(temp.max()), 2),
        steps_outside_normal_range=int(out_of_range.sum()),
        hmi_final_mean_10=round(float(hmi[-10:].mean()), 2),
        monitor_final_mean_10=round(float(mon[-10:].mean()), 2),
        detection_threshold_pct=p.threshold * 100,
        hmi_result="ANOMALY VISIBLE" if hmi_det is not None else "NORMAL",
        hmi_detection_delay_steps=delay(hmi_det),
        monitor_result="ANOMALY" if mon_det is not None else "NORMAL",
        monitor_detection_delay_steps=delay(mon_det),
        anomaly_detected_by=detected_by,
        security_status="SIMULATED ANOMALY" if mon_det is not None else "SAFE",
    )
    series = pd.DataFrame(dict(
        experiment=name, step=np.arange(n), command=command, actual_speed=actual,
        temperature=temp, hmi_displayed=hmi, independent_monitor=mon,
        expected=expected, hmi_deviation_pct=hmi_dev * 100,
        monitor_deviation_pct=mon_dev * 100,
        hmi_flag=hmi_flag.astype(int), monitor_flag=mon_flag.astype(int)))
    return summary, series, dict(hmi_det=hmi_det, mon_det=mon_det)


def make_noise(p, seed):
    """Same random disturbances for every experiment (paired comparison)."""
    rng = np.random.default_rng(seed)
    return dict(proc=rng.normal(0, p.process_noise, p.steps),
                hmi=rng.normal(0, p.sensor_noise, p.steps),
                mon=rng.normal(0, p.sensor_noise, p.steps))


def run_all(seed=42, p=Params()):
    noise = make_noise(p, seed)
    sums, sers, dets = [], [], {}
    for exp in EXPERIMENTS:
        s, d, det = run_experiment(exp, p, noise)
        sums.append(s); sers.append(d); dets[exp[0]] = det
    return pd.DataFrame(sums), pd.concat(sers, ignore_index=True), dets


# ----------------------------------------------------------------------------
# Text dashboard
# ----------------------------------------------------------------------------
def dashboard_text(row, p):
    bar = "-" * 48
    return "\n".join([
        bar, "ICS CYBER-PHYSICAL SIMULATION (FICTIONAL, BENIGN)", bar,
        f"Scenario:               {row['experiment']} - {row['scenario']}",
        f"Controller:             {row['controller_id']} ({row['configuration']})",
        f"Target validation:      {row['target_validation']}",
        f"Controller state:       {row['controller_state']}",
        f"Conceptual concealment: {row['conceptual_concealment']}",
        f"Expected process value: {p.target_value:.0f}",
        f"Simulated process value:{row['process_mean_final_50_steps']:>8.1f}  (mean of final 50 steps)",
        f"HMI value:              {row['hmi_final_mean_10']:>8.1f}  -> {row['hmi_result']}",
        f"Independent monitor:    {row['monitor_final_mean_10']:>8.1f}  -> {row['monitor_result']}",
        f"Security status:        {row['security_status']}", bar])


# ----------------------------------------------------------------------------
# Figures (generated only from simulation output)
# ----------------------------------------------------------------------------
BLUE, TEAL, AMBER, SLATE, LGREY, RED = "#1F4E9C", "#0E6F6E", "#A8510A", "#475569", "#CBD5E1", "#9B1C1C"
LBLUE, LTEAL, LAMBER = "#E8EEF8", "#DDF0EF", "#FBEBDD"
NOTE = ("Fictional process, arbitrary units. Benign conceptual simulation inspired by the "
        "Stuxnet attack chain; not Stuxnet.")


def _style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["Liberation Serif", "DejaVu Serif"],
        "font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": "#E2E8F0", "grid.linewidth": 0.8,
        "legend.frameon": False, "figure.dpi": 100, "savefig.dpi": 200})
    return plt


def _foot(fig, text=NOTE):
    fig.text(0.01, 0.005, text, fontsize=9, color=SLATE, style="italic", va="bottom")


def _band(ax, p):
    ax.axhspan(p.normal_low, p.normal_high, color=LBLUE, zorder=0, label="Fictional normal range (950–1050)")


def make_figures(summ, ser, dets, p, figdir):
    from matplotlib.patches import FancyBboxPatch
    plt = _style()
    os.makedirs(figdir, exist_ok=True)
    E = {k: ser[ser.experiment == k].reset_index(drop=True) for k in "ABCD"}
    S = {r.experiment: r for r in summ.itertuples()}
    t0 = p.activation_step
    thr_hi, thr_lo = p.target_value * (1 + p.threshold), p.target_value * (1 - p.threshold)

    # ---- Figure 1: architecture
    fig, ax = plt.subplots(figsize=(12, 5.2)); ax.set_xlim(0, 12); ax.set_ylim(0, 5.2); ax.axis("off")
    def box(x, y, w, h, text, fc, ec, tc="#1E293B", fs=12, ls="-"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc=fc, ec=ec, lw=2, ls=ls))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc, linespacing=1.25)
    def arrow(x1, y1, x2, y2, c=SLATE, ls="-"):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=c, lw=2, ls=ls))
    box(0.2, 2.2, 2.0, 1.1, "Engineering\nWorkstation", LTEAL, TEAL)
    box(2.8, 2.2, 2.0, 1.1, "Target\nValidation", LTEAL, TEAL)
    box(5.4, 2.2, 2.0, 1.1, "Simulated PLC\n(one-line logic)", LTEAL, TEAL)
    box(8.0, 2.2, 1.8, 1.1, "Process\nModel", LAMBER, AMBER)
    box(10.2, 3.5, 1.6, 1.1, "HMI\n(Path A)", LBLUE, BLUE)
    box(10.2, 0.9, 1.6, 1.1, "Independent\nMonitor\n(Path B)", LBLUE, BLUE)
    arrow(2.2, 2.75, 2.8, 2.75); arrow(4.8, 2.75, 5.4, 2.75); arrow(7.4, 2.75, 8.0, 2.75)
    arrow(9.8, 2.95, 10.2, 3.9); arrow(9.8, 2.55, 10.2, 1.5)
    ax.text(3.8, 1.95, "CTRL-A: TARGET → passed\nCTRL-B: NON-TARGET → no action", ha="center", va="top", fontsize=10, color=SLATE)
    ax.text(6.4, 1.95, "command = target_value\nor altered_value", ha="center", va="top", fontsize=10, color=SLATE)
    ax.text(10.99, 3.35, "Exp. D: replays recorded values\n(conceptual concealment)", ha="center", va="top", fontsize=9.5, color=BLUE, style="italic")
    ax.text(10.99, 0.75, "own sensor, always true value", ha="center", va="top", fontsize=9.5, color=BLUE, style="italic")
    ax.text(1.2, 4.0, "Engineering / control layer (simulated)", fontsize=11, color=TEAL, weight="bold")
    ax.text(8.0, 1.0, "Physical-process layer\n(fictional)", fontsize=11, color=AMBER, weight="bold")
    ax.text(6.0, 5.0, "Conceptual simulation architecture", ha="center", fontsize=14, weight="bold")
    _foot(fig); fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(f"{figdir}/figure_1_architecture.png"); plt.close(fig)

    # ---- Figure 2: normal operation
    d = E["A"]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.6), sharex=True, gridspec_kw=dict(height_ratios=[2.2, 1]))
    _band(a1, p)
    a1.plot(d.step, d.actual_speed, color=BLUE, lw=1.6, label="Process speed")
    a1.axhline(p.target_value, color=SLATE, ls="--", lw=1.2, label="Target (1000)")
    a1.set_ylim(900, 1100); a1.set_ylabel("Speed (arbitrary units)")
    a1.set_title("Experiment A – normal operation: process stable around target"); a1.legend(loc="upper right", fontsize=10, ncol=3)
    a2.plot(d.step, d.temperature, color=AMBER, lw=1.6); a2.set_ylabel("Temperature (a.u.)"); a2.set_xlabel("Simulation step")
    a2.set_ylim(45, 55)
    _foot(fig); fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(f"{figdir}/figure_2_normal_operation.png"); plt.close(fig)

    # ---- Figure 3: target validation
    fig, axs = plt.subplots(1, 2, figsize=(12, 5.2), sharey=True)
    for ax, k, ttl, msg, col in ((axs[0], "B", "Experiment B – CTRL-B (NON-TARGET)", "TARGET VALIDATION: FAILED\n→ NO CONTROLLER CHANGE\n→ NO PROCESS MANIPULATION", TEAL),
                                 (axs[1], "C", "Experiment C – CTRL-A (TARGET)", "TARGET VALIDATION: PASSED\n→ SIMULATED CONTROLLER CHANGE\n→ process deviates", AMBER)):
        d = E[k]; _band(ax, p)
        ax.plot(d.step, d.command, color=SLATE, ls="--", lw=1.4, label="Controller command")
        ax.plot(d.step, d.actual_speed, color=BLUE, lw=1.6, label="Process speed")
        ax.axvline(t0, color=LGREY, lw=1.5); ax.text(t0 + 3, 1230, "activation step", fontsize=9.5, color=SLATE)
        ax.text(0.04, 0.96, msg, transform=ax.transAxes, va="top", fontsize=11, weight="bold", color=col,
                bbox=dict(boxstyle="round", fc="white", ec=col, lw=1.5))
        ax.set_title(ttl); ax.set_xlabel("Simulation step"); ax.set_ylim(900, 1250)
    axs[0].set_ylabel("Speed (arbitrary units)"); axs[1].legend(loc="center right", fontsize=10)
    fig.suptitle("Target validation restricts the simulated change to one configuration", fontsize=14, weight="bold")
    _foot(fig); fig.tight_layout(rect=(0, 0.03, 1, 0.95)); fig.savefig(f"{figdir}/figure_3_target_validation.png"); plt.close(fig)

    # ---- Figure 4: normal vs manipulated
    a, c = E["A"], E["C"]
    fig, ax = plt.subplots(figsize=(10, 5.6)); _band(ax, p)
    ax.plot(a.step, a.actual_speed, color=SLATE, lw=1.6, label="Expected process (Exp. A, normal)")
    ax.plot(c.step, c.actual_speed, color=AMBER, lw=1.8, label="Simulated manipulated process (Exp. C)")
    ax.fill_between(c.step, a.actual_speed, c.actual_speed, where=c.step >= t0, color=LAMBER, zorder=0)
    for y, lab in ((thr_hi, "+5 % threshold"), (thr_lo, "−5 % threshold")):
        ax.axhline(y, color=RED, ls=":", lw=1.2); ax.text(2, y + 4, lab, fontsize=9.5, color=RED)
    ax.axvline(t0, color=LGREY, lw=1.5); ax.text(t0 + 3, 905, "simulated change takes effect", fontsize=9.5, color=SLATE)
    ax.set_ylim(900, 1180); ax.set_xlabel("Simulation step"); ax.set_ylabel("Speed (arbitrary units)")
    ax.set_title("Expected vs simulated manipulated process variable"); ax.legend(loc="upper left", fontsize=10)
    ax.annotate(f"max deviation {S['C'].max_process_deviation_pct:.1f} %", xy=(T := p.steps - 5, S['C'].process_mean_final_50_steps),
                xytext=(T - 85, 1120), fontsize=10.5, arrowprops=dict(arrowstyle="->", color=SLATE))
    _foot(fig); fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(f"{figdir}/figure_4_process_comparison.png"); plt.close(fig)

    # ---- Figure 5: HMI vs independent monitor
    d, c = E["D"], E["C"]
    fig, ax = plt.subplots(figsize=(10, 5.6)); _band(ax, p)
    ax.plot(c.step, c.hmi_displayed, color=LGREY, lw=1.2, ls=":", label="HMI in Exp. C (no concealment)")
    ax.plot(d.step, d.hmi_displayed, color=BLUE, lw=1.8, label="Path A: HMI value shown to operator (Exp. D)")
    ax.plot(d.step, d.independent_monitor, color=AMBER, lw=1.8, label="Path B: independent monitor (Exp. D)")
    for y in (thr_hi, thr_lo): ax.axhline(y, color=RED, ls=":", lw=1.2)
    ax.text(2, thr_hi + 4, "±5 % threshold", fontsize=9.5, color=RED)
    ax.axvline(t0, color=LGREY, lw=1.5)
    ax.text(205, 1098, "Independent monitor sees the deviation", ha="center", color=AMBER, fontsize=11, weight="bold",
            bbox=dict(fc="white", ec="none", pad=2))
    ax.text(205, 962, "HMI appears normal", ha="center", color=BLUE, fontsize=11, weight="bold",
            bbox=dict(fc="white", ec="none", pad=2))
    ax.set_ylim(900, 1180); ax.set_xlabel("Simulation step"); ax.set_ylabel("Reported speed (arbitrary units)")
    ax.set_title("Conceptual concealment scenario: operator display vs independent measurement")
    ax.legend(loc="upper left", fontsize=9.5)
    _foot(fig, NOTE + " Concealment is conceptual, not Stuxnet’s implementation.")
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(f"{figdir}/figure_5_hmi_vs_monitor.png"); plt.close(fig)

    # ---- Figure 6: detection result
    fig, (ax, tb) = plt.subplots(1, 2, figsize=(13, 5.4), gridspec_kw=dict(width_ratios=[1.15, 1]))
    ax.plot(d.step, d.hmi_deviation_pct, color=BLUE, lw=1.5, label="Path A: HMI deviation")
    ax.plot(d.step, d.monitor_deviation_pct, color=AMBER, lw=1.7, label="Path B: independent monitor deviation")
    ax.axhline(p.threshold * 100, color=RED, ls=":", lw=1.4); ax.text(205, p.threshold * 100 + 0.6, "5 % threshold (simulation assumption)", ha="center", fontsize=9.5, color=RED)
    md = dets["D"]["mon_det"]
    ax.axvline(md, color=AMBER, ls="--", lw=1.2)
    ax.text(205, 8.3, f"independent monitor flags anomaly at step {md}\n({md - t0} steps after the simulated change)", ha="center", fontsize=10, color=AMBER)
    ax.axvline(t0, color=LGREY, lw=1.5)
    ax.set_xlabel("Simulation step"); ax.set_ylabel("Deviation from expected (%)"); ax.set_ylim(0, 17)
    ax.set_title("Experiment D: detection by the independent monitor"); ax.legend(loc="upper left", fontsize=10)
    tb.axis("off"); tb.set_xlim(0, 10); tb.set_ylim(0, 6)
    tb.text(5, 5.75, "Detection result by experiment", ha="center", fontsize=13, weight="bold")
    for x, lab in ((4.7, "HMI path"), (8.0, "Independent monitor")):
        tb.text(x, 5.05, lab, ha="center", fontsize=11, weight="bold", color=SLATE)
    for i, k in enumerate("ABCD"):
        y = 4.0 - i * 1.05
        tb.text(0.1, y, f"Exp. {k}", fontsize=11.5, weight="bold", va="center")
        tb.text(0.1, y - 0.38, S[k].scenario.split(" + ")[0] if k != "D" else "Target matched + concealment", fontsize=8.5, color=SLATE, va="center")
        for x, res, dl in ((4.7, S[k].hmi_result, S[k].hmi_detection_delay_steps), (8.0, S[k].monitor_result, S[k].monitor_detection_delay_steps)):
            bad = res != "NORMAL"
            tb.add_patch(FancyBboxPatch((x - 1.45, y - 0.42), 2.9, 0.84, boxstyle="round,pad=0.02,rounding_size=0.1",
                                        fc=LAMBER if bad else LTEAL, ec=AMBER if bad else TEAL, lw=1.6))
            tb.text(x, y + (0.1 if bad else 0), res, ha="center", va="center", fontsize=10.5, weight="bold", color=AMBER if bad else TEAL)
            if bad: tb.text(x, y - 0.22, f"delay: {dl} steps", ha="center", va="center", fontsize=9, color=SLATE)
    _foot(fig); fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(f"{figdir}/figure_6_detection_result.png"); plt.close(fig)

    # ---- Figure 7 (extra): dashboards
    fig, axs = plt.subplots(2, 2, figsize=(12, 7.6))
    for ax, k in zip(axs.ravel(), "ABCD"):
        ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 10); r = S[k]
        bad = r.security_status != "SAFE"
        ax.add_patch(FancyBboxPatch((0.1, 0.1), 9.8, 9.8, boxstyle="round,pad=0.02,rounding_size=0.2",
                                    fc="white", ec=AMBER if bad else TEAL, lw=2.2))
        ax.text(0.5, 9.2, f"Scenario {k}: {r.scenario}", fontsize=11.5, weight="bold", va="top")
        rows = [("Target validation", r.target_validation), ("Controller state", r.controller_state),
                ("Expected value", f"{p.target_value:.0f}"), ("Simulated process value", f"{r.process_mean_final_50_steps:.1f}"),
                ("HMI value", f"{r.hmi_final_mean_10:.1f}  ({r.hmi_result})"),
                ("Independent monitor", f"{r.monitor_final_mean_10:.1f}  ({r.monitor_result})"),
                ("Security status", r.security_status)]
        for i, (l, v) in enumerate(rows):
            y = 7.7 - i * 1.0
            ax.text(0.5, y, l, fontsize=10.5, color=SLATE, va="center")
            ax.text(5.0, y, v, fontsize=10.5, weight="bold", va="center", color=(AMBER if (l == "Security status" and bad) else "#1E293B"))
    fig.suptitle("ICS cyber-physical simulation dashboard (fictional, benign)", fontsize=14, weight="bold")
    _foot(fig); fig.tight_layout(rect=(0, 0.03, 1, 0.95)); fig.savefig(f"{figdir}/figure_7_dashboard.png"); plt.close(fig)


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Benign Stuxnet-inspired ICS concept simulation (fictional process).")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--no-figures", action="store_true")
    ap.add_argument("--outroot", default=None, help="project root (default: parent of this script's folder)")
    args = ap.parse_args()
    root = args.outroot or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    p = Params()
    summ, ser, dets = run_all(args.seed, p)
    os.makedirs(f"{root}/02_Results", exist_ok=True)
    ser.round(4).to_csv(f"{root}/02_Results/simulation_results.csv", index=False)
    summ.to_csv(f"{root}/02_Results/simulation_summary.csv", index=False)
    print("This process model is fictional and does not represent the physical parameters of any real industrial facility.\n")
    for _, r in summ.iterrows():
        print(dashboard_text(r, p)); print()
    if not args.no_figures:
        make_figures(summ, ser, dets, p, f"{root}/03_Figures")
        print("Figures written to", f"{root}/03_Figures")
    print("Results written to", f"{root}/02_Results")


if __name__ == "__main__":
    sys.exit(main())
