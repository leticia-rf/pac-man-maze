from __future__ import annotations

from .search_agent_base import SearchAgentBase
from ..search.algorithms import SearchResult, reconstruct_path


class AStarAgent(SearchAgentBase):
    algorithm_name = "astar"

    def search(self, problem) -> SearchResult:
        # fronteira = fila de prioridade por f(n) = g(n) + h(n)
        frontier = problem.priority_frontier()
        frontier.push(0.0, problem.start)

        start_key = problem.start.as_tuple()
        parents = {start_key: (None, None)}

        # dicionário com os custos acumulados g(n)
        dist = {start_key: 0.0}
        # conjunto de explorados
        expanded_set: set[tuple[int, int]] = set()

        while frontier:
            _, cur = frontier.pop() 
            cur_key = cur.as_tuple()
            g = dist[cur_key] # custo real acumulado do nó 
            
            # ignora as chaves já expandidas
            if cur_key in expanded_set:
                continue
            
            if problem.is_goal(cur):
                actions, path = reconstruct_path(parents, cur)
                return problem.solution(actions, path, g, True)

            expanded_set.add(cur_key) 
            for action, nxt, step_cost in problem.successors(cur):
                nxt_key = nxt.as_tuple()
                new_g = g + step_cost # novo custo acumulado

                if new_g < dist.get(nxt_key, float("inf")):    
                    dist[nxt_key] = new_g
                    parents[nxt_key] = (cur_key, action)
                    
                    # soma com o valor da heurística para chegar ao objetivo
                    frontier.push(new_g + problem.heuristic(nxt), nxt) 

        return problem.failure()