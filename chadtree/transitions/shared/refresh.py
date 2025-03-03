from pathlib import PurePath
from typing import AbstractSet

from pynvim import Nvim
from pynvim_pp.api import list_wins
from std2.types import Void

from ...fs.ops import ancestors, exists
from ...nvim.markers import markers
from ...settings.types import Settings
from ...state.next import forward
from ...state.types import State
from ..shared.wm import find_current_buffer_path
from ..types import Stage


def refresh(nvim: Nvim, state: State, settings: Settings) -> Stage:
    current = find_current_buffer_path(nvim)
    cwd = state.root.path
    paths = {cwd}
    current_ancestors = ancestors(current) if current else set()
    new_current = current if cwd in current_ancestors else None

    index = {path for path in state.index if exists(path, follow=True)} | paths
    selection = {s for s in state.selection if exists(s, follow=False)}
    parent_paths: AbstractSet[PurePath] = current_ancestors if state.follow else set()
    new_index = index if new_current else index | parent_paths

    window_ids = {w.handle for w in list_wins(nvim)}
    window_order = {
        win_id: None for win_id in state.window_order if win_id in window_ids
    }

    mks = markers(nvim)
    new_state = forward(
        state,
        settings=settings,
        index=new_index,
        selection=selection,
        markers=mks,
        paths=paths,
        current=new_current or Void,
        window_order=window_order,
    )

    return Stage(new_state)
