# CorridorKey for Nuke

A Nuke node for **[CorridorKey 2.0](https://github.com/nikopueringer/CorridorKey2.0)**, the AI green/blue screen keyer by Corridor Digital, so you can pull CorridorKey 2.0 keys inside Nuke.

The plugin is free and unofficial. It doesn't include CorridorKey itself: the installer downloads CorridorKey 2.0 and its models from the official sources onto your machine.

> Corridor Digital also sells an official, commercially supported CorridorKey plugin for Nuke and other hosts at [corridorkey.com](https://corridorkey.com).

## Features

- **CorridorKey 2.0 node.** Connect the plate, press **Run CorridorKey**, and the key comes back into the node. The model keys the whole frame range together, which keeps the key stable over time, and runs in the background with a progress bar.
- **ACES and non-ACES.** The plate is converted to the display-referred look the model was trained on, and the result is converted back to your working space (ACEScg or linear). Feeding the model raw ACEScg makes hair noticeably softer, so the node never does that.
- **Hint input.** An optional roto or garbage matte tells the model what to keep, either on the first frame only or on every frame, with a quality control.
- **Outputs** (switch instantly, no re-run): premultiplied FG, straight FG, matte only, or plate + alpha (your original plate pixels with the new alpha).
- **Live matte controls.** Clip black and clip white tighten the matte without a re-run. **key starts at** slides the key in time.
- **Read + Switch.** After each run, the node builds a Read of the keyed EXRs plus an output Switch in your node graph, inside a backdrop with the plate and the CorridorKey node. **Ctrl+Alt+K** rebuilds it for the selected node.
- **Safe caching.** Each node keeps its own cache folder. If two nodes point at the same folder, the node asks before overwriting. Proxy mode can't make it key a low-res plate.
- **How to use** tab on the node explains every control.

## Requirements

| | |
|---|---|
| OS | Windows 10/11 or Linux (CorridorKey 2.0 needs CUDA, so macOS is not supported) |
| GPU | NVIDIA RTX 30-series or newer. At least 4 GB VRAM for up to 1440p, 6 GB for 4K. More VRAM means longer temporal windows. |
| Nuke | Tested with Nuke 17.1. Needs a Nuke with Python 3 and OCIO. |
| Software | [Git](https://git-scm.com), [Python 3.10 – 3.13](https://www.python.org) (a normal Python install, not Nuke's), [ffmpeg](https://ffmpeg.org) on PATH (Windows: `winget install Gyan.FFmpeg`) |
| Disk | About 10 GB for CorridorKey and its models, plus cache space for your shots (EXR) |

## Install

1. Download this repository (green **Code** button > **Download ZIP**) and unzip it, or `git clone` it.
2. Run the installer:
   - **Windows:** double-click `install\install_windows.bat`, or run it from a terminal to choose the install folder:
     ```bat
     install\install_windows.bat --backend D:\CorridorKey2.0
     ```
   - **Linux:**
     ```bash
     ./install/install_linux.sh --backend ~/CorridorKey2.0
     ```
   The installer will:
   1. clone CorridorKey 2.0 into the `--backend` folder (default `~/CorridorKey2.0`)
   2. install CUDA PyTorch and the requirements into a virtual environment there
   3. download about 5 GB of model weights from the official sources
   4. copy the plugin to `~/.nuke/CorridorKey`
   5. add one line to `~/.nuke/init.py`, after backing it up

   Re-running is safe: finished steps are skipped.
3. Restart Nuke. The node is in **Nodes toolbar > CorridorKey > CorridorKey 2.0**, or press Tab and type "CorridorKey".

**Already have CorridorKey 2.0 installed?** Install only the plugin:
```bash
python install/install_backend.py --skip-backend --backend /path/to/CorridorKey2.0
```
Or copy the `CorridorKey` folder into your `.nuke`, add `nuke.pluginAddPath('CorridorKey')` to `init.py`, and pick the folder in Nuke with **Nodes > CorridorKey > Set backend folder...**.

## Using it

1. Connect your green or blue screen plate to the **Plate** input.
2. Set **cache folder** (one per node), or leave it empty for an automatic folder.
3. Set the frame range: type it in, or use **from input** or **in/out** (the in/out points from the Viewer).
4. Press **Run CorridorKey**. When it finishes, the node shows the key, and a Read + Switch appears in the node graph.

### Hint input (optional)
A matte that tells CorridorKey **what to keep**: white = subject, black = remove. Use it when the model keeps light stands, rigs or furniture, or picks the wrong subject. A rough Roto is enough; keep it a little loose rather than tight.
- **first frame only:** the matte only has to be right on the first frame of the range. The model follows the subject from there.
- **every frame:** an animated roto or garbage matte, for the most control.
- **hint quality:** about 0.95 for a clean roto, 0.75 for a rough matte, 0.5 or less for a loose garbage matte.

The hint decides *what* is keyed. It doesn't add edge detail.

### Controls
| Control | What it does | Re-run needed? |
|---|---|---|
| output | premultiplied FG, straight FG, matte only, plate + alpha | no |
| clip black / clip white | alpha below black → 0, above white → 1 | no |
| key starts at | the Nuke frame where the key begins (set automatically) | no |
| despill | despill strength, applied by the model | yes |
| model colour | what the model sees. Leave on **viewer look**. | yes |
| GPU memory / window | auto, or low VRAM if you get "CUDA out of memory" | yes |

## Good to know

- **Not real-time.** CorridorKey 2.0 keys frames together in temporal windows, so it runs as a job. Expect roughly 2 s per 2K frame on an RTX 5070 Ti, plus about 20 s to load the model. 4K is several times slower.
- **Hair detail depends on the shot.** Backlit hair against a clean screen keys very well. Dark hair over a dark or uneven screen comes out softer. That's the model, not the node.
- **Highlights.** The model sees display-referred values, so highlights in its FG output are capped. For HDR highlights, use **plate + alpha**.
- **Copy-pasted nodes** keep the original's cache folder. Run detects this and offers a separate subfolder.
- Logs are saved in each node's cache folder (`corridorkey_log.txt`).

## Troubleshooting

- **"CorridorKey 2.0 backend not found":** run the installer, or use **Nodes > CorridorKey > Set backend folder...**.
- **CUDA out of memory:** close other GPU apps, set **GPU memory** to *low VRAM*, then lower **window** (8, 4, 2).
- **ffmpeg not found:** install ffmpeg and make sure `ffmpeg` runs in a terminal.
- **Key looks out of step with the plate:** press **reset** next to *key starts at*, or **Reload result**.

## Credits and licence

- **CorridorKey 2.0**: model designed and trained by **Zachary Harris** with **Niko Pueringer / Corridor Digital**. https://github.com/nikopueringer/CorridorKey2.0
- CorridorKey builds on C-RADIO (NVIDIA), MoGe (Microsoft) and RVM (Google DeepMind). Each has its own licence; see CorridorKey's [THIRD_PARTY_NOTICES.md](https://github.com/nikopueringer/CorridorKey2.0/blob/main/THIRD_PARTY_NOTICES.md). The installer downloads them from their original publishers.

This plugin builds on CorridorKey, so it is released under the same **[Corridor Key Licence](LICENSE)**, which is CC BY-NC-SA 4.0 plus Corridor Digital's additional terms. In short:
- You can use it, including to process footage for commercial projects, and what you make is yours.
- It must stay free. You can't sell it, charge for access, or offer it as a paid service.
- Organisations with more than US $20M in annual revenue need a CorridorKey plugin seat per user. See [corridorkey.com](https://corridorkey.com).

Read the [LICENSE](LICENSE) for the full terms.
