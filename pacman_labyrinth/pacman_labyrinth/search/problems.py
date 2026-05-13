from __future__ import annotations

from dataclasses import dataclass, field

from ..core.actions import ACTION_TO_DELTA, Action
from ..core.models import EXIT, FREE, UNKNOWN, Position
from .algorithms import (
    FIFOFrontier,
    LIFOFrontier,
    PriorityFrontier,
    SearchResult,
    SearchTraceRecorder,
)


@dataclass(slots=True)
class GridPlanningProblem:
    """Classical planning problem over the known maze.

    The algorithm receives the full grid, the initial position, and the goal.
    """

    grid: tuple[tuple[int, ...], ...]
    start: Position
    goal: Position
    allow_unknown: bool = False
    recorder: SearchTraceRecorder | None = field(default=None, repr=False)

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return len(self.grid[0]) if self.grid else 0

    def in_bounds(self, pos: Position) -> bool:
        return 0 <= pos.row < self.rows and 0 <= pos.col < self.cols

    def traversable(self, pos: Position) -> bool:
        cell = self.grid[pos.row][pos.col]
        if cell in (FREE, EXIT):
            return True
        return self.allow_unknown and cell == UNKNOWN

    def is_goal(self, pos: Position) -> bool:
        return pos == self.goal

    def heuristic(self, pos: Position) -> int:
        raise NotImplementedError("heurística não implementada!")

    def successors(self, pos: Position) -> list[tuple[Action, Position, float]]:
        if self.recorder is not None:
            self.recorder.mark_expanded(pos)

        out: list[tuple[Action, Position, float]] = []
        for action, (dr, dc) in ACTION_TO_DELTA.items():
            nxt = Position(pos.row + dr, pos.col + dc)
            if self.in_bounds(nxt) and self.traversable(nxt):
                out.append((action, nxt, 1.0))
        return out

    def _ensure_recorder(self) -> SearchTraceRecorder:
        if self.recorder is None:
            self.recorder = SearchTraceRecorder()
        return self.recorder

    def fifo_frontier(self, items=()) -> FIFOFrontier:
        return FIFOFrontier(items, self._ensure_recorder())

    def lifo_frontier(self, items=()) -> LIFOFrontier:
        return LIFOFrontier(items, self._ensure_recorder())

    def priority_frontier(self) -> PriorityFrontier:
        return PriorityFrontier(self._ensure_recorder())

    def solution(
        self,
        actions: list[Action],
        path: list[Position],
        cost: float,
        found: bool = True,
    ) -> SearchResult:
        if self.recorder is not None and path:
            self.recorder.current = path[-1]
            self.recorder.record()
        trace = list(self.recorder.trace) if self.recorder is not None else []
        expanded = self.recorder.expanded_count() if self.recorder is not None else max(0, len(path) - 1)
        return SearchResult(actions, path, cost, expanded, found, trace)

    def failure(self) -> SearchResult:
        trace = list(self.recorder.trace) if self.recorder is not None else []
        expanded = self.recorder.expanded_count() if self.recorder is not None else 0
        return SearchResult([], [self.start], float("inf"), expanded, False, trace)
