#!/usr/bin/env python3
"""Install CorridorKey 2.0 (the backend) and the CorridorKey Nuke plugin.

What it does:
  1. Clones the official CorridorKey 2.0 repository (pinned to the version this plugin was tested with).
  2. Creates a Python virtual environment in it and installs CUDA PyTorch + its requirements.
  3. Downloads the CorridorKey weights and the three foundation models from their original publishers
     (about 5 GB) using CorridorKey's own scripts/download_weights.py.
  4. Copies the Nuke plugin into your .nuke folder, points it at the backend and adds one line to
     .nuke/init.py.

Nothing from CorridorKey is redistributed by this repository - everything is fetched from the official sources.

Usage (run with Python 3.10 - 3.13, not Nuke's Python):
  python install_backend.py                         # backend in ~/CorridorKey2.0, plugin in ~/.nuke
  python install_backend.py --backend D:/CorridorKey2.0
  python install_backend.py --skip-backend --backend D:/CorridorKey2.0   # plugin only, existing backend
Re-running is safe: finished steps are skipped.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

UPSTREAM = "https://github.com/nikopueringer/CorridorKey2.0.git"
UPSTREAM_REF = "485f5e9ab759ead6138cc990776184b59d6ea971"   # tested with plugin 1.0.0
TORCH = ["torch==2.9.1", "torchvision==0.24.1"]
TORCH_INDEX = "https://download.pytorch.org/whl/cu128"
PLUGIN_SRC = Path(__file__).resolve().parents[1] / "CorridorKey"
INIT_MARK = "# CorridorKey 2.0 for Nuke"


def step(msg):
    print(f"\n=== {msg}", flush=True)


def run(cmd, **kw):
    print("  >", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def venv_python(backend: Path) -> Path:
    return backend / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def checks():
    step("Checking requirements")
    if not ((3, 10) <= sys.version_info[:2] <= (3, 13)):
        sys.exit(f"Python 3.10 - 3.13 is required (this is {sys.version.split()[0]}).")
    if not shutil.which("git"):
        sys.exit("git was not found on PATH. Install Git first: https://git-scm.com")
    if not shutil.which("ffmpeg"):
        print("  WARNING: ffmpeg is not on PATH. CorridorKey needs it. Windows: winget install Gyan.FFmpeg, "
              "Linux: install ffmpeg with your package manager.")
    if not shutil.which("nvidia-smi"):
        print("  WARNING: nvidia-smi not found. CorridorKey needs an NVIDIA RTX GPU (30-series or newer).")
    print(f"  Python {sys.version.split()[0]} OK")


def install_backend(backend: Path, ref: str):
    step(f"CorridorKey 2.0 source -> {backend}")
    if (backend / "infer.py").is_file():
        print("  already present, skipping clone")
    else:
        backend.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", UPSTREAM, backend])
        run(["git", "-C", backend, "checkout", "--quiet", ref])

    py = venv_python(backend)
    step("Python environment")
    if py.is_file():
        print("  venv already present")
    else:
        run([sys.executable, "-m", "venv", backend / "venv"])
    run([py, "-m", "pip", "install", "--upgrade", "pip", "-q"])

    step("PyTorch (CUDA 12.8) and requirements - large download, this can take a while")
    run([py, "-m", "pip", "install", "--no-cache-dir", *TORCH, "--index-url", TORCH_INDEX])
    run([py, "-m", "pip", "install", "--no-cache-dir", "-r", backend / "requirements.txt"])

    step("Model weights (about 5 GB) from the official sources")
    env = dict(os.environ, HF_HOME=str(backend / "_cache" / "hf"), HF_HUB_DISABLE_XET="1")
    run([py, backend / "scripts" / "download_weights.py"], cwd=backend, env=env)

    step("GPU check")
    run([py, "-c", "import torch; print('  torch', torch.__version__, '| CUDA:', torch.cuda.is_available(), "
                   "'|', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no GPU')"])


def install_plugin(backend: Path, nuke_dir: Path):
    step(f"Nuke plugin -> {nuke_dir / 'CorridorKey'}")
    dst = nuke_dir / "CorridorKey"
    dst.mkdir(parents=True, exist_ok=True)
    for f in PLUGIN_SRC.glob("*.py"):
        shutil.copy2(f, dst / f.name)
        print(f"  copied {f.name}")
    cfg_path = dst / "corridorkey_config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.is_file() else {}
    cfg["backend"] = str(backend.resolve()).replace("\\", "/")
    cfg_path.write_text(json.dumps(cfg, indent=1), encoding="utf-8")
    print(f"  backend set to {cfg['backend']}")

    init_py = nuke_dir / "init.py"
    text = init_py.read_text(encoding="utf-8", errors="replace") if init_py.is_file() else ""
    # absolute path: relative pluginAddPath entries are resolved against other plugin folders by some tools
    line = f"nuke.pluginAddPath(r'{dst.resolve().as_posix()}')  {INIT_MARK}"
    if INIT_MARK in text:
        print("  init.py already loads CorridorKey")
    else:
        if init_py.is_file():
            backup = init_py.with_name(f"init.py.bak_{datetime.datetime.now():%Y%m%d_%H%M%S}")
            shutil.copy2(init_py, backup)
            print(f"  backed up init.py -> {backup.name}")
        prefix = "" if (not text or text.endswith("\n")) else "\n"
        header = "" if "import nuke" in text else "import nuke\n"
        with open(init_py, "a", encoding="utf-8") as f:
            f.write(f"{prefix}\n{header}{line}\n")
        print("  added CorridorKey to init.py")


def main():
    ap = argparse.ArgumentParser(description="Install CorridorKey 2.0 and the CorridorKey Nuke plugin.")
    ap.add_argument("--backend", default=str(Path.home() / "CorridorKey2.0"),
                    help="where CorridorKey 2.0 is (or will be) installed - needs ~10 GB (default ~/CorridorKey2.0)")
    ap.add_argument("--nuke-dir", default=str(Path.home() / ".nuke"), help="your .nuke folder (default ~/.nuke)")
    ap.add_argument("--skip-backend", action="store_true", help="only install the Nuke plugin")
    ap.add_argument("--skip-plugin", action="store_true", help="only install the backend")
    ap.add_argument("--ref", default=UPSTREAM_REF, help="CorridorKey 2.0 git commit to use")
    args = ap.parse_args()

    backend = Path(args.backend).expanduser()
    checks()
    if not args.skip_backend:
        install_backend(backend, args.ref)
    elif not (backend / "infer.py").is_file():
        sys.exit(f"--skip-backend given but no CorridorKey 2.0 found at {backend}")
    if not args.skip_plugin:
        install_plugin(backend, Path(args.nuke_dir).expanduser())
    step("Done. Restart Nuke: Nodes toolbar > CorridorKey > CorridorKey 2.0")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(f"\nA step failed (exit {exc.returncode}). Fix the error above and run the installer again - "
                 "finished steps are skipped.")
