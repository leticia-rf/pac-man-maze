from __future__ import annotations

from .search_agent_base import SearchAgentBase
from ..search.algorithms import SearchResult, reconstruct_path


class DijkstraAgent(SearchAgentBase):
    algorithm_name = "dijkstra"

    def search(self, problem) -> SearchResult:
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
