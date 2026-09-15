#!/usr/bin/env python3
"""Prepara datasets + kernels Kaggle por personagem (usa jarvis-train.ipynb de molde).
Uso: python3 gen-kaggle.py
Saida: /tmp/opencode/kaggle-ds/<slug>/ + /tmp/opencode/kaggle-ky/<slug>/ + plano.json
"""
import json
import os
import shutil

DS = "/home/nixos/Audio/lotm/datasets"
OUT_DS = "/tmp/opencode/kaggle-ds"
OUT_KY = "/tmp/opencode/kaggle-ky"
TPL_NB = "/home/nixos/projects/applio-lab/kaggle-train/jarvis-train.ipynb"

# slug pool -> (dataset existente? , kernel existente?)
CHARS = {
    "klein": ("kuchiriel/klein-lotm", "kuchiriel/klein-rvc-train"),
    "dunn": (None, None), "neil": (None, None), "narrador": (None, None),
    "leonard": (None, None), "megose": (None, None), "daly": (None, None),
    "alger": (None, None), "hood": (None, None),
}
MERGE = {"klein": ["klein-v4"], "narrador": ["narrador-abertura"]}
MIN_MIN = 1.9


def main():
    rep = json.load(open(os.path.join(DS, "pools-report.json")))
    nb_tpl = json.load(open(TPL_NB))
    plan = []
    for slug, (ds_ref, ky_ref) in CHARS.items():
        pool = f"{slug}-v1"
        info = rep.get(pool)
        if not info:
            print(f"{slug}: sem pool, pulo"); continue
        # minutos extras dos merges
        extra_min, extra_n = 0.0, 0
        if slug in MERGE:
            import wave
            import contextlib
            for m in MERGE[slug]:
                mp = os.path.join(DS, m)
                for f in os.listdir(mp):
                    if f.endswith(".wav"):
                        extra_n += 1
                        try:
                            with contextlib.closing(wave.open(os.path.join(mp, f))) as wv:
                                extra_min += wv.getnframes() / wv.getframerate()
                        except Exception:
                            pass
        tot_min = info["min"] + extra_min / 60
        if tot_min < MIN_MIN:
            print(f"{slug}: {tot_min:.1f}min < {MIN_MIN}, fora da fila"); continue
        model = f"lotm-{slug}"
        # --- dataset dir ---
        dd = os.path.join(OUT_DS, slug)
        os.makedirs(dd, exist_ok=True)
        for f in os.listdir(os.path.join(DS, pool)):
            if f.endswith(".wav"):
                shutil.copy2(os.path.join(DS, pool, f), os.path.join(dd, f))
        if slug in MERGE:
            for m in MERGE[slug]:
                for f in os.listdir(os.path.join(DS, m)):
                    if f.endswith(".wav"):
                        shutil.copy2(os.path.join(DS, m, f), os.path.join(dd, f"merge-{m}-{f}"))
        nfiles = len([f for f in os.listdir(dd) if f.endswith(".wav")])
        title = ds_ref.split("/")[1] if ds_ref else f"lotm-{slug}"
        meta = {"title": title, "licenses": [{"name": "CC0-1.0"}]}
        if ds_ref:
            meta["id"] = ds_ref
        else:
            meta["id"] = f"kuchiriel/lotm-{slug}"
        json.dump(meta, open(os.path.join(dd, "dataset-metadata.json"), "w"), indent=1)
        # --- kernel dir ---
        kd = os.path.join(OUT_KY, slug)
        os.makedirs(kd, exist_ok=True)
        nb = json.loads(json.dumps(nb_tpl))
        for c in nb["cells"]:
            if c["cell_type"] == "code":
                c["source"] = [ln.replace("klein-rvc", model).replace("klein-best", f"{slug}-best")
                               for ln in c["source"]]
        # prova de GPU no cell1
        nb["cells"][1]["source"].append(
            'print("GPUS:\", __import__(\"subprocess\").run([\"nvidia-smi\", \"--list-gpus\"], capture_output=True, text=True).stdout)')
        json.dump(nb, open(os.path.join(kd, f"{model}-train.ipynb"), "w"), indent=1)
        kmeta = {"id": ky_ref if ky_ref else f"kuchiriel/{model}-train",
                 "title": ky_ref.split("/")[1] if ky_ref else f"{model}-train",
                 "code_file": f"{model}-train.ipynb", "language": "python",
                 "kernel_type": "notebook", "is_private": "true",
                 "enable_gpu": "true", "enable_tpu": "false", "enable_internet": "true",
                 "dataset_sources": [ds_ref if ds_ref else f"kuchiriel/lotm-{slug}"],
                 "competition_sources": [], "kernel_sources": [], "model_sources": [],
                 "machine_shape": "NvidiaTeslaT4"}
        json.dump(kmeta, open(os.path.join(kd, "kernel-metadata.json"), "w"), indent=1)
        plan.append({"slug": slug, "model": model, "ds": meta["id"],
                     "kernel": kmeta["id"], "clips": nfiles,
                     "min": round(tot_min, 1), "is_version": bool(ds_ref)})
        print(f"{slug}: {nfiles} clips {tot_min:.1f}min -> {meta['id']} + {kmeta['id']}", flush=True)
    json.dump(plan, open("/tmp/opencode/kaggle-plan.json", "w"), indent=1)


main()
