# Undo/Redo history stack
# ========================

from collections import deque
from copy import deepcopy


class UndoRedoStack:
    """Generic undo/redo stack for any serializable state."""

    def __init__(self, max_size=50):
        self._undo_stack = deque(maxlen=max_size)
        self._redo_stack = deque(maxlen=max_size)

    def push(self, state):
        self._undo_stack.append(deepcopy(state))
        self._redo_stack.clear()

    def undo(self, current_state):
        if not self._undo_stack:
            return None
        self._redo_stack.append(deepcopy(current_state))
        return self._undo_stack.pop()

    def redo(self, current_state):
        if not self._redo_stack:
            return None
        self._undo_stack.append(deepcopy(current_state))
        return self._redo_stack.pop()

    @property
    def can_undo(self):
        return bool(self._undo_stack)

    @property
    def can_redo(self):
        return bool(self._redo_stack)

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()

    @property
    def undo_count(self):
        return len(self._undo_stack)

    @property
    def redo_count(self):
        return len(self._redo_stack)
