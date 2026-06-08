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

        # dicionário para a reconstrução do caminho
        parents = {start_key: (None, None)}

        # enquanto fronteira não vazia
        while frontier:
            cur = frontier.pop() # remove da fila
            cur_key = cur.as_tuple()

            # se o atual é o objetivo, reconstrói o caminho e retorna a solução
            if problem.is_goal(cur):
                actions, path = reconstruct_path(parents, cur)
                return problem.solution(actions, path, float(len(actions)), True)

            # para cada sucessor, adiciona na fronteira 
            for action, nxt, _ in problem.successors(cur):
                nxt_key = nxt.as_tuple()

                # só adiciona se não está no histórico de pais, ou seja, se não foi explorado
                if nxt_key not in parents:
                    parents[nxt_key] = (cur_key, action)
                    frontier.push(nxt)

        return problem.failure()