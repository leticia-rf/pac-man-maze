from __future__ import annotations

from .search_agent_base import SearchAgentBase
from ..search.algorithms import SearchResult, reconstruct_path


class BFSAgent(SearchAgentBase):
    algorithm_name = "bfs"

    def search(self, problem) -> SearchResult:
        raise NotImplementedError
