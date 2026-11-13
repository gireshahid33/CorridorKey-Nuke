"""CorridorKey for Nuke - menu entries (Nodes toolbar > CorridorKey)."""
import nuke


def _selected_ck():
    return [n for n in nuke.selectedNodes() if n.knob("ck_first") is not None]


def _read_switch_from_selected():
    import corridorkey_nuke
    nodes = _selected_ck()
    if not nodes:
        nuke.message("Select a CorridorKey node that has been keyed.")
        return
    for n in nodes:
        corridorkey_nuke.make_read_switch(n)


def _upgrade_selected():
    import corridorkey_nuke
    nodes = _selected_ck()
    if not nodes:
        nuke.message("Select one or more CorridorKey nodes to update.")
        return
    for n in nodes:
        corridorkey_nuke.upgrade(n)
    nuke.message(f"Updated {len(nodes)} CorridorKey node(s).")


try:
    import corridorkey_nuke  # noqa: F401  (checks the module loads)
    _m = nuke.menu("Nodes").addMenu("CorridorKey", icon="Keyer.png")
    _m.addCommand("CorridorKey 2.0", "import corridorkey_nuke; corridorkey_nuke.create()", icon="Keyer.png")
    # Ctrl+Alt+K, Node Graph only (Ctrl+Shift+X is Nuke's Edit > Extract)
    _m.addCommand("Create Read + Switch from selected", _read_switch_from_selected, "^#k", shortcutContext=2)
    _m.addCommand("Update selected CorridorKey nodes", _upgrade_selected)
    _m.addSeparator()
    _m.addCommand("Set backend folder...", "import corridorkey_nuke; corridorkey_nuke.choose_backend()")
except Exception as _exc:  # never break Nuke start-up
    nuke.tprint(f"[CorridorKey] menu not loaded: {_exc}")
