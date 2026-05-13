from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import heapq
import itertools
from typing import Any, Iterable, Iterator

from ..core.actions import Action
from ..core.models import Position


@dataclass(slots=True)
class SearchStep:
    current: Position | None
    frontier: list[Position] = field(default_factory=list)
    expanded: list[Position] = field(default_factory=list)


@dataclass(slots=True)
class SearchResult:
    actions: list[Action]
    path: list[Position]
    cost: float
    expanded: int
    found: bool
    trace: list[SearchStep] = field(default_factory=list)


def reconstruct_path(
    parents: dict[tuple[int, int], tuple[tuple[int, int] | None, Action | None]],
    goal: Position,
) -> tuple[list[Action], list[Position]]:
    """Reconstruct actions and positions from a parent dictionary."""
    actions: list[Action] = []
    path: list[Position] = [goal]
    cur = goal.as_tuple()
    while True:
        parent, action = parents[cur]
        if parent is None:
            break
        assert action is not None
        actions.append(action)
        path.append(Position(*parent))
        cur = parent
    actions.reverse()
    path.reverse()
    return actions, path


def unique_positions(items: Iterable[Any]) -> list[Position]:
    """Return positions in insertion order, removing repeated coordinates. """
    out: list[Position] = []
    seen: set[tuple[int, int]] = set()
    for item in items:
        pos = item[-1] if isinstance(item, (tuple, list)) and item else item
        if not isinstance(pos, Position):
            continue
        key = pos.as_tuple()
        if key in seen:
            continue
        seen.add(key)
        out.append(pos)
    return out


class SearchTraceRecorder:
    """Automatic recorder used by the GUI search animation."""

    def __init__(self) -> None:
        self.current: Position | None = None
        self.expanded_cells: list[Position] = []
        self.expanded_keys: set[tuple[int, int]] = set()
        self.trace: list[SearchStep] = []
        self._frontier: ObservableFrontier | None = None

    def bind_frontier(self, frontier: "ObservableFrontier") -> None:
        self._frontier = frontier
        self.record()

    def mark_expanded(self, pos: Position) -> None:
        self.current = pos
        key = pos.as_tuple()
        if key not in self.expanded_keys:
            self.expanded_keys.add(key)
            self.expanded_cells.append(pos)
        self.record()

    def frontier_changed(self) -> None:
        if self.current is not None:
            self.record()

    def frontier_positions(self) -> list[Position]:
        if self._frontier is None:
            return []
        return self._frontier.snapshot_positions()

    def record(self) -> None:
        self.trace.append(
            SearchStep(
                current=self.current,
                frontier=self.frontier_positions(),
                expanded=self.expanded_cells.copy(),
            )
        )

    def expanded_count(self) -> int:
        return len(self.expanded_cells)


class ObservableFrontier:
    """Base class for frontiers that feed the automatic search animation."""

    def __init__(self, recorder: SearchTraceRecorder | None = None) -> None:
        self.recorder = recorder
        if recorder is not None:
            recorder.bind_frontier(self)

    def _changed(self) -> None:
        if self.recorder is not None:
            self.recorder.frontier_changed()

    def snapshot_positions(self) -> list[Position]:
        raise NotImplementedError

    def __bool__(self) -> bool:
        return len(self) > 0

    def __len__(self) -> int:
        raise NotImplementedError


class FIFOFrontier(ObservableFrontier):
    """Queue frontier for BFS."""

    def __init__(self, items: Iterable[Position] = (), recorder: SearchTraceRecorder | None = None) -> None:
        self._items: deque[Position] = deque(items)
        super().__init__(recorder)

    def push(self, pos: Position) -> None:
        self._items.append(pos)
        self._changed()

    def pop(self) -> Position:
        return self._items.popleft()

    def snapshot_positions(self) -> list[Position]:
        return unique_positions(self._items)

    def __len__(self) -> int:
        return len(self._items)


class LIFOFrontier(ObservableFrontier):
    """Stack frontier for DFS."""

    def __init__(self, items: Iterable[Position] = (), recorder: SearchTraceRecorder | None = None) -> None:
        self._items: list[Position] = list(items)
        super().__init__(recorder)

    def push(self, pos: Position) -> None:
        self._items.append(pos)
        self._changed()

    def pop(self) -> Position:
        return self._items.pop()

    def snapshot_positions(self) -> list[Position]:
        return unique_positions(self._items)

    def __len__(self) -> int:
        return len(self._items)


class PriorityFrontier(ObservableFrontier):
    """Stable priority queue for UCS, Greedy, and A*.

    push(priority, pos) accepts either a number or a tuple of numbers.
    pop() returns (priority_tuple, pos).
    """

    def __init__(self, recorder: SearchTraceRecorder | None = None) -> None:
        self._heap: list[tuple[tuple[float, ...], int, Position]] = []
        self._counter = itertools.count()
        super().__init__(recorder)

    @staticmethod
    def _priority_tuple(priority: float | int | tuple[float | int, ...]) -> tuple[float, ...]:
        if isinstance(priority, tuple):
            return tuple(float(v) for v in priority)
        return (float(priority),)

    def push(self, priority: float | int | tuple[float | int, ...], pos: Position) -> None:
        heapq.heappush(self._heap, (self._priority_tuple(priority), next(self._counter), pos))
        self._changed()

    def pop(self) -> tuple[tuple[float, ...], Position]:
        priority, _idx, pos = heapq.heappop(self._heap)
        return priority, pos

    def snapshot_positions(self) -> list[Position]:
        return unique_positions(self._heap)

    def __len__(self) -> int:
        return len(self._heap)


def failure_result(start: Position, expanded: int, trace: list[SearchStep] | None = None) -> SearchResult:
    return SearchResult([], [start], float("inf"), expanded, False, trace or [])


def dijkstra_search(problem) -> SearchResult:
    frontier = problem.priority_frontier()
    frontier.push(0.0, problem.start)

    start_key = problem.start.as_tuple()
    parents = {start_key: (None, None)}
    dist = {start_key: 0.0}
    expanded_set: set[tuple[int, int]] = set()

    while frontier:
        priority, cur = frontier.pop()
        cost = priority[0]
        cur_key = cur.as_tuple()

        if cost > dist[cur_key]:
            continue
        if cur_key in expanded_set:
            continue

        if problem.is_goal(cur):
            actions, path = reconstruct_path(parents, cur)
            return problem.solution(actions, path, cost, True)

        expanded_set.add(cur_key)
        for action, nxt, step_cost in problem.successors(cur):
            nxt_key = nxt.as_tuple()
            new_cost = cost + step_cost
            if new_cost < dist.get(nxt_key, float("inf")):
                dist[nxt_key] = new_cost
                parents[nxt_key] = (cur_key, action)
                frontier.push(new_cost, nxt)

    return problem.failure()


SEARCH_REGISTRY = {
    "dijkstra": dijkstra_search,
}
