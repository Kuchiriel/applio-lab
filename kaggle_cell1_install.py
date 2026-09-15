# ============================================================
# CELL 1 — Applio (latest) install for Kaggle T4 x2
# Fixes vs. old version:
#  - Always clones latest Applio (no stale sentinel file)
#  - No fairseq uninstall (not a dependency in current Applio)
#  - Uses official uv + torch cu128 recipe (valid on T4, used
#    by Applio's own Kaggle notebook)
#  - Downloads pretrained G/D + rmvpe/FCPE/Hubert models via
#    `core.py prerequisites` (this was MISSING -> training
#    silently refused to start: pretrained_selector returns "")
#  - FileBrowser: default auth + admin user (noauth keeps
#    returning 401 on every API call -> endless login wall)
# ============================================================
import os
import sys
import shutil
import subprocess

MODEL_NAME = "jarvis-rvc"
BASE_DIR = "/kaggle/working/program_ml"
FB_DB = "/tmp/filebrowser.db"
FB_USER = "applio"
FB_PASS = "applio123456"

os.chdir("/kaggle/working")


def run(cmd, **kw):
    check = kw.pop("check", True)
    quiet = kw.pop("quiet", False)
    r = subprocess.run(
        cmd,
        check=check,
        stdout=subprocess.DEVNULL if quiet else None,
        stderr=subprocess.STDOUT if quiet else None,
        **kw,
    )
    return r


# ---------- [1/6] Locate dataset ----------
print("=== [1/6] LOCATING DATASET ===")
dataset_path = None
for root, dirs, files in os.walk("/kaggle/input"):
    if os.path.basename(root).lower() == MODEL_NAME.lower():
        dataset_path = root
        break
if dataset_path:
    print(f"  OK: {dataset_path}")
else:
    print(f"  WARNING: dataset '{MODEL_NAME}' not found under /kaggle/input")


# ---------- [2/6] Fresh clone (always latest) ----------
print("=== [2/6] CLONING LATEST APPLIO ===")
if os.path.exists(BASE_DIR):
    shutil.rmtree(BASE_DIR)
run(["git", "clone", "--depth", "1", "https://github.com/IAHispano/Applio.git", BASE_DIR])
print("  Cloned to " + BASE_DIR)


# ---------- [3/6] System packages ----------
print("=== [3/6] SYSTEM PACKAGES ===")
run(["apt-get", "update", "-qq"], check=False, quiet=True)
run(
    ["apt-get", "install", "-y", "-qq", "portaudio19-dev", "psmisc", "ffmpeg"],
    check=False,
    quiet=True,
)
print("  Done (portaudio, psmisc, ffmpeg)")


# ---------- [4/6] Python deps (uv + torch cu128, official recipe) ----------
print("=== [4/6] PYTHON DEPENDENCIES (uv, torch cu128) ===")
run([sys.executable, "-m", "pip", "install", "-q", "uv"], check=True)
run(
    [
        "uv", "pip", "install", "-q",
        "-r", os.path.join(BASE_DIR, "requirements.txt"),
        "--extra-index-url", "https://download.pytorch.org/whl/cu128",
        "--index-strategy", "unsafe-best-match",
        "--system",
    ],
    check=True,
)
print("  requirements.txt installed (torch 2.11 + cu128 wheels, T4-compatible)")


# ---------- [5/6] Model prerequisites (pretraineds, rmvpe, hubert) ----------
print("=== [5/6] DOWNLOADING MODEL PREREQUISITES (do not skip) ===")
run(
    [sys.executable, "core.py", "prerequisites",
     "--models", "--exe", "--pretraineds-hifigan"],
    cwd=BASE_DIR,
    check=True,
)
print("  Pretrained G/D (f0G40k/f0D40k), rmvpe, FCPE, Hubert: OK")


# ---------- [6/6] FileBrowser (user/password auth) ----------
print("=== [6/6] FILEBROWSER SETUP ===")
if shutil.which("filebrowser") is None:
    run(
        "curl -fsSL https://github.com/filebrowser/filebrowser/releases/latest/download/"
        "linux-amd64-filebrowser.tar.gz | tar xz -C /usr/local/bin filebrowser",
        shell=True,
        check=True,
    )
if os.path.exists(FB_DB):
    os.remove(FB_DB)
run(["filebrowser", "config", "init", "-d", FB_DB], check=True, quiet=True)
run(["filebrowser", "config", "set", "-d", FB_DB, "--root", "/kaggle"], check=True, quiet=True)
run(["filebrowser", "users", "add", FB_USER, FB_PASS, "--perm.admin", "-d", FB_DB],
    check=True, quiet=True)
print(f"  Auth ready -> login: {FB_USER} / {FB_PASS}")

print("\nINSTALL COMPLETE")
print(f"Dataset (auto-prefilled in Cell 2): {dataset_path}")
