from __future__ import annotations

from .search_agent_base import SearchAgentBase
from ..search.algorithms import SearchResult, reconstruct_path


class GreedyBestFirstAgent(SearchAgentBase):
    algorithm_name = "greedy"

    def search(self, problem) -> SearchResult:
        # fronteira = fila de prioridade por f(n) = h(n)
        frontier = problem.priority_frontier()
        frontier.push(0.0, problem.start)

        start_key = problem.start.as_tuple()
        parents = {start_key: (None, None)}

        while frontier:
            priority_tuple, cur = frontier.pop() 
            cost = priority_tuple[0] 

            cur_key = cur.as_tuple()
            
            if problem.is_goal(cur):
                actions, path = reconstruct_path(parents, cur)
                return problem.solution(actions, path, cost, True)

            for action, nxt, _ in problem.successors(cur):
                nxt_key = nxt.as_tuple()

                if nxt_key not in parents:
                    parents[nxt_key] = (cur_key, action)
                    # usa apenas o valor da heurística para a prioridade na fila
                    frontier.push(problem.heuristic(nxt), nxt)

        return problem.failure()
