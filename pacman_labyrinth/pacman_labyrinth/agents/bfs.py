from __future__ import annotations

from .search_agent_base import SearchAgentBase
from ..search.algorithms import SearchResult, reconstruct_path


class BFSAgent(SearchAgentBase):
    algorithm_name = "bfs"

    def search(self, problem) -> SearchResult:
        # fronteira = fila com nó inicial 
        frontier = problem.fifo_frontier()
        frontier.push(problem.start)

        start_key = problem.start.as_tuple()

        # explorados = vazio
        explored_set: set[tuple[int, int]] = set()

        # dicionário para a reconstrução do caminho
        parents = {start_key: (None, None)}

        frontier_set = {start_key}

        # enquanto fronteira não vazia
        while frontier:
            cur = frontier.pop() # remove da fila
            cur_key = cur.as_tuple()
            frontier_set.remove(cur_key) # e do conjunto

            # se o atual é o objetivo, reconstrói o caminho e retorna a solução
            if problem.is_goal(cur):
                actions, path = reconstruct_path(parents, cur)
                return problem.solution(actions, path, float(len(actions)), True)

            # adiciona a explorados
            explored_set.add(cur_key) 

            # para cada sucessor, adiciona na fronteira 
            for action, nxt, _ in problem.successors(cur):
                nxt_key = nxt.as_tuple()

                # só adiciona se não foi explorado e não está na fronteira
                if nxt_key not in explored_set and nxt_key not in frontier_set:
                    parents[nxt_key] = (cur_key, action)
                    frontier.push(nxt)
                    frontier_set.add(nxt_key)

        return problem.failure()