from __future__ import annotations

from .search_agent_base import SearchAgentBase
from ..search.algorithms import SearchResult, reconstruct_path


class GreedyBestFirstAgent(SearchAgentBase):
    algorithm_name = "greedy"

    def search(self, problem) -> SearchResult:
        raise NotImplementedError
