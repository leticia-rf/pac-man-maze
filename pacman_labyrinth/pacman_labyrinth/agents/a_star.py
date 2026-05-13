from __future__ import annotations

from .search_agent_base import SearchAgentBase
from ..search.algorithms import SearchResult, reconstruct_path


class AStarAgent(SearchAgentBase):
    algorithm_name = "astar"

    def search(self, problem) -> SearchResult:
        raise NotImplementedError
