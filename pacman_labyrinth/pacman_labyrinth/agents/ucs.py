from __future__ import annotations

from .search_agent_base import SearchAgentBase
from ..search.algorithms import SearchResult, reconstruct_path


class UCSAgent(SearchAgentBase):
    algorithm_name = "ucs"

    def search(self, problem) -> SearchResult:
        # fronteira = fila de prioridade
        frontier = problem.priority_frontier()
        frontier.push(0.0, problem.start) # começa com o nó inicial com custo 0

        start_key = problem.start.as_tuple()
        parents = {start_key: (None, None)}

        # dicionário para armazenar os menores custos acumulados
        dist = {start_key: 0.0}

        while frontier:
            # PriorityFrontier -> pop() returns (priority_tuple, pos) 
            priority_tuple, cur = frontier.pop() 
            cost = priority_tuple[0] # acessa o primeiro elemento da tupla
            cur_key = cur.as_tuple()

            # ignora chaves da fronteira com custo maior do que o já encontrado
            if cost > dist[cur_key]:
                continue

            if problem.is_goal(cur):
                actions, path = reconstruct_path(parents, cur)
                return problem.solution(actions, path, cost, True)

            for action, nxt, step_cost in problem.successors(cur):
                nxt_key = nxt.as_tuple()
                new_cost = cost + step_cost                       # calcula o custo acumulado

                # para um nó não conhecido, retorna infinito
                if new_cost < dist.get(nxt_key, float("inf")):    # se encontrou um caminho melhor,
                    dist[nxt_key] = new_cost                      # atualiza no dicionario
                    parents[nxt_key] = (cur_key, action)
                    frontier.push(new_cost, nxt)

        return problem.failure()