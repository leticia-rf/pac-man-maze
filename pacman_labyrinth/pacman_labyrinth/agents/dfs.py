from __future__ import annotations

from .search_agent_base import SearchAgentBase
from ..search.algorithms import SearchResult, reconstruct_path


class DFSAgent(SearchAgentBase):
    algorithm_name = "dfs"

    def search(self, problem) -> SearchResult:
        # fronteira = pilha 
        frontier = problem.lifo_frontier()
        frontier.push(problem.start)

        start_key = problem.start.as_tuple()

        parents = {start_key: (None, None)}

        while frontier:
            cur = frontier.pop() # remove da pilha
            cur_key = cur.as_tuple()

            if problem.is_goal(cur):
                actions, path = reconstruct_path(parents, cur)
                return problem.solution(actions, path, float(len(actions)), True)
            
            for action, nxt, _ in problem.successors(cur):
                nxt_key = nxt.as_tuple()

                if nxt_key not in parents:
                    parents[nxt_key] = (cur_key, action)
                    frontier.push(nxt)

        return problem.failure()