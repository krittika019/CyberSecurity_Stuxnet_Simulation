"""Automated validation of the benign ICS concept simulation. Run: python run_validation.py"""
import ast, hashlib, os, subprocess, sys, tempfile
import numpy as np, pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CODE = f"{ROOT}/01_Code/stuxnet_ics_concept_simulation.py"
sys.path.insert(0, f"{ROOT}/01_Code")
import stuxnet_ics_concept_simulation as sim
res = []
def check(name, ok, detail=""):
    res.append(ok); print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")

# 1 code runs from a clean temp output root
tmp = tempfile.mkdtemp()
r = subprocess.run([sys.executable, CODE, "--outroot", tmp], capture_output=True, text=True)
check("code runs successfully (exit 0)", r.returncode == 0, r.stderr[-200:])
# 2 static scan: no network / process / OS-level capability imports or calls
tree = ast.parse(open(CODE).read()); imps = set()
for n in ast.walk(tree):
    if isinstance(n, ast.Import): imps |= {a.name.split(".")[0] for a in n.names}
    if isinstance(n, ast.ImportFrom): imps.add((n.module or "").split(".")[0])
banned = {"socket", "requests", "urllib", "http", "subprocess", "ctypes", "winreg", "paramiko", "scapy", "snap7", "pymodbus", "opcua", "ftplib", "smtplib", "telnetlib"}
check("no network/process/ICS-protocol imports", not (imps & banned), f"imports={sorted(imps)}")
src = open(CODE).read()
check("no os.system / eval / exec / popen", not any(s in src for s in ("os.system", "eval(", "exec(", "popen")))
# 3 reproducibility
def h(root): return hashlib.sha256(open(f"{root}/02_Results/simulation_results.csv", "rb").read()).hexdigest()
tmp2 = tempfile.mkdtemp(); subprocess.run([sys.executable, CODE, "--outroot", tmp2, "--no-figures"], capture_output=True)
check("results reproducible (identical SHA-256 across two runs)", h(tmp) == h(tmp2), h(tmp)[:16])
check("project results file equals fresh run", h(ROOT) == h(tmp))
# 4 data quality
ser = pd.read_csv(f"{ROOT}/02_Results/simulation_results.csv"); sm = pd.read_csv(f"{ROOT}/02_Results/simulation_summary.csv", keep_default_na=False)
check("no NaN in time-series CSV", not ser.isna().any().any(), f"rows={len(ser)}")
check("no NaN / empty in summary CSV", not sm.isna().any().any() and not (sm.astype(str) == "").any().any())
check("four experiments present", list(sm.experiment) == list("ABCD"))
# 5 behaviours
S = sm.set_index("experiment")
check("A normal stable (max dev < 5%)", S.loc["A", "max_process_deviation_pct"] < 5, f"{S.loc['A','max_process_deviation_pct']}%")
check("A: no alarms on either path (no false positives)", S.loc["A", "hmi_result"] == "NORMAL" and S.loc["A", "monitor_result"] == "NORMAL")
check("B: target validation FAILED, controller NORMAL, no deviation", S.loc["B", "target_validation"] == "FAILED" and S.loc["B", "controller_state"] == "NORMAL" and S.loc["B", "max_process_deviation_pct"] < 5)
check("B identical to A in process output", np.allclose(ser[ser.experiment == "A"].actual_speed, ser[ser.experiment == "B"].actual_speed))
check("C: validation PASSED, change applied, deviation > 5%", S.loc["C", "target_validation"] == "PASSED" and S.loc["C", "controller_state"] == "SIMULATED CHANGE" and S.loc["C", "max_process_deviation_pct"] > 5, f"{S.loc['C','max_process_deviation_pct']}%")
check("C: process identical to A before activation", np.allclose(ser[(ser.experiment == "A") & (ser.step < 100)].actual_speed, ser[(ser.experiment == "C") & (ser.step < 100)].actual_speed))
check("C: operator HMI shows the anomaly (no concealment)", S.loc["C", "hmi_result"] == "ANOMALY VISIBLE")
check("D: HMI stays NORMAL while independent monitor flags ANOMALY", S.loc["D", "hmi_result"] == "NORMAL" and S.loc["D", "monitor_result"] == "ANOMALY")
check("D: true process identical to C (concealment alters display only)", np.allclose(ser[ser.experiment == "C"].actual_speed, ser[ser.experiment == "D"].actual_speed))
check("independent monitor detects C and D", S.loc["C", "monitor_result"] == "ANOMALY" and S.loc["D", "monitor_result"] == "ANOMALY")
d = ser[ser.experiment == "D"]; post = d[d.step >= 100]
print(f"       D post-activation: max HMI deviation {post.hmi_deviation_pct.max():.2f}% ; max monitor deviation {post.monitor_deviation_pct.max():.2f}% ; HMI flags {int(post.hmi_flag.sum())} ; monitor flags {int(post.monitor_flag.sum())}")
# 6 outputs
figs = [f"figure_{i}_{n}.png" for i, n in enumerate(["architecture", "normal_operation", "target_validation", "process_comparison", "hmi_vs_monitor", "detection_result"], 1)]
check("six required figures exist and are non-empty", all(os.path.getsize(f"{ROOT}/03_Figures/{f}") > 10000 for f in figs))
# 7 report numbers match the simulation output
pre = ser[(ser.experiment == "C") & (ser.step < 100)].actual_speed.mean()
vals = {"1.27": S.loc["A", "max_process_deviation_pct"], "15.73": S.loc["C", "max_process_deviation_pct"], "1140.16": S.loc["C", "process_mean_post_activation"],
        "1150.39": S.loc["C", "process_mean_final_50_steps"], "999.86": S.loc["C", "baseline_mean_pre_activation"], "195": S.loc["C", "steps_outside_normal_range"],
        "56.14": S.loc["C", "max_process_temperature"], "1.11": post.hmi_deviation_pct.max(), "15.81": post.monitor_deviation_pct.max()}
rep = "".join(open(f"{ROOT}/04_Report/{n}").read() for n in os.listdir(f"{ROOT}/04_Report") if n.endswith(".md"))
for k, x in vals.items():
    fmt = f"{x:.2f}" if k != "195" else str(int(x))
    check(f"report number {k} equals simulation output ({fmt}) and appears in report text", fmt == k and k in rep)
check("detection delay 7 steps in C and D matches report", str(S.loc["C", "monitor_detection_delay_steps"]) == "7" and str(S.loc["D", "monitor_detection_delay_steps"]) == "7" and "7 steps" in rep)
print(f"\nSummary: {sum(res)}/{len(res)} checks passed"); sys.exit(0 if all(res) else 1)
