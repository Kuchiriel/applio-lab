# ============================================================
# CELL 3 — Export trained model to /kaggle/working
# Run after training finishes (or any time to grab a snapshot)
# ============================================================
import glob
import os
import shutil

MODEL_NAME = "jarvis-rvc"
BASE_DIR = "/kaggle/working/program_ml"
exp_dir = os.path.join(BASE_DIR, "logs", MODEL_NAME)
out_dir = "/kaggle/working"
os.makedirs(out_dir, exist_ok=True)

# Newest inference .pth (skip G_/D_ checkpoints)
pths = sorted(
    (p for p in glob.glob(os.path.join(exp_dir, f"{MODEL_NAME}*.pth"))
     if not os.path.basename(p).startswith(("G_", "D_"))),
    key=os.path.getmtime,
)
idxs = glob.glob(os.path.join(exp_dir, f"{MODEL_NAME}.index"))

if not pths:
    print(f"No .pth found in {exp_dir}")
    print("Contents:", os.listdir(exp_dir) if os.path.exists(exp_dir) else "dir missing")
else:
    src = pths[-1]
    dst = os.path.join(out_dir, os.path.basename(src))
    shutil.copy2(src, dst)
    print(f"Copied: {dst}  ({os.path.getsize(dst)/1e6:.1f} MB)")

if idxs:
    dst = os.path.join(out_dir, os.path.basename(idxs[0]))
    shutil.copy2(idxs[0], dst)
    print(f"Copied: {dst}  ({os.path.getsize(dst)/1e3:.1f} KB)")
else:
    print("No .index yet — use 'Generate Index' in the UI or rerun after training.")

# Optional: newest G/D checkpoints for resuming training later
for pattern in (f"G_*.pth", f"D_*.pth"):
    ckpts = sorted(glob.glob(os.path.join(exp_dir, pattern)), key=os.path.getmtime)
    if ckpts:
        dst = os.path.join(out_dir, os.path.basename(ckpts[-1]))
        shutil.copy2(ckpts[-1], dst)
        print(f"Copied checkpoint: {dst}")

print("\nDone. Files in /kaggle/working are downloadable from the notebook output panel")
print("or via FileBrowser (they persist in the saved notebook version).")
