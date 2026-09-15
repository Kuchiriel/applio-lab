"""Verify Cell 2's set_component_default against the REAL latest Applio code."""
import ast
import re
import shutil
import subprocess
import sys

# fresh copy of the repo
shutil.rmtree("/tmp/applio-test", ignore_errors=True)
subprocess.run(
    ["cp", "-r", "applio-lab/Applio", "/tmp/applio-test"], check=True
)
train_py = "/tmp/applio-test/tabs/train/train.py"
with open(train_py, encoding="utf-8") as f:
    src = f.read()

# --- exact same function as Cell 2 ---
def set_component_default(src, var_name, value_expr):
    m = re.search(rf"\b{re.escape(var_name)}\s*=\s*gr\.\w+\(", src)
    if not m:
        print(f"  !! '{var_name}' not found"); return src
    open_paren = m.end() - 1
    depth, i, quote, esc = 0, open_paren, None, False
    while i < len(src):
        c = src[i]
        if quote:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == quote: quote = None
        else:
            if c in "\"'": quote = c
            elif c == "(": depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0: break
        i += 1
    segment = src[open_paren + 1 : i]
    args, buf, d, q, e = [], "", 0, None, False
    for c in segment:
        if q:
            buf += c
            if e: e = False
            elif c == "\\": e = True
            elif c == q: q = None
        else:
            if c in "\"'": q = c; buf += c
            elif c == ",":
                if d == 0: args.append(buf); buf = ""
                else: buf += c
            else:
                if c in "([{": d += 1
                elif c in ")]}": d -= 1
                buf += c
    if buf.strip(): args.append(buf)
    kw_idx = next((k for k, a in enumerate(args) if re.match(r"\s*value\s*=", a)), None)
    positional_idx = [k for k, a in enumerate(args) if not re.match(r"\s*\w+\s*=", a)]
    if kw_idx is not None:
        args[kw_idx] = f" value={value_expr}"; how = "kwarg"
    elif var_name in ("batch_size", "save_every_epoch", "total_epoch") and len(positional_idx) >= 3:
        args[positional_idx[2]] = f" {value_expr}"; how = "positional"
    else:
        args.insert(0, f" value={value_expr}"); how = "inserted"
    print(f"  {var_name} <- {value_expr} ({how})")
    return src[: open_paren + 1] + ",".join(args) + src[i:]

print("Applying patches:")
src = set_component_default(src, "model_name", '"jarvis-rvc"')
src = set_component_default(src, "dataset_path", 'r"/kaggle/input/x"')
src = set_component_default(src, "gpu", '"0-1"')
src = set_component_default(src, "batch_size", "8")
src = set_component_default(src, "save_every_epoch", "25")
src = set_component_default(src, "total_epoch", "250")
src = set_component_default(src, "cache_dataset_in_gpu", "True")
src = set_component_default(src, "terms_checkbox", "True")

ast.parse(src)
print("\nast.parse: OK")

# write patched file for direct inspection
def write_patched():
    with open(train_py, "w", encoding="utf-8") as f:
        f.write(src)

write_patched()
print("Patched file written to", train_py)


def get_segment(source: str, var_name: str) -> str:
    """Extract the argument segment of a component call using the same
    paren-matching (string-aware) logic as Cell 2."""
    m = re.search(rf"\b{re.escape(var_name)}\s*=\s*gr\.\w+\(", source)
    if not m:
        return ""
    op = m.end() - 1
    depth, i, quote, esc = 0, op, None, False
    while i < len(source):
        c = source[i]
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
    return source[op + 1 : i]


checks = {
    "model_name value": 'value="jarvis-rvc"' in get_segment(src, "model_name"),
    "dataset_path value": 'value=r"/kaggle/input/x"' in get_segment(src, "dataset_path"),
    "gpu value 0-1": 'value="0-1"' in get_segment(src, "gpu"),
    "batch_size positional": re.search(r"\s*1,\s*64,\s*8,", get_segment(src, "batch_size")) is not None,
    "save_every positional": re.search(r"\s*1,\s*100,\s*25,", get_segment(src, "save_every_epoch")) is not None,
    "total_epoch positional": re.search(r"\s*1,\s*10000,\s*250,", get_segment(src, "total_epoch")) is not None,
    "cache checkbox True": re.search(r"\bvalue\s*=\s*True", get_segment(src, "cache_dataset_in_gpu")) is not None,
    "terms checkbox True": re.search(r"\bvalue\s*=\s*True", get_segment(src, "terms_checkbox")) is not None,
}
fails = [k for k, ok in checks.items() if not ok]
for k, ok in checks.items():
    print(f"  {'PASS' if ok else 'FAIL'}: {k}")
if fails:
    sys.exit(f"FAILED: {fails}")
print("\nALL PATCH CHECKS PASSED against real Applio code")
