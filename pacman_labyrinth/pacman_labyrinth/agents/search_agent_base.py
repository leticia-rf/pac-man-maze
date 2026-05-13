from __future__ import annotations

from dataclasses import dataclass

from .base import BaseAgent
from ..core.actions import Action
from ..core.models import Percept, Position
from ..search.algorithms import SearchResult, SearchStep, SearchTraceRecorder
from ..search.problems import GridPlanningProblem


@dataclass(slots=True)
class SearchDebug:
    algorithm: str
    phase: str
    current: tuple[int, int] | None
    frontier_cells: list[tuple[int, int]]
    expanded_cells: list[tuple[int, int]]
    final_path: list[tuple[int, int]]
    frontier_count: int
    expanded: int
    plan_length: int
    path_length: int
    cost: float
    found: bool


def _tuples(positions: list[Position]) -> list[tuple[int, int]]:
    return [pos.as_tuple() for pos in positions]


class SearchAgentBase(BaseAgent):
    """
    Base class for search agents.

    Subclasses only implement search(problem) and return a SearchResult. 
    This base class handles:
    - building the GridPlanningProblem from the current percept;
    - animating frontier/expanded/current nodes;
    - storing the final path;
    - executing the final action sequence one step at a time.
    """

    algorithm_name = "search"

    def __init__(self):
        super().__init__(algorithm=self.algorithm_name)
        self.reset()

    def reset(self) -> None:
        self.result: SearchResult | None = None
        self.plan: list[Action] = []
        self.trace: list[SearchStep] = []
        self.trace_index = 0
        self.trace_stride = 1
        self.phase = "idle"
        self.last_debug = SearchDebug(
            algorithm=self.algorithm_name,
            phase="idle",
            current=None,
            frontier_cells=[],
            expanded_cells=[],
            final_path=[],
            frontier_count=0,
            expanded=0,
            plan_length=0,
            path_length=0,
            cost=0.0,
            found=False,
        )

    def search(self, problem: GridPlanningProblem) -> SearchResult:
        raise NotImplementedError

    def _build_problem(self, percept: Percept) -> GridPlanningProblem:
        return GridPlanningProblem(
            grid=percept.known_grid,
            start=percept.start_position,
            goal=percept.goal_position,
            allow_unknown=False,
            recorder=SearchTraceRecorder(),
        )

    def _run_search_once(self, percept: Percept) -> None:
        if self.result is not None:
            return
        problem = self._build_problem(percept)
        self.result = self.search(problem)
        if not self.result.trace and problem.recorder is not None:
            self.result.trace = list(problem.recorder.trace)
            if self.result.expanded == 0:
                self.result.expanded = problem.recorder.expanded_count()
        self.plan = list(self.result.actions)
        self.trace = list(self.result.trace)
        # Keep long mazes usable: at most about 700 visualization frames.
        self.trace_stride = max(1, len(self.trace) // 700)
        self.trace_index = 0
        self.phase = "search" if self.trace else "path_ready"
        self.last_debug = self._debug_from_result("search_started")

    def _debug_from_step(self, step: SearchStep, phase: str) -> SearchDebug:
        assert self.result is not None
        final_path = _tuples(self.result.path) if phase in {"path_ready", "execute", "done"} and self.result.found else []
        return SearchDebug(
            algorithm=self.algorithm_name,
            phase=phase,
            current=None if step.current is None else step.current.as_tuple(),
            frontier_cells=_tuples(step.frontier),
            expanded_cells=_tuples(step.expanded),
            final_path=final_path,
            frontier_count=len(step.frontier),
            expanded=len(step.expanded),
            plan_length=len(self.plan),
            path_length=max(0, len(self.result.path) - 1),
            cost=self.result.cost,
            found=self.result.found,
        )

    def _debug_from_result(self, phase: str) -> SearchDebug:
        if self.result is None:
            return self.last_debug
        expanded_cells = self.trace[-1].expanded if self.trace else []
        return SearchDebug(
            algorithm=self.algorithm_name,
            phase=phase,
            current=None,
            frontier_cells=[],
            expanded_cells=_tuples(expanded_cells),
            final_path=_tuples(self.result.path) if self.result.found else [],
            frontier_count=0,
            expanded=self.result.expanded,
            plan_length=len(self.plan),
            path_length=max(0, len(self.result.path) - 1),
            cost=self.result.cost,
            found=self.result.found,
        )

    def advance_visualization(self, percept: Percept) -> bool:
        """Advance one search-animation frame.

        Returns True while the GUI should render only the animation and should
        not call env.step(...). 
        Returns False when the final path is ready for physical execution by act(...).
        """
        self._run_search_once(percept)

        if self.phase == "search":
            if not self.trace:
                self.phase = "path_ready"
                self.last_debug = self._debug_from_result("path_ready")
                return True

            idx = min(self.trace_index, len(self.trace) - 1)
            self.last_debug = self._debug_from_step(self.trace[idx], "search")
            self.trace_index += self.trace_stride

            if idx >= len(self.trace) - 1:
                self.phase = "path_ready"
                self.last_debug = self._debug_from_result("path_ready")
            return True

        if self.phase == "path_ready":
            self.phase = "execute"
            self.last_debug = self._debug_from_result("execute")
            return True

        return False

    def act(self, percept: Percept, legal_actions: list[Action]) -> Action:
        self._run_search_once(percept)
        if self.phase in {"idle", "search", "path_ready"}:
            self.phase = "execute"

        self.last_debug = self._debug_from_result("execute")

        if not self.result or not self.result.found:
            self.phase = "done"
            self.last_debug = self._debug_from_result("done")
            return Action.WAIT

        if self.plan:
            action = self.plan.pop(0)
            self.last_debug = self._debug_from_result("execute")
            if action in legal_actions:
                return action
            return Action.WAIT

        self.phase = "done"
        self.last_debug = self._debug_from_result("done")
        return Action.WAIT
