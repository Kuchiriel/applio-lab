# ============================================================
# CELL 2 — Launch Applio on Kaggle (T4 x2) with prefilled UI
# Fixes vs. old version:
#  - app.py has NO --listen flag (silently ignored before);
#    binding is 127.0.0.1 by default and ngrok works with it
#  - UI patch rewritten: matches the REAL latest Applio code
#    (model_name/dataset_path are Dropdowns, sliders use
#    positional values, terms_checkbox now gates training)
#  - GPU string auto-detected ("0-1" on T4 x2, "0" on P100)
#  - Patch is syntax-verified with ast.parse before launch
#  - FileBrowser uses the working user/password recipe
# ============================================================
import os
import re
import ast
import sys
import time
import socket
import subprocess
import shutil
import json
from pyngrok import ngrok
from IPython.display import clear_output

BASE_DIR = "/kaggle/working/program_ml"
MODEL_NAME = "jarvis-rvc"
NGROK_TOKEN = "2nRnxIB9bCV0GG6Rh6zbIinN0N6_3R3CaYYiYUov7qoEkzVNd"  # <- your token (consider rotating it, it's stored in the notebook)

# ---------- [1/7] Detect dataset + GPUs ----------
print("=== [1/7] DETECTING DATASET AND GPUS ===")
DATASET_PATH = None
for root, dirs, files in os.walk("/kaggle/input"):
    if os.path.basename(root).lower() == MODEL_NAME.lower():
        DATASET_PATH = root
        break
print(f"  Dataset: {DATASET_PATH}")

try:
    n_gpus = len([l for l in subprocess.run(
        ["nvidia-smi", "--list-gpus"], capture_output=True, text=True
    ).stdout.splitlines() if l.strip()])
except Exception:
    n_gpus = 0
GPU_STR = "-".join(str(i) for i in range(n_gpus)) if n_gpus else "0"
print(f"  GPUs detected: {n_gpus} -> training/extraction on '{GPU_STR}'")

# ---------- [2/7] Stop leftovers ----------
print("=== [2/7] STOPPING LEFTOVER PROCESSES ===")
for port in (6969, 8077, 9876):
    subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True)
ngrok.kill()
print("  Clean.")

os.chdir(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.environ["PYTHONPATH"] = f"{BASE_DIR}:{os.environ.get('PYTHONPATH', '')}"
os.environ.setdefault("OMP_NUM_THREADS", "4")

# ---------- [3/7] Verify prerequisites exist ----------
print("=== [3/7] VERIFYING PREREQUISITES ===")
_pre = os.path.join(BASE_DIR, "rvc", "models", "pretraineds", "hifigan")
_missing = [f for f in ("f0G40k.pth", "f0D40k.pth") if not os.path.exists(os.path.join(_pre, f))]
if _missing:
    print(f"  WARNING: missing pretrained {_missing} — run Cell 1 step 5 or training will fail!")
else:
    print("  Pretrained f0G40k/f0D40k present.")

# ---------- [4/7] config.json (official schema) ----------
print("=== [4/7] WRITING assets/config.json ===")
config = {
    "theme": {"file": "Applio.py", "class": "Applio"},
    "plugins": [],
    "discord_presence": False,
    "lang": {"override": False, "selected_lang": "en_US"},
    "version": "3.6.4",
    "model_author": "Kaggle",
    "precision": "fp16",
    "rmvpe_high_register": {"enabled": False, "mode": "true_pitch", "f0_ceil": 1250},
    "realtime": {
        "input_device": "", "output_device": "", "monitor_device": "",
        "model_file": "", "index_file": "",
        "client_input_device": "", "client_output_device": "",
        "client_monitor_device": "",
    },
}
with open(os.path.join(BASE_DIR, "assets", "config.json"), "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4)
print("  Written (fp16, no discord presence).")


# ---------- [5/7] Patch Train tab defaults ----------
def set_component_default(src: str, var_name: str, value_expr: str) -> str:
    """Set the `value` of a Gradio component assignment in train.py.

    Handles: existing value= kwarg (replace), Slider positional value
    (3rd positional, replace), or no value (insert kwarg)."""
    m = re.search(rf"\b{re.escape(var_name)}\s*=\s*gr\.\w+\(", src)
    if not m:
        print(f"  !! '{var_name}' not found — patch skipped")
        return src
    open_paren = m.end() - 1

    # find matching close paren, skipping string literals
    depth, i, quote, esc = 0, open_paren, None, False
    while i < len(src):
        c = src[i]
        if quote:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == quote:
                quote = None
        else:
            if c in "\"'":
                quote = c
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
        i += 1
    segment = src[open_paren + 1 : i]

    # split top-level args (strings respected)
    args, buf, d, q, e = [], "", 0, None, False
    for c in segment:
        if q:
            buf += c
            if e:
                e = False
            elif c == "\\":
                e = True
            elif c == q:
                q = None
        else:
            if c in "\"'":
                q = c
                buf += c
            elif c == ",":
                if d == 0:
                    args.append(buf)
                    buf = ""
                else:
                    buf += c
            else:
                if c in "([{":
                    d += 1
                elif c in ")]}":
                    d -= 1
                buf += c
    if buf.strip():
        args.append(buf)

    kw_idx = next((k for k, a in enumerate(args) if re.match(r"\s*value\s*=", a)), None)
    positional_idx = [k for k, a in enumerate(args) if not re.match(r"\s*\w+\s*=", a)]

    if kw_idx is not None:
        args[kw_idx] = f" value={value_expr}"
        how = "replaced value kwarg"
    elif var_name in ("batch_size", "save_every_epoch", "total_epoch") and len(positional_idx) >= 3:
        args[positional_idx[2]] = f" {value_expr}"  # Slider(min, max, value, ...)
        how = "replaced 3rd positional (Slider value)"
    else:
        args.insert(0, f" value={value_expr}")
        how = "inserted value kwarg"

    new_seg = ",".join(args)
    patched = src[: open_paren + 1] + new_seg + src[i:]
    print(f"  {var_name} <- {value_expr} ({how})")
    return patched


print("=== [5/7] PATCHING tabs/train/train.py DEFAULTS ===")
train_py = os.path.join(BASE_DIR, "tabs", "train", "train.py")
with open(train_py, "r", encoding="utf-8") as f:
    content = f.read()

content = set_component_default(content, "model_name", f'"{MODEL_NAME}"')
content = set_component_default(content, "dataset_path", f'r"{DATASET_PATH}"' if DATASET_PATH else '""')
content = set_component_default(content, "gpu", f'"{GPU_STR}"')
content = set_component_default(content, "batch_size", "8")
content = set_component_default(content, "save_every_epoch", "25")
content = set_component_default(content, "total_epoch", "250")
content = set_component_default(content, "cache_dataset_in_gpu", "True")
content = set_component_default(content, "terms_checkbox", "True")  # required to enable Start Training

ast.parse(content)  # hard fail if the patch broke syntax
with open(train_py, "w", encoding="utf-8") as f:
    f.write(content)
print("  Patched + ast.parse OK")

# ---------- [6/7] TensorBoard + FileBrowser ----------
print("=== [6/7] STARTING TENSORBOARD + FILEBROWSER ===")
logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)
subprocess.Popen(
    [sys.executable, "-m", "tensorboard.main", "--logdir", logs_dir, "--port", "8077"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE_DIR,
)

FB_DB = "/tmp/filebrowser.db"
if os.path.exists(FB_DB):
    os.remove(FB_DB)
subprocess.run(["filebrowser", "config", "init", "-d", FB_DB], capture_output=True)
subprocess.run(["filebrowser", "config", "set", "-d", FB_DB, "--root", "/kaggle"], capture_output=True)
subprocess.run(["filebrowser", "users", "add", "applio", "applio123456", "--perm.admin", "-d", FB_DB],
               capture_output=True)
subprocess.Popen(["filebrowser", "-d", FB_DB, "-p", "9876"],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("  TB :8077 | FB :9876 (login applio / applio123456)")

# ---------- [7/7] Launch Applio + ngrok ----------
print("=== [7/7] LAUNCHING APPLIO ===")
applio_log = os.path.join(BASE_DIR, "applio.log")
log_file = open(applio_log, "w", encoding="utf-8")
app_process = subprocess.Popen(
    [sys.executable, "-u", "app.py", "--port", "6969"],
    stdout=log_file, stderr=subprocess.STDOUT, cwd=BASE_DIR,
)

port_open = False
start_time = time.time()
while time.time() - start_time < 180:
    if app_process.poll() is not None:
        break
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", 6969)) == 0:
            port_open = True
            break
    time.sleep(2)

if not port_open:
    log_file.close()
    with open(applio_log, "r", encoding="utf-8") as f:
        print("=== APPLIO FAILED TO START — LOG TAIL ===")
        print(f.read()[-4000:])
    raise RuntimeError("Applio did not open port 6969 within 180s.")

ngrok.set_auth_token(NGROK_TOKEN)
p_tunnel = ngrok.connect(6969)
t_tunnel = ngrok.connect(8077)
f_tunnel = ngrok.connect(9876)

clear_output()
print("=== SERVERS ONLINE (Kaggle T4 x2 preset) ===")
print("Applio      :", p_tunnel.public_url)
print("TensorBoard :", t_tunnel.public_url)
print("FileBrowser :", f_tunnel.public_url, " (login: applio / applio123456)")
print(f"Model: {MODEL_NAME} | Dataset: {DATASET_PATH}")
print(f"GPUs: {GPU_STR} | batch 8 | 250 epochs | save every 25 | fp16 | cache in GPU")
print("\n--- LIVE LOG (Ctrl+C or interrupt to stop watching; training keeps running) ---")
try:
    with open(applio_log, "r", encoding="utf-8") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            print(line, end="")
except KeyboardInterrupt:
    print("\nLog watching stopped. Applio is still running in the background.")
